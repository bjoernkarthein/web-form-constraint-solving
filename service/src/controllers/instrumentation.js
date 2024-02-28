const path = require("path");

const common = require("../common");
const instrumentationService = require("../instrument");
const logService = require("../log");
const logger = logService.logger;

let instrument = (req, res) => {
  const name = req.body.name || "no_name.js"; // TODO
  const content = req.body.source;

  instrumentationService.saveFile(name, content);
  common.runCommand(instrumentationService.getBabelCommand(name)).then(
    (result) => {
      logger.info(`instrumented file ${name}`);
      res.sendFile(name, { root: path.join(__dirname, "..", "instrumented") });
    },
    (error) => {
      res.sendFile(name, { root: path.join(__dirname, "..", "original") });
    }
  );
};

module.exports = { instrument };
