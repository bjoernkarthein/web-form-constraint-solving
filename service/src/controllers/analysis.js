const path = require("path");

const tracerService = require("../trace");
const constraintService = require("../constraints");

let record = (req, res) => {
  tracerService.addToTraceLog(req);
  res.sendFile(tracerService.traceLogFile, {
    root: path.join(__dirname, "../"),
  });
};

let getConstraintCandidatesForTraces = async (req, res) => {
  tracerService.cleanUp();
  const results = await constraintService.analyseTraces(req.body.traces);
  res.json({ candidates: results });
};

module.exports = { getConstraintCandidatesForTraces, record };
