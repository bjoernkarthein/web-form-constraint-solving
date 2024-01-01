require("dotenv").config({ path: "../../.env" });

const fs = require("fs");

const common = require("./common");

const codeqlPath = process.env.CODEQL_PATH;
const codeqlDirectory = "codeql";
const queryDirectory = `${codeqlDirectory}/queries`;
const resultDirectory = `${codeqlDirectory}/results`;
const allQueries = ["to_comparisson", "to_regex"];

function createDatabase(source, database) {
  if (!fs.existsSync(resultDirectory)) {
    fs.mkdirSync(resultDirectory);
  }

  const databaseDir = `${codeqlDirectory}/${database}`;
  const command = `${codeqlPath} database create --language=javascript --source-root=${source} ${databaseDir}`;
  common.runCommandSync(command);
  return databaseDir;
}

let number = 0;

function runQuery(databaseDir, queryFile) {
  const command = `${codeqlPath} database analyze --format=csv --output=${codeqlDirectory}/results/${queryFile}-${number}-results.csv ${databaseDir} ${queryDirectory}/${queryFile}.ql`;
  number++;
  common.runCommandSync(command);
}

function runQueries(databaseDir, queryFiles) {
  for (const query of queryFiles) {
    runQuery(databaseDir, query);
  }
}

function prepareQueries(sourceFile, startLine, expression) {
  for (const query of allQueries) {
    addDataToQuery(query, sourceFile, startLine, expression);
  }
}

function addDataToQuery(queryFile, sourceFile, startLine, expression) {
  const data = fs.readFileSync(`${queryDirectory}/${queryFile}.ql`, {
    encoding: "utf8",
  });

  fs.writeFileSync(`${queryDirectory}/${queryFile}.ql`, "");
  const lines = data.split(/\r?\n/);

  for (let i = 0; i < lines.length; i++) {
    if (lines[i].endsWith("LOCATION")) {
      lines[i] = lines[i].replace(/FILE/, sourceFile);
      lines[i] = lines[i].replace(/12345/, startLine);
    }

    if (lines[i].endsWith("EXPRESSION")) {
      lines[i] = lines[i].replace(/NAME/, expression);
    }

    fs.appendFileSync(
      `${queryDirectory}/${queryFile}.ql`,
      `${lines[i]}${i < lines.length - 1 ? "\n" : ""}`,
      {
        encoding: "utf8",
      }
    );
  }
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

  fs.writeFileSync(`${queryDirectory}/${queryFile}.ql`, "");
  const lines = data.split(/\r?\n/);

  for (let i = 0; i < lines.length; i++) {
    if (lines[i].endsWith("LOCATION")) {
      lines[i] = lines[i].replace(/hasLocation\(.*\)/, resetArgs);
    }

    if (lines[i].endsWith("EXPRESSION")) {
      lines[i] = lines[i].replace(/toString\(\).*=.*".*"/, resetExpression);
    }

    fs.appendFileSync(
      `${queryDirectory}/${queryFile}.ql`,
      `${lines[i]}${i < lines.length - 1 ? "\n" : ""}`,
      {
        encoding: "utf8",
      }
    );
  }
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

const resetExpression = (match) => {
  if (match.includes("NAME")) {
    return match;
  }

  const values = match.split("=");
  return `${values[0].trim()} = "NAME"`;
};

module.exports = {
  createDatabase,
  runQuery,
  runQueries,
  prepareQueries,
  resetQuery,
  resetQueries,
  allQueries,
  resultDirectory
};
