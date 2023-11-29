require("dotenv").config({ path: "../../.env" });
const common = require("./common");

const codeqlPath = process.env.CODEQL_PATH;
const codeqlDirectory = "codeql";

function createDatabase(source, name) {
  command = `${codeqlPath} database create --language=javascript --source-root=${source} ${codeqlDirectory}/${name}`;
  common.runCommandSync(command);
}

function runQuery() {
  createDatabase("original", "db");
}

runQuery();
