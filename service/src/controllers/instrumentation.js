const path = require("path");

const instrumentationService = require("../instrument");
const logService = require("../log");
const logger = logService.logger;

let instrument = (req, res) => {
  const name = req.body.name || "no_name.js";
  const content = req.body.source;

  instrumentationService.saveFile(name, content);
  instrumentationService
    .runCommand(instrumentationService.getBabelCommand(name))
    .then(() => {
      logger.info(`instrumented file ${name}`);
      res.sendFile(name, { root: path.join(__dirname, "../instrumented") });
    });
};

module.exports = { instrument };
