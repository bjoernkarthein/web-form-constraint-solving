const path = require("path");

const tracerService = require("../trace");

let record = (req, res) => {
  tracerService.addToTraceLog(req);
  res.sendFile(tracerService.traceLogFile, {
    root: path.join(__dirname, "../"),
  });
};

let getConstraintCandidates = (req, res) => {
  res.json({
    candidates: [],
  });
};

module.exports = { getConstraintCandidates, record };
