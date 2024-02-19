const winston = require("winston");

const combinedLogFile = "../static/combined.log";
const errorLogFile = "../static/error.log";

const logger = winston.createLogger({
  format: winston.format.json(),
  defaultMeta: { service: "instrumentation-service" },
  transports: [
    // For production
    // new winston.transports.File({
    //   filename: errorLogFile,
    //   level: "error",
    // }),
    // new winston.transports.File({
    //   filename: combinedLogFile,
    //   level: "info",
    // }),
    // For debugging the logs can be transported to the console
    // This only works if the console is kept open
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.simple()
      ),
      colorize: true,
      level: "debug",
    }),
    new winston.transports.Http({
      port: 4000,
      path: "/admin/log",
      level: "info",
    }),
  ],
});

module.exports = { logger };
