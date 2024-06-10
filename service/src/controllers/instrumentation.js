const fs = require("fs");
const path = require("path");
const { performance } = require("perf_hooks");

const common = require("../common");
const instrumentationService = require("../instrument");
const { logger } = require("../log");
const { getStat, saveStat } = require("../../evaluation/evaluation");

let instrument = (req, res) => {
  const name = req.body.name || "no_name.js"; // TODO: is it possible for a file to have no name?

  // Check if the file already exists
  if (fs.existsSync(`${instrumentationService.instrumentedDir}/${name}`)) {
    logger.info(`file ${name} found in storage`);
    res.sendFile(name, { root: path.join(__dirname, "..", "instrumented") });
    return;
  }

  const content = req.body.source;
  instrumentationService.saveFile(name, content);

  const start = performance.now();
  common.runCommand(instrumentationService.getBabelCommand(name)).then(
    (result) => {
      const end = performance.now();
      saveStat(
        "time_instrumenting_ms",
        getStat("time_instrumenting_ms") + (end - start)
      );

      logger.info(`instrumented file ${name}`);
      res.sendFile(name, { root: path.join(__dirname, "..", "instrumented") });
    },
    (error) => {
      res.sendFile(name, { root: path.join(__dirname, "..", "original") });
    }
  );
};

module.exports = { instrument };
