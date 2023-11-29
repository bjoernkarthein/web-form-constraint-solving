const { exec } = require("child_process");
const spawn = require("cross-spawn");

const { logger } = require("./log");

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

/**
 * Function to execute a command synchronously
 * @param {String} cmd the command to be executed
 */
function runCommandSync(cmd) {
  logger.info(`Running command: ${cmd}`);
  console.log(cmd);
  const exec = spawn.sync(cmd, { shell: true });
  if (exec.stderr && exec.stderr.toString().trim()) {
    logger.error(exec.stderr.toString().trim());
  }

  if (exec.stdout && exec.stdout.toString().trim()) {
    logger.info(exec.stdout.toString().trim());
  }
}

module.exports = { runCommand, runCommandSync };
