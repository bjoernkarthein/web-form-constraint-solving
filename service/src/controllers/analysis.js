const path = require("path");

const tracerService = require("../trace");
const constraintService = require("../constraints");

let record = (req, res) => {
  tracerService.addToTraceLog(req);
  res.sendFile(tracerService.traceLogFile, {
    root: path.join(__dirname, "../"),
  });
};

let getConstraintCandidates = (req, res) => {
  tracerService.cleanUp();
  res.json({
    candidates: [],
  });
};

module.exports = { getConstraintCandidates, record };
