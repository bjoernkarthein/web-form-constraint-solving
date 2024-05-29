const path = require("path");

const tracerService = require("../trace");
const constraintService = require("../constraints");

let record = (req, res) => {
  tracerService.addToTraceLog(req);
  res.sendFile(tracerService.traceLogFile, {
    root: path.join(__dirname, "../"),
  });
};

let getConstraintCandidatesForTraces = async (_, res) => {
  const results = await constraintService.analyseTraces();
  tracerService.cleanUp();
  res.json({ candidates: results });
};

module.exports = { getConstraintCandidatesForTraces, record };
