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
  includesValue = false;
  for (const [_, elem] of Object.entries(object)) {
    if (typeof elem === "string") {
      includesValue = includesValue || elem === value;
    } else if (typeof elem === "object") {
      includesValue = includesValue || hasValue(elem, value);
    }
  }

  return includesValue;
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

    const interestingLocations = [
      ...new Set(
        findMagicValues(traceGroup).map((t) => JSON.stringify(t.location))
      ),
    ].map((t) => JSON.parse(t));
    console.log(interestingLocations);

    if (interestingLocations.length === 0) {
      return [];
    }

    const sourceDir = perpareForCodeQLQueries(traceGroup);
    const databaseDir = codeql.createDatabase(sourceDir, "db");
    for (const location of interestingLocations) {
      codeql.prepareQueries(location.file, location.start.line);
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

function findMagicValues(traceGroup) {
  const magicValues = traceGroup[0].args.values;
  // let found = true;
  let tracesWithMagicValues = [];
  const traces = traceGroup.filter((t) => t.pageFile);
  for (const value of magicValues) {
    const tracesWithMagicValue = traces.filter((t) => hasValue(t, value));
    tracesWithMagicValues = tracesWithMagicValues.concat(tracesWithMagicValue);
    // found = found && tracesWithMagicValue.length > 0;
  }
  return tracesWithMagicValues;
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
