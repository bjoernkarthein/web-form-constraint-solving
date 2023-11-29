const { exec } = require("child_process");

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
    }).stdout.on("data", function (data) {
      console.log(data);
    });
  });
}

module.exports = { runCommand };
