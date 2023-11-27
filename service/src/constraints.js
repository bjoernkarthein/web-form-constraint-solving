const fs = require("fs");
const readline = require("readline");
const trace = require("./trace");
const log = require("./log");
const logger = log.logger;

allTraces = [];
groupedTraces = [];

function analyseTraces() {
  const fileStream = fs.createReadStream(trace.traceLogFile);
  const rl = readline.createInterface({
    input: fileStream,
    crlfDelay: Infinity,
  });

  rl.on("line", (line) => {
    if (!line) {
      return;
    }
    allTraces.push(JSON.parse(line));
  });

  rl.on("close", () => {
    console.log("Finished reading the file.");
    allTraces.sort(compareTimestamps);
    let add = false;
    let interactions = [];
    for (const t of allTraces) {
      if (t.action == trace.ACTION_ENUM.INTERACTION_START) {
        add = true;
      }

      if (add) {
        interactions.push(t);
      }

      if (t.action == trace.ACTION_ENUM.INTERACTION_END) {
        add = false;
        groupedTraces.push(interactions);
        interactions = [];
      }
    }

    extractConstraintCandidates();
  });
}

function compareTimestamps(a, b) {
  return a.time - b.time;
}

function extractConstraintCandidates() {
  for (const traceGroup of groupedTraces) {
    console.log("--");
    for (const t of traceGroup) {
      switch (t.action) {
        case trace.ACTION_ENUM.INTERACTION_START:
          console.log(t.args.spec.reference);
          break;
        case trace.ACTION_ENUM.INTERACTION_END:
          console.log(t.args.spec.reference);
          break;
        case trace.ACTION_ENUM.VALUE_INPUT:
          console.log(t.args.value);
          break;
        default:
          logger.error(
            `Action type ${t.action} was not recognized and can not be parsed`
          );
      }
    }
  }
}

module.exports = { analyseTraces };

analyseTraces();
