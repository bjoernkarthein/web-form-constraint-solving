const fs = require("fs");

const { logger } = require("./log");

const traceLogFile = "trace.log";
let record = false;

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

function getLogState() {
  return record;
}

function setLogState(action) {
  if (!fs.existsSync(traceLogFile)) {
    fs.writeFileSync(traceLogFile, "");
  }

  let oneMoreTime = false;

  if (action == ACTION_ENUM.INTERACTION_START) {
    record = true;
  } else if (action == ACTION_ENUM.INTERACTION_END) {
    record = false;
    oneMoreTime = true;
  }

  return record || oneMoreTime;
}

function addToTraceLog(req) {
  const traceEntry = new Object();
  traceEntry.action = req.body.action;
  try {
    traceEntry.args = JSON.parse(req.body.args);
  } catch (err) {
    traceEntry.args = req.body.args;
  }
  traceEntry.time = req.body.time;
  traceEntry.file = req.body.file;
  traceEntry.location = req.body.location;
  traceEntry.pageFile = req.body.pageFile;

  try {
    fs.appendFileSync(traceLogFile, `${JSON.stringify(traceEntry)}\n`);
  } catch (err) {
    logger.error(err);
  }
}

function cleanUp() {
  fs.rmSync(traceLogFile, { force: true });
}

module.exports = {
  addToTraceLog,
  cleanUp,
  setLogState,
  getLogState,
  traceLogFile,
  ACTION_ENUM,
};
