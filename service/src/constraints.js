const fs = require("fs");
const readline = require("readline");
const trace = require("./trace");
const codeql = require("./codeql");

const allTraces = [];
const groupedTraces = [];

// class Action {
//   constructor(actionType, args) {
//     this.actionType = actionType;
//     this.args = args;
//   }

//   getConstraintCandidates() {
//     return [];
//   }
// }

// class ValueInputAction extends Action {
//   constructor(t) {
//     super(trace.ACTION_ENUM.VALUE_INPUT, t.args);
//   }

//   getConstraintCandidates() {
//     return ["value"];
//   }
// }

// class NamedFunctionCallAction extends Action {
//   constructor(t) {
//     super(trace.ACTION_ENUM.NAMED_FUNCTION_CALL, t.args);
//     this.file = t.file;
//     this.location = t.location;
//   }

//   getConstraintCandidates() {
//     return ["named"];
//   }
// }

// class UnNamedFunctionCallAction extends Action {
//   constructor(t) {
//     super(trace.ACTION_ENUM.UNNAMED_FUNCTION_CALL, t.args);
//     this.file = t.file;
//     this.location = t.location;
//   }

//   getConstraintCandidates() {
//     return ["unnamed"];
//   }
// }

// class VariableDeclarationAction extends Action {
//   constructor(t) {
//     super(trace.ACTION_ENUM.VARIABLE_DECLARATION, t.args);
//     this.file = t.file;
//     this.location = t.location;
//   }

//   getConstraintCandidates() {
//     return ["variable decl"];
//   }
// }

// class VariableAssignmentAction extends Action {
//   constructor(t) {
//     super(trace.ACTION_ENUM.VARIABLE_ASSIGNMENT, t.args);
//     this.file = t.file;
//     this.location = t.location;
//   }

//   getConstraintCandidates() {
//     return ["variable ass"];
//   }
// }

// class ConditionStatementAction extends Action {
//   constructor(t) {
//     super(trace.ACTION_ENUM.VARIABLE_ASSIGNMENT, t.args);
//     this.file = t.file;
//     this.location = t.location;
//   }

//   getConstraintCandidates() {
//     return ["condition statement"];
//   }
// }

function jsonEuqals(jsonOne, jsonTwo) {
  return JSON.stringify(jsonOne) === JSON.stringify(jsonTwo);
}

function hasValue(object, value) {
  for (const [key, elem] of Object.entries(object)) {
    if (typeof elem === "string") {
      if (elem === value) {
        return [true, object, key];
      }
    } else if (typeof elem === "object") {
      return hasValue(elem, value);
    }
  }

  return [false, {}, ""];
}

function analyseTraces() {
  const fileStream = fs.createReadStream(trace.traceLogFile);
  const rl = readline.createInterface({
    input: fileStream,
    crlfDelay: Infinity,
  });

  rl.on("line", (line) => {
    if (!line) {
      return;
    }
    allTraces.push(JSON.parse(line));
  });

  rl.on("close", () => {
    console.log("Finished reading the file.");
    allTraces.sort(compareTimestamps);
    let add = false;
    let interactions = [];
    for (const t of allTraces) {
      if (t.action == trace.ACTION_ENUM.INTERACTION_START) {
        add = true;
      }

      if (add) {
        interactions.push(t);
      }

      if (t.action == trace.ACTION_ENUM.INTERACTION_END) {
        add = false;
        groupedTraces.push(interactions);
        interactions = [];
      }
    }

    extractConstraintCandidates();
  });
}

function compareTimestamps(a, b) {
  return a.time - b.time;
}

function extractConstraintCandidates() {
  for (const traceGroup of groupedTraces) {
    const browserTraces = traceGroup.filter((t) => t.pageFile);
    if (browserTraces.length == 0) {
      continue;
    }

    let importantTraces = findMagicValues(traceGroup);
    if (importantTraces.length === 0) {
      return [];
    }

    importantTraces = [
      ...new Set(importantTraces.map((e) => JSON.stringify(e))),
    ].map((e) => JSON.parse(e));

    const sourceDir = perpareForCodeQLQueries(traceGroup);
    const databaseDir = codeql.createDatabase(sourceDir, "db");

    for (const t of importantTraces) {
      codeql.prepareQueries(
        t.location.file,
        t.location.start.line,
        t.expression
      );
      codeql.runQueries(databaseDir, codeql.allQueries);
      codeql.resetQueries();
    }

    fs.rmSync(sourceDir, { recursive: true, force: true });
    fs.rmSync(databaseDir, { recursive: true, force: true });
  }
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

function getExpressionByKey(t, element, key) {
  switch (t.action) {
    case trace.ACTION_ENUM.NAMED_FUNCTION_CALL:
      return key;
    case trace.ACTION_ENUM.CONDITIONAL_EXPRESSION:
    case trace.ACTION_ENUM.CONDITIONAL_STATEMENT:
      return element.name;
    default:
      // TODO
      return null;
  }
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
        tracesWithMagicValue.push({
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

function runCodeQLQueries(traceGroup) {
  for (const trace of traceGroup) {
    if (!trace.pageFile) {
      continue;
    }
  }
}

module.exports = { analyseTraces };

analyseTraces();
