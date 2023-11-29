require("dotenv").config({ path: "../../.env" });
const common = require("./common");

const codeqlPath = process.env.CODEQL_PATH;

function runQuery() {
  codeqlCommand = `${codeqlPath} --version`;
  common.runCommand(codeqlCommand).then(console.log("Done"));
}

runQuery();
