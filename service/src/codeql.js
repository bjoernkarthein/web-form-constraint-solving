require("dotenv").config({ path: "../../.env" });

const fs = require("fs");

const common = require("./common");

const codeqlPath = process.env.CODEQL_PATH;
const codeqlDirectory = "codeql";
const queryDirectory = `${codeqlDirectory}/queries`;
const allQueries = ["to_comparisson", "to_regex"];

function createDatabase(source, database) {
  const databaseDir = `${codeqlDirectory}/${database}`;
  const command = `${codeqlPath} database create --language=javascript --source-root=${source} ${databaseDir}`;
  common.runCommandSync(command);
  return databaseDir;
}

let number = 0;

function runQuery(databaseDir, queryFile) {
  const command = `${codeqlPath} database analyze --format=sarifv2.1.0 --output=${codeqlDirectory}/results/${queryFile}-${number}-results.sarif ${databaseDir} ${queryDirectory}/${queryFile}.ql`;
  number++;
  common.runCommandSync(command);
}

function runQueries(databaseDir, queryFiles) {
  for (const query of queryFiles) {
    runQuery(databaseDir, query);
  }
}

function prepareQueries(sourceFile, startLine) {
  for (const query of allQueries) {
    addLocationToQuery(query, sourceFile, startLine);
  }
}

function addLocationToQuery(queryFile, sourceFile, startLine) {
  const data = fs.readFileSync(`${queryDirectory}/${queryFile}.ql`, {
    encoding: "utf8",
  });
  var result = data.replace(/FILE/g, sourceFile);
  result = result.replace(/12345/g, startLine);
  fs.writeFileSync(`${queryDirectory}/${queryFile}.ql`, result, {
    encoding: "utf8",
  });
}

function resetQueries() {
  for (const query of allQueries) {
    resetQuery(query);
  }
}

function resetQuery(queryFile) {
  const data = fs.readFileSync(`${queryDirectory}/${queryFile}.ql`, {
    encoding: "utf8",
  });
  var result = data.replace(/hasLocation\(.*\)/g, resetArgs);
  fs.writeFileSync(`${queryDirectory}/${queryFile}.ql`, result, {
    encoding: "utf8",
  });
}

const resetArgs = (match) => {
  if (match.includes("FILE") && match.includes("12345")) {
    return match;
  }

  const args = match.split(",");
  args[1] = '"FILE"';
  args[2] = "12345)";
  return args.join(", ");
};

module.exports = {
  createDatabase,
  runQuery,
  runQueries,
  addLocationToQuery,
  prepareQueries,
  resetQuery,
  resetQueries,
  allQueries,
};
