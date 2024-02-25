require("dotenv").config({ path: "../../.env" });

const fs = require("fs");
const CSV = require("csv-string");

const common = require("./common");

const codeqlPath = process.env.CODEQL_PATH;
const codeqlDirectory = "codeql";
const databaseName = "db";
const databaseDirectory = `${codeqlDirectory}/${databaseName}`;
const queryDirectory = `${codeqlDirectory}/queries`;
const resultDirectory = `${codeqlDirectory}/results`;

// const allQueries = ["to_comp", "to_length_comp", "to_regex", "get_regex_vars"];
const allQueries = ["to_var_comp"];
const queryTypes = {
  COMPARISON_TO_ANOTHER_VARIABLE: "ToVarComp",
};

// const queryPlan = {
//   1: "to_comp",
//   2: "to_length_comp",
//   3: {
//     1: "to_regex",
//     2: { run: "get_regex_vars", if_results_for: "to_regex" },
//   },
// };

function createDatabase(source) {
  if (!fs.existsSync(codeqlDirectory)) {
    fs.mkdirSync(codeqlDirectory);
  }

  if (!fs.existsSync(resultDirectory)) {
    fs.mkdirSync(resultDirectory);
  }

  fs.rmSync(databaseDirectory, { recursive: true, force: true });
  const command = `${codeqlPath} database create --language=javascript --source-root=${source} ${databaseDirectory}`;
  common.runCommandSync(command);
}

let number = 0;

function runQuery(queryFile, queryDir = queryDirectory) {
  const command = `${codeqlPath} database analyze --format=csv --output=${codeqlDirectory}/results/${queryFile}-${number}-results.csv ${databaseDirectory} ${queryDir}/${queryFile}.ql --rerun`;
  number++;
  common.runCommandSync(command);
}

function runQueries(queryFiles, queryDir = queryDirectory) {
  for (const query of queryFiles) {
    runQuery(query, queryDir);
  }
}

function prepareQueries(sourceFile, startLine, expression) {
  for (const query of allQueries) {
    addDataToQuery(query, sourceFile, startLine, expression);
  }
}

function addDataToQuery(queryFile, sourceFile, startLine, expression, queryDir = queryDirectory) {
  const data = fs.readFileSync(`${queryDir}/${queryFile}.ql`, {
    encoding: "utf8",
  });

  fs.writeFileSync(`${queryDir}/${queryFile}.ql`, "");
  // This is needed because codeql for javascript automatically sanitizes strings
  // (https://github.com/github/codeql/blob/7361ad977a5dd5252d21f5fd23de47d75b763651/javascript/extractor/src/com/semmle/js/extractor/TextualExtractor.java#L121)
  if (expression.length > 20) {
    expression =
      expression.substring(0, 7) +
      " ... " +
      expression.substring(expression.length - 7);
  }

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
      `${queryDir}/${queryFile}.ql`,
      `${lines[i]}${i < lines.length - 1 ? "\n" : ""}`,
      {
        encoding: "utf8",
      }
    );
  }
}

function readResults() {
  results = new Set();

  if (!fs.existsSync(resultDirectory)) {
    return [];
  }

  const files = fs.readdirSync(resultDirectory);
  for (const file of files) {
    const csv_str = fs.readFileSync(`${resultDirectory}/${file}`, "utf-8");
    if (csv_str.trim()) {
      const csv = CSV.parse(csv_str);
      for (const line of csv) {
        if (line.length > 0 && !!line[0]) {
          results.add(JSON.stringify(line));
        }
      }
    }
  }
  return [...results];
}

function resetQueries() {
  for (const query of allQueries) {
    resetQuery(query);
  }
}

function resetQuery(queryFile, queryDir = queryDirectory) {
  const data = fs.readFileSync(`${queryDir}/${queryFile}.ql`, {
    encoding: "utf8",
  });

  fs.writeFileSync(`${queryDir}/${queryFile}.ql`, "");
  const lines = data.split(/\r?\n/);

  for (let i = 0; i < lines.length; i++) {
    if (lines[i].endsWith("LOCATION")) {
      lines[i] = lines[i].replace(/hasLocation\(.*\)/, resetArgs);
    }

    if (lines[i].endsWith("EXPRESSION")) {
      lines[i] = lines[i].replace(/toString\(\).*=.*".*"/, resetExpression);
    }

    fs.appendFileSync(
      `${queryDir}/${queryFile}.ql`,
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

function cleanUp() {
  fs.rmSync(databaseDirectory, { recursive: true, force: true });
  fs.rmSync(resultDirectory, { recursive: true, force: true });
}

module.exports = {
  addDataToQuery,
  cleanUp,
  createDatabase,
  readResults,
  runQuery,
  runQueries,
  prepareQueries,
  resetQuery,
  resetQueries,
  allQueries,
  databaseDirectory,
  queryTypes,
  resultDirectory,
};
