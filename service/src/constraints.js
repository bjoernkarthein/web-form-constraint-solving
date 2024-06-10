const parser = require("@babel/parser");
const traverse = require("@babel/traverse").default;

const codeql = require("./codeql");
const fs = require("fs");
const instrumentation = require("./instrument");
const { logger } = require("./log");
const trace = require("./trace");
const {
  getStat,
  saveStat,
  getCurrentStats,
} = require("../evaluation/evaluation");

let currentInputName = "";
const magicValueToReferenceMap = new Map();
const expressionToFieldMap = new Map();

function hasValue(object, value) {
  if (!!object) {
    for (const [name, propertyValue] of Object.entries(object)) {
      if (typeof propertyValue === "string") {
        if (name === "value" && propertyValue === value) {
          return [true, object];
        }
      } else if (typeof propertyValue === "object") {
        const [result, object] = hasValue(propertyValue, value);
        if (result) {
          return [result, object];
        }
      }
    }
  }

  return [false, {}];
}

async function analyseTraces() {
  const allTraces = [];
  const traces = fs
    .readFileSync(trace.traceLogFile, { encoding: "utf-8" })
    .split(/\r\n|[\n\r\u2028\u2029]/);
  for (let i = 0; i < traces.length; i++) {
    if (!!traces[i]) {
      try {
        allTraces.push(JSON.parse(traces[i]));
      } catch (e) {
        logger.error(`error parsing trace ${i}`);
        logger.error(e.message);
      }
    }
  }

  const pointsOfInterest = processTraces(allTraces);
  console.log(currentInputName);
  console.log(pointsOfInterest);
  const points = getStat("points_of_interest");
  points[currentInputName] = pointsOfInterest;
  saveStat("points_of_interest", points);
  if (pointsOfInterest.length == 0) {
    return [];
  }

  const sourceDir = perpareForCodeQLQueries(allTraces);
  runQueries(pointsOfInterest, sourceDir);
  return getConstraintCandidates();
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
  currentInputName =
    startTraces[0].args.spec.name || startTraces[0].args.spec.constraints.name;

  const interactionTraces = allTraces.filter(
    (t) => t.time >= start && t.time <= end
  );

  const browserTraces = interactionTraces.filter((t) => t.pageFile);
  if (browserTraces.length > 0) {
    // TODO: does this always work and finds the first value of any other form field in the current traces?
    outer: for (const magicValue of magicValueToReferenceMap.keys()) {
      for (const trace of browserTraces) {
        const [included, object] = hasValue(trace, magicValue);
        if (included) {
          const expression = object.expression;
          try {
            expressionToFieldMap.set(
              expression,
              JSON.stringify({
                references: Array.from(
                  magicValueToReferenceMap.get(magicValue)
                ).map((ref) => JSON.parse(ref)),
                generalLocation: trace.location,
              })
            );
          } catch (e) {
            // Do nothing
          }
          // TODO: Is it a good idea to keep going and have possibly multiple results? Can I somehow check if all magic values of another input are there?
          // break outer;
        }
      }
    }
  }

  const interactionStart = interactionTraces[0];

  if (!!interactionStart.args.spec.options) {
    for (const option of interactionStart.args.spec.options) {
      addReferenceForMagicValue(option.value, option.reference);
    }
  } else {
    for (const value of interactionStart.args.values) {
      addReferenceForMagicValue(value, interactionStart.args.spec.reference);
    }
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
          line: element.line || t.location.start.line,
          file: t.location.file,
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
    codeql.prepareQueries(point.file, point.line, point.expression);
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

  let allFiles = traces
    .filter((t) => !!t.location?.file)
    .map((t) => t.location.file);
  const uniqueFiles = new Set(allFiles);
  saveStat("js_files_analyzed", [
    ...new Set([...getStat("js_files_analyzed"), ...uniqueFiles]),
  ]);

  for (const fileName of uniqueFiles) {
    fs.copyFileSync(`original/${fileName}`, `source/${fileName}`);
  }

  return "source";
}

function getConstraintCandidates(originalDir = instrumentation.originalDir) {
  const pathCandidates = getPathConstraintCandidates(originalDir);
  const otherCandidates = getOtherConstraintCandidates(originalDir);
  const allCandidates = pathCandidates.concat(otherCandidates);

  fs.rmSync(codeql.resultDirectory, { recursive: true, force: true });
  const candidates = getStat("constraint_candidates");
  candidates[currentInputName] = allCandidates;
  saveStat("constraint_candidates", candidates);

  console.log(allCandidates);
  return allCandidates;
}

function getOtherConstraintCandidates(
  originalDir = instrumentation.originalDir
) {
  const results = codeql.readCSVResults();
  const codeLocations = results.map((res) => {
    csv = JSON.parse(res);
    return {
      type: csv[0],
      location: buildLocationsFromString(csv[3]),
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
}

function getPathConstraintCandidates(
  originalDir = instrumentation.originalDir
) {
  const candidates = [];
  const results = codeql.readPathResults();

  for (const res of results) {
    const edges = res.edges.tuples.map((e) => [e[1], e[0]]); // reverse edges to traverse backwards
    const selects = res["#select"].tuples;

    for (const s of selects) {
      const sourceId = s[1].id;
      const sinkId = s[2].id;

      let currentNodeId = sinkId;
      let interestingEdges = [];
      let path = [];
      while (currentNodeId !== sourceId) {
        interestingEdges = edges.filter((e) => e[0].id === currentNodeId);

        if (interestingEdges.length == 0) {
          console.log("edges are empty");
          return [];
        }

        let index = 0;
        if (interestingEdges.length > 1) {
          // TODO: Somehow determine which edge is the right one. Could check all in depth first search with backtracking
          console.log("more than one edge to choose from");
          index = 1;
        }

        path.push(interestingEdges[index][0]);
        currentNodeId = interestingEdges[index][1].id;
      }

      const expressions = path.map((n) =>
        getSliceFromCodeQLResult(n, originalDir)
      );
      const sourceExpression = getSliceFromCodeQLResult(s[1], originalDir);
      let res = combineExpressions(expressions);
      res = res.replace(
        sourceExpression,
        "<FIELD-VALUE>"
        // `<FIELD-VALUE> (${sourceExpression})`
      );
      candidates.push({ type: "Expression", expression: res });
    }
  }
  return candidates;
}

function combineExpressions(expressions) {
  let result = expressions[0];

  for (let i = 1; i < expressions.length; i++) {
    const currentExpression = expressions[i];

    const assignmentIndex = currentExpression.indexOf("=");
    if (assignmentIndex !== -1) {
      const lhs = currentExpression.substring(0, assignmentIndex).trim();
      const rhs = currentExpression.substring(assignmentIndex + 1).trim();

      const regex = new RegExp(`\\b${lhs}\\b`, "g");
      result = result.replace(regex, rhs);
    }
  }

  return result;
}

function getSliceFromCodeQLResult(
  codeQLResult,
  originalDir = instrumentation.originalDir
) {
  const loc = getLocationFromCodeQLResult(codeQLResult);
  return getCodeSliceFromFileByLocation(
    loc.file,
    loc.startPos,
    loc.endPos,
    originalDir
  );
}

function getLocationFromCodeQLResult(codeQLResult) {
  const fileName = codeQLResult.url.uri.replace(/^.*[\\/]/, "");
  return {
    file: `/${fileName}`,
    startPos: {
      line: codeQLResult.url.startLine,
      col: codeQLResult.url.startColumn,
    },
    endPos: {
      line: codeQLResult.url.endLine,
      col: codeQLResult.url.endColumn,
    },
  };
}

function buildLocationsFromString(value) {
  result = [];
  const matches = [...value.matchAll(codeql.resultLocationPattern)];
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
  let lines = fs
    .readFileSync(`${dir}${file}`, "utf-8")
    .split(/\r\n|[\n\r\u2028\u2029]/);
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
    case codeql.queryTypes.COMPARISON_TO_LITERAL_LENGTH:
      return handleLiteralComparison(slices[0], slices[1], true);
    case codeql.queryTypes.REGEX_TEST:
    case codeql.queryTypes.STRING_MATCH:
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

function handleLiteralComparison(compSlice, literal, length = false) {
  const ast = parseSliceToAst(compSlice);
  if (!ast) {
    return [];
  }

  const candidates = [];
  let result = {
    type: length ? "LiteralLengthComp" : "LiteralComp",
    operator: "",
    otherValue: literal,
  };

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
        otherValue.value = JSON.parse(possibleReferenceField).references[0]; // TODO: what if multiple fields are assigned to the same expression?
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
};
