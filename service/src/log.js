const winston = require("winston");

const combinedLogFile = "../static/combined.log";
const errorLogFile = "../static/error.log";

const logger = winston.createLogger({
  level: "info",
  format: winston.format.json(),
  defaultMeta: { service: "instrumentation-service" },
  transports: [
    new winston.transports.File({
      filename: errorLogFile,
      level: "error",
    }),
    new winston.transports.File({
      filename: combinedLogFile,
      level: "info",
    }),
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.simple()
      ),
      colorize: true,
      level: "info",
    }),
  ],
});

module.exports = { logger };
