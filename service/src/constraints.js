const generate = require("@babel/generator").default;
const parser = require("@babel/parser");
const traverse = require("@babel/traverse").default;
const t = require("@babel/types");

const codeql = require("./codeql");
const fs = require("fs");
const instrumentation = require("./instrument");
const { logger } = require("./log");
const trace = require("./trace");

const magicValueToReferenceMap = new Map();
// const magicValueToReferenceMap = new Map([
//   ["l", 1],
//   ["Yy", 2],
//   ["71p", 3],
//   ["aHH}", 4],
//   ["6*`O?", 5],
// ]);

const expressionToFieldMap = new Map();

function hasValue(object, value) {
  for (const elem of Object.values(object)) {
    if (typeof elem === "string") {
      if (elem === value) {
        return [true, object];
      }
    } else if (typeof elem === "object") {
      const [result, object] = hasValue(elem, value);
      if (result) {
        return [result, object];
      }
    }
  }

  return [false, {}];
}

async function analyseTraces(traces) {
  const allTraces = [];
  for (const t of traces) {
    if (!!t) {
      try {
        allTraces.push(JSON.parse(t));
      } catch (e) {
        logger.error("error parsing trace");
        logger.error(e.message);
      }
    }
  }

  const pointsOfInterest = processTraces(allTraces);
  console.log(pointsOfInterest);
  if (pointsOfInterest.length == 0) {
    return [];
  }

  const sourceDir = perpareForCodeQLQueries(allTraces);
  runQueries(pointsOfInterest, sourceDir);
  return extractConstraintCandidates();
}

function processTraces(allTraces) {
  const startTraces = allTraces.filter(
    (t) => t.action == trace.ACTION_ENUM.INTERACTION_START
  );
  const endTraces = allTraces.filter(
    (t) => t.action == trace.ACTION_ENUM.INTERACTION_END
  );

  if (startTraces.length === 0 || endTraces.length === 0) {
    return [];
  }

  const start = startTraces[0].time;
  const end = endTraces[0].time;

  const interactionTraces = allTraces.filter(
    (t) => t.time >= start && t.time <= end
  );
  interactionTraces.sort(compareTimestamps);

  const browserTraces = interactionTraces.filter((t) => t.pageFile);
  if (browserTraces.length > 0) {
    // TODO: does this always work and finds the first value of any other form field in the current traces?
    outer: for (const magicValue of magicValueToReferenceMap.keys()) {
      for (const trace of browserTraces) {
        const [included, object] = hasValue(trace, magicValue);
        if (included) {
          const expression = object.expression;
          expressionToFieldMap.set(
            expression,
            JSON.stringify({
              references: Array.from(
                magicValueToReferenceMap.get(magicValue)
              ).map((ref) => JSON.parse(ref)),
              generalLocation: trace.location,
            })
          );
          // TODO: Is it a good idea to keep going and have possibly multiple results? Can I somehow check if all magic values of another input are there?
          // break outer;
        }
      }
    }
  }

  const interactionStart = interactionTraces[0];
  for (const value of interactionStart.args.values) {
    addReferenceForMagicValue(value, interactionStart.args.spec.reference);
  }

  // If there are no functions called in the browser we can return
  if (browserTraces.length === 0) {
    return [];
  }

  // If the magic values are not included in the traces we can also return
  let importantTraces = findMagicValues(interactionTraces);
  if (importantTraces.length === 0) {
    return [];
  }

  return [...new Set(importantTraces.map((e) => JSON.stringify(e)))].map((e) =>
    JSON.parse(e)
  );
}

function compareTimestamps(a, b) {
  return a.time - b.time;
}

function findMagicValues(traceGroup) {
  const magicValues = traceGroup[0].args.values;
  const traces = traceGroup.filter((t) => t.pageFile);
  let tracesWithMagicValues = [];
  let found = true;
  for (const value of magicValues) {
    const tracesWithMagicValue = [];
    // Find first occurence of variable that contains the magic values in every execution
    for (const t of traces) {
      const [hasMagicValue, element] = hasValue(t, value);
      if (hasMagicValue) {
        tracesWithMagicValue.push({
          expression: element.expression,
          location: t.location,
        });
      }
    }

    tracesWithMagicValues = tracesWithMagicValues.concat(tracesWithMagicValue);
    found = found && tracesWithMagicValue.length > 0;
  }

  if (found) {
    return tracesWithMagicValues;
  } else {
    return [];
  }
}

function addReferenceForMagicValue(magicValue, reference) {
  if (!magicValueToReferenceMap.get(magicValue)) {
    magicValueToReferenceMap.set(magicValue, new Set());
  }
  magicValueToReferenceMap.get(magicValue).add(JSON.stringify(reference));
}

function runQueries(pointsOfInterest, sourceDir) {
  // TODO: Only rebuild database if the file set changed since last build
  codeql.createDatabase(sourceDir, "db");

  for (const point of pointsOfInterest) {
    codeql.prepareQueries(
      point.location.file,
      point.location.start.line,
      point.expression
    );
    codeql.runQueries(codeql.allQueries);
    codeql.resetQueries();
  }

  fs.rmSync(sourceDir, { recursive: true, force: true });
  fs.rmSync(codeql.databaseDirectory, { recursive: true, force: true });
}

function perpareForCodeQLQueries(traces) {
  if (!fs.existsSync("source")) {
    fs.mkdirSync("source");
  }

  let allFiles = traces.filter((t) => t.file).map((t) => t.file);
  allFiles = new Set(allFiles);

  for (const file of allFiles) {
    const elements = file.split("/");
    const fileName = elements[elements.length - 1];
    fs.copyFileSync(file, `source/${fileName}`);
  }

  return "source";
}

function extractConstraintCandidates(
  originalDir = instrumentation.originalDir
) {
  const results = codeql.readResults();
  const codeLocations = results.map((res) => {
    csv = JSON.parse(res);
    return {
      type: csv[0],
      location: buildLocationFromResult(csv.slice(3, csv.length)),
    };
  });

  let allCandidates = [];

  for (const codeLoc of codeLocations) {
    const slices = [];
    for (const loc of codeLoc.location) {
      const slice = getCodeSliceFromFileByLocation(
        loc.file,
        loc.startPos,
        loc.endPos,
        originalDir
      );
      slices.push(slice);
    }

    const candidates = buildConstraintCandidates(codeLoc.type, slices);
    allCandidates = allCandidates.concat(candidates);
  }

  return allCandidates;
  // fs.rmSync(codeql.resultDirectory, { recursive: true, force: true });
}

function buildLocationFromResult(locationData) {
  if (/\[\[([^\]]+)\|([^\]]+)\]\]/g.test(locationData[0])) {
    return buildLocationsFromString(locationData[0]);
  } else {
    return {
      file: locationData[1],
      startPos: { line: Number(locationData[2]), col: Number(locationData[3]) },
      endPos: { line: Number(locationData[4]), col: Number(locationData[5]) },
    };
  }
}

function buildLocationsFromString(value) {
  result = [];
  const locationRegExp = /\[\[([^\]]+)\|([^\]]+)\]\]/g;
  const matches = [...value.matchAll(locationRegExp)];
  for (const match of matches) {
    let sourceLoc = match[2];
    sourceLoc = sourceLoc.substring(1, sourceLoc.length - 1);
    sourceLoc = sourceLoc.split("//");
    sourceLoc = sourceLoc[sourceLoc.length - 1];
    const [file, startLine, startCol, endLine, endCol] = sourceLoc.split(":");
    result.push({
      file,
      startPos: { line: startLine, col: startCol },
      endPos: { line: endLine, col: endCol },
    });
  }
  return result;
}

function getCodeSliceFromFileByLocation(
  file,
  startPos,
  endPos,
  dir = instrumentation.originalDir
) {
  let lines = fs.readFileSync(`${dir}${file}`, "utf-8").split("\r\n");
  lines = lines.slice(startPos.line - 1, endPos.line);
  lines[0] = lines[0].substring(startPos.col - 1);
  lines[lines.length - 1] = lines[lines.length - 1].substring(
    0,
    startPos.line === endPos.line
      ? endPos.col - startPos.col + 1
      : endPos.col + 1
  );
  lines = lines.join("\n");
  return lines;
}

function buildConstraintCandidates(type, slices) {
  if (slices.length < 2) {
    return [];
  }

  switch (type) {
    case codeql.queryTypes.COMPARISON_TO_A_LITERAL:
      return handleLiteralComparison(slices[0], slices[1]);
    case codeql.queryTypes.COMPARISON_TO_ANOTHER_VARIABLE:
      return handleVariableComparison(slices[0], slices[1]);
    case codeql.queryTypes.REGEX_TEST:
      return handleRegexTest(slices[1]);
    default:
      return [];
  }
}

function parseSliceToAst(slice) {
  let ast = undefined;
  try {
    ast = parser.parse(slice);
  } catch (e) {
    logger.error("error while converting slice '" + slice + "' to tree");
    logger.error(e.message);
  }

  return ast;
}

function handleRegexTest(pattern) {
  return [{ type: "PatternTest", pattern: pattern }];
}

function handleLiteralComparison(compSlice, literal) {
  const ast = parseSliceToAst(compSlice);
  if (!ast) {
    return [];
  }

  const candidates = [];
  let result = { type: "LitComp", operator: "", otherValue: literal };

  traverse(ast, {
    BinaryExpression: function (path) {
      result.operator = path.node.operator;
      candidates.push(result);
    },
  });

  return candidates;
}

function handleVariableComparison(compSlice, comparedValue) {
  const ast = parseSliceToAst(compSlice);
  if (!ast) {
    return [];
  }

  const candidates = [];

  let otherValue = { type: "", value: "" };
  let result = { type: "VarComp", operator: "", otherValue };

  traverse(ast, {
    BinaryExpression: function (path) {
      result.operator = path.node.operator;

      const possibleReferenceField = expressionToFieldMap.get(comparedValue);
      if (!!possibleReferenceField) {
        otherValue.type = "reference";
        otherValue.value = JSON.parse(possibleReferenceField).references[0];
      } else {
        otherValue.type = "unknown variable";
        otherValue.value = comparedValue;
      }

      candidates.push(result);
    },
  });

  return candidates;
}

function cleanUp() {
  expressionToFieldMap.clear();
  magicValueToReferenceMap.clear();
}

module.exports = {
  analyseTraces,
  cleanUp,
  hasValue,
  extractConstraintCandidates,
};
