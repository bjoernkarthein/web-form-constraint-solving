const fs = require("fs");
const { exec } = require("child_process");
const log = require("./log");
const logger = log.logger;

/**
 * Helper functions for instrumentation
 */

const originalDir = "./original/";
const instrumentedDir = "./instrumented/";

/**
 * Save a file to be instrumented
 * @param {String} originalName original name of the file
 * @param {String} originalContent original content of the file
 */
function saveFile(originalName, originalContent) {
  if (!fs.existsSync(originalDir)) {
    fs.mkdirSync(originalDir);
  }

  if (!fs.existsSync(instrumentedDir)) {
    fs.mkdirSync(instrumentedDir);
  }

  fs.writeFile(`${originalDir}${originalName}`, originalContent, (err) => {
    if (err) {
      logger.error(err);
    }
  });
}

/**
 * Returns the babel command to instrument a file and save the instrumented file
 * @param {String} originalName name of the original file
 * @returns the command to instrument as a string
 */
function getBabelCommand(originalName) {
  return `npx babel ${originalDir}${originalName} --out-file ${instrumentedDir}${originalName}`;
}

/**
 * Function to execute a command asynchronously
 * @param {String} cmd the command to be executed
 * @returns a Promise that is rejected in case of an error, otherwise resolved
 */
function runCommand(cmd) {
  return new Promise((resolve, reject) => {
    exec(cmd, (error) => {
      if (error) {
        reject();
        return;
      }
      resolve();
    });
  });
}

function cleanUp() {
  fs.rmSync(originalDir, { recursive: true, force: true });
  fs.rmSync(instrumentedDir, { recursive: true, force: true });
}

module.exports = {
  saveFile,
  runCommand,
  getBabelCommand,
  cleanUp,
  instrumentedDir,
};
