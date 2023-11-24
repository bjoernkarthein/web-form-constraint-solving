const winston = require("winston");

const serverLogFile = "../static/server-log.log";
const logger = winston.createLogger({
  level: "info",
  format: winston.format.json(),
  defaultMeta: { service: "instrumentation-service" },
  transports: [new winston.transports.File({ filename: serverLogFile })],
});

module.exports = { logger };
