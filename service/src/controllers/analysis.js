const path = require("path");

const tracerService = require("../trace");

let record = (req, res) => {
  tracerService.addToTraceLog(req);
  res.sendFile(tracerService.traceLogFile, {
    root: path.join(__dirname, "../"),
  });
};

module.exports = { record };
