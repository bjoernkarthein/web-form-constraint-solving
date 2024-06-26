const winston = require("winston");

const combinedLogFile = "../static/combined.log";
const errorLogFile = "../static/error.log";

const logger = winston.createLogger({
  format: winston.format.json(),
  defaultMeta: { service: "instrumentation-service" },
  transports: [
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
