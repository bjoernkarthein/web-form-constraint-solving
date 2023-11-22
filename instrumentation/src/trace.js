const fs = require("fs");

const traceLogFile = "trace.log";
const record = false;

const ACTION_ENUM = {
  START_TRACE_RECORDING: "START_TRACE_RECORDING",
  STROP_TRACE_RECORDING: "STOP_TRACE_RECORDING",
  VALUE_INPUT: "VALUE_INPUT",
};

function checkLogState(action) {
  if (!fs.existsSync(traceLogFile)) {
    fs.writeFileSync(traceLogFile, "");
  }

  if (action == ACTION_ENUM.START_TRACE_RECORDING) {
    record = true;
  } else if (action == ACTION_ENUM.STROP_TRACE_RECORDING) {
    record = false;
  }

  return record;
}

function addToTraceLog(req) {
  const traceEntry = new Object();
  traceEntry.action = req.body.action;
  traceEntry.args = req.body.args;
  traceEntry.time = req.body.time;
  traceEntry.file = req.body.file;
  traceEntry.location = req.body.location;
  traceEntry.pageFile = req.body.pageFile;

  data = JSON.stringify(traceEntry);
  try {
    fs.appendFileSync(traceLogFile, `${data}\n`);
    console.log(`recorded trace: ${data}`);
  } catch (err) {
    console.error(err);
  }
}

function cleanUp() {
  fs.rmSync(traceLogFile, { force: true });
}

module.exports = { addToTraceLog, cleanUp, checkLogState, traceLogFile };
