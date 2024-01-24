require("dotenv").config({ path: "../../.env" });

const { exec } = require("child_process");
const spawn = require("cross-spawn");

const { logger } = require("./log");

const loggingLevel = process.env.LOGGING_LEVEL;

/**
 * Function to execute a command asynchronously
 * @param {String} cmd the command to be executed
 * @returns a Promise that is rejected in case of an error, otherwise resolved
 */
function runCommand(cmd) {
  return new Promise((resolve, reject) => {
    exec(cmd, (error) => {
      if (error) {
        logger.error(error.message);
        reject();
        return;
      }
      resolve();
    });
  });
}

/**
 * Executes a command synchronously
 * @param {String} cmd the command to be executed
 */
function runCommandSync(cmd) {
  logger.info(`Running command: ${cmd}`);
  const exec = spawn.sync(cmd, { shell: true });
  if (exec.stderr && exec.stderr.toString().trim()) {
    logger.error(exec.stderr.toString().trim());
  }

  if (exec.stdout && exec.stdout.toString().trim() && loggingLevel == "debug") {
    logger.info(exec.stdout.toString().trim());
  }
}

module.exports = { runCommand, runCommandSync };
