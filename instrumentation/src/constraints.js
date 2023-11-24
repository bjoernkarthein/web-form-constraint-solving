const fs = require("fs");
const readline = require("readline");
const trace = require("./trace");

allTraces = [];

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
    allTraces.sort(compareTimeStamps);
    let add = false;
    let test = [];
    for (const t of allTraces) {
      if (t.action == trace.ACTION_ENUM.INTERACTION_START) {
        add = true;
      }

      if (add) {
        test.push(t);
      }

      if (t.action == trace.ACTION_ENUM.INTERACTION_END) {
        add = false;
        console.log(test.map((t) => t.action + " " + t.time));
        test = [];
      }
    }
  });
}

function compareTimeStamps(a, b) {
  return a.time - b.time;
}

module.exports = { analyseTraces };

analyseTraces();
