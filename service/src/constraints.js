const generate = require("@babel/generator").default;
const parser = require("@babel/parser");
const traverse = require("@babel/traverse").default;

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
  for (const [key, elem] of Object.entries(object)) {
    if (typeof elem === "string") {
      if (elem === value) {
        return [true, object, key];
      }
    } else if (typeof elem === "object") {
      const [result, object, key] = hasValue(elem, value);
      if (result) {
        return [result, object, key];
      }
    }
  }

  return [false, {}, ""];
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
        // TODO
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
  const magicValueExpressions = pointsOfInterest.map((p) => p.expression);
  return extractConstraintCandidates(magicValueExpressions);
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
        const [included, object, key] = hasValue(trace, magicValue);
        if (included) {
          const expression = getExpressionByKey(trace, object, key);
          expressionToFieldMap.set(
            expression,
            JSON.stringify({
              references: Array.from(
                magicValueToReferenceMap.get(magicValue)
              ).map((ref) => JSON.parse(ref)),
              generalLocation: trace.location,
            })
          );
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
      const [hasMagicValue, element, key] = hasValue(t, value);
      if (hasMagicValue) {
        // console.log("here");
        // console.log(t);
        // console.log(element);
        // console.log(key);
        // console.log(getExpressionByKey(t, element, key));
        tracesWithMagicValue.push({
          // TODO: Would be nicer if this was not needed somehow
          expression: getExpressionByKey(t, element, key),
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

// TODO: Would be nicer if there was a universal way to get the right data for all types to only leave codeql queries and babel plugins as extension
function getExpressionByKey(t, element, key) {
  switch (t.action) {
    case trace.ACTION_ENUM.NAMED_FUNCTION_CALL:
      return key;
    case trace.ACTION_ENUM.CONDITIONAL_EXPRESSION:
    case trace.ACTION_ENUM.CONDITIONAL_STATEMENT:
      return element.name;
    case trace.ACTION_ENUM.VARIABLE_ASSIGNMENT:
    case trace.ACTION_ENUM.VARIABLE_DECLARATION:
      // return element.expression;
      return t.args.expression;
    default:
      // TODO
      return null;
  }
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

function extractConstraintCandidates(magicValueExpressions) {
  const results = codeql.readResults();
  const codeLocations = results.map((res) => {
    csv = JSON.parse(res);
    return {
      type: csv[0],
      location: buildLocationFromResult(csv.slice(4, csv.length)),
    };
  });

  let allCandidates = [];
  for (const codeLoc of codeLocations) {
    slice = getCodeSliceFromFileByLocation(
      codeLoc.location.file,
      codeLoc.location.startPos,
      codeLoc.location.endPos
    );

    const candidates = buildConstraintCandidates(
      codeLoc.type,
      slice,
      magicValueExpressions
    );
    allCandidates = allCandidates.concat(candidates);
  }

  return allCandidates;
  // fs.rmSync(codeql.resultDirectory, { recursive: true, force: true });
}

function buildLocationFromResult(locationData) {
  return {
    file: locationData[0],
    startPos: { line: Number(locationData[1]), col: Number(locationData[2]) },
    endPos: { line: Number(locationData[3]), col: Number(locationData[4]) },
  };
}

function getCodeSliceFromFileByLocation(file, startPos, endPos) {
  let lines = fs
    .readFileSync(`${instrumentation.originalDir}/${file}`, "utf-8")
    .split("\r\n");
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

function buildConstraintCandidates(type, slice, magicValueExpressions) {
  try {
    ast = parser.parse(slice);
  } catch (e) {
    logger.error("error while converting slice '" + slice + "' to tree");
    logger.error(e.message);
    return [];
  }

  switch (type) {
    case codeql.queryTypes.COMPARISON_TO_ANOTHER_VARIABLE:
      return handleVariableComparison(ast, magicValueExpressions);
    default:
      return [];
  }
}

function handleVariableComparison(ast, magicValueExpressions) {
  const candidates = [];

  let otherValue = { type: "", value: "" };
  let result = { type: "VarComp", operator: "", otherValue };

  traverse(ast, {
    BinaryExpression: function (path) {
      const left = generate(path.node.left).code;
      const op = path.node.operator;
      const right = generate(path.node.right).code;

      result.operator = op;
      let comparedValue = "";

      if (
        magicValueExpressions.includes(left) &&
        !magicValueExpressions.includes(right)
      ) {
        comparedValue = right;
      } else if (
        !magicValueExpressions.includes(left) &&
        magicValueExpressions.includes(right)
      ) {
        comparedValue = left;
      } else if (
        !magicValueExpressions.includes(left) &&
        !magicValueExpressions.includes(right)
      ) {
        // TODO
      } else {
        // TODO
      }

      const possibleReferenceField = expressionToFieldMap.get(comparedValue);
      if (!!possibleReferenceField) {
        otherValue.type = "reference";
        otherValue.value = JSON.parse(possibleReferenceField);
      } else {
        otherValue.type = "unknown variable";
        otherValue.value = comparedValue;
      }

      candidates.push(result);
    },
  });

  return candidates;
}

// function buildLocationsFromString(value) {
//   result = [];
//   const locationRegExp = /\[\[([^\]]+)\|([^\]]+)\]\]/g;
//   const matches = [...value.matchAll(locationRegExp)];
//   for (const match of matches) {
//     let sourceLoc = match[2];
//     sourceLoc = sourceLoc.substring(1, sourceLoc.length - 1);
//     sourceLoc = sourceLoc.split("/");
//     sourceLoc = sourceLoc[sourceLoc.length - 1];
//     const [file, startLine, startCol, endLine, endCol] = sourceLoc.split(":");
//     result.push({
//       file,
//       startPos: { line: startLine, col: startCol },
//       endPos: { line: endLine, col: endCol },
//     });
//   }
//   return result;
// }

function cleanUp() {
  expressionToFieldMap.clear();
  magicValueToReferenceMap.clear();
}

module.exports = { analyseTraces, cleanUp, hasValue };

const data = fs.readFileSync("./trace.log", "utf-8");
const traces = data.split("\n");
analyseTraces(traces);
