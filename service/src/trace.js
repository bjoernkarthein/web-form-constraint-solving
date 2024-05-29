const fs = require("fs");

const { logger } = require("./log");

const traceLogFile = "trace.log";

const ACTION_ENUM = {
  INTERACTION_START: "INTERACTION_START",
  INTERACTION_END: "INTERACTION_END",
  VALUE_INPUT: "VALUE_INPUT",
  NAMED_FUNCTION_CALL: "NAMED_FUNCTION_CALL",
  VARIABLE_ASSIGNMENT: "VARIABLE_ASSIGNMENT",
  VARIABLE_DECLARATION: "VARIABLE_DECLARATION",
  CONDITIONAL_EXPRESSION: "CONDITIONAL_EXPRESSION",
  CONDITIONAL_STATEMENT: "CONDITIONAL_STATEMENT",
  UNNAMED_FUNCTION_CALL: "UNNAMED_FUNCTION_CALL",
};

function addToTraceLog(req) {
  for (const trace of req.body) {
    try {
      fs.appendFileSync(traceLogFile, `${trace}\n`);
    } catch (err) {
      logger.error(err);
    }
  }
}

function cleanUp() {
  fs.writeFileSync(traceLogFile, "");
}

module.exports = {
  addToTraceLog,
  cleanUp,
  traceLogFile,
  ACTION_ENUM,
};
