const fs = require("fs");
const readline = require("readline");
const trace = require("./trace");

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
    let isEmpty = traceGroup.filter((t) => t.pageFile).length == 0;
    if (isEmpty) {
      continue;
    }
    perpareForCodeQLQueries(traceGroup);
  }
}

function perpareForCodeQLQueries(traces) {
  console.log(traces.map((t) => t.pageFile));
  // switch (t.action) {
  //   case trace.ACTION_ENUM.INTERACTION_START:
  //   case trace.ACTION_ENUM.INTERACTION_END:
  //   case trace.ACTION_ENUM.VALUE_INPUT:
  //   case trace.ACTION_ENUM.NAMED_FUNCTION_CALL:
  //   default:
  //     logger.error(
  //       `Action type ${t.action} was not recognized and can not be parsed`
  //     );
  // }
}

module.exports = { analyseTraces };

analyseTraces();
