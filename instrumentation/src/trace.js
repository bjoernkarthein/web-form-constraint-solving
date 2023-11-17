const fs = require("fs");

const traceLogFile = "trace.log";
const ACTION_ENUM = {
  VALUE_INPUT: "VALUE_INPUT",
};

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

module.exports = { addToTraceLog, traceLogFile };
