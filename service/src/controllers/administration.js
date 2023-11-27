const instrumentationService = require("../instrument");
const tracerService = require("../trace");
const logService = require("../log");
const logger = logService.logger;

let clean = (req, res) => {
  instrumentationService.cleanUp();
  tracerService.cleanUp();
  logger.info("Cleaned up all resources");
  res.send("Cleaned up all resources");
};

module.exports = { clean };
