const fs = require("fs");

logFile = "../static/server-log.log";

function clear() {
  fs.writeFile(logFile, "", (err) => {
    if (err) {
      console.error(err);
    }
  });
}

module.exports = { clear };
