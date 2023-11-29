const path = require("path");

const common = require("../common");
const instrumentationService = require("../instrument");
const logService = require("../log");
const logger = logService.logger;

let instrument = (req, res) => {
  const name = req.body.name || "no_name.js";
  const content = req.body.source;

  instrumentationService.saveFile(name, content);
  common.runCommand(instrumentationService.getBabelCommand(name)).then(() => {
    logger.info(`instrumented file ${name}`);
    res.sendFile(name, { root: path.join(__dirname, "../instrumented") });
  });
};

module.exports = { instrument };
