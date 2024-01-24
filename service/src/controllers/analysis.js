const path = require("path");

const tracerService = require("../trace");
const constraintService = require("../constraints");

let record = (req, res) => {
  tracerService.addToTraceLog(req);
  res.sendFile(tracerService.traceLogFile, {
    root: path.join(__dirname, "../"),
  });
};

let getConstraintCandidates = async (req, res) => {
  const results = await constraintService.analyseTraces();
  res.json(results);
};

module.exports = { getConstraintCandidates, record };
