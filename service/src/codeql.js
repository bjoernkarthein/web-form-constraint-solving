require("dotenv").config({ path: "../../.env" });

const CSV = require("csv-string");
const fs = require("fs");
const path = require("path");
const { performance } = require("perf_hooks");

const common = require("./common");
const { getStat, saveStat } = require("../evaluation/evaluation");

const codeqlPath = process.env.CODEQL_PATH;
const codeqlDirectory = "codeql";
const databaseName = "db";
const databaseDirectory = `${codeqlDirectory}/${databaseName}`;
const queryDirectory = `${codeqlDirectory}/queries`;
const resultDirectory = `${codeqlDirectory}/results`;

const pathQueries = ["to_literal_comp_path", "to_literal_length_comp_path"];
const otherQueries = [
  // "to_literal_comp",
  // "to_literal_length_comp",
  "to_regex",
  "to_string_match",
  "to_var_comp",
];

const allQueries = pathQueries.concat(otherQueries);

const queryTypes = {
  COMPARISON_TO_A_LITERAL: "To Literal Comparison",
  COMPARISON_TO_ANOTHER_VARIABLE: "To Variable Comparison",
  COMPARISON_TO_LITERAL_LENGTH: "To Literal Length Comparison",
  REGEX_TEST: "To Regex Test",
  STRING_MATCH: "To String Match",
};
const resultLocationPattern = /\[\[(.*?)\|(.*?)\]\]/g;

let count = 0;
function createDatabase(source) {
  count = 0;

  if (!fs.existsSync(codeqlDirectory)) {
    fs.mkdirSync(codeqlDirectory);
  }

  if (!fs.existsSync(resultDirectory)) {
    fs.mkdirSync(resultDirectory);
  }

  fs.rmSync(databaseDirectory, { recursive: true, force: true });
  const command = `${codeqlPath} database create --language=javascript --source-root=${source} ${databaseDirectory}`;
  const start = performance.now();
  common.runCommandSync(command);
  const end = performance.now();
  saveStat("time_analyzing_ms", getStat("time_analyzing_ms") + (end - start));
}

function runQuery(queryFile, queryDir = queryDirectory) {
  if (queryFile.includes("_path")) {
    return runPathQuery(queryFile, queryDir);
  } else {
    return runRegularQuery(queryFile, queryDir);
  }
}

function runRegularQuery(queryFile, queryDir = queryDirectory) {
  const outFile = `${codeqlDirectory}/results/${queryFile}-${count}-results.csv`;
  const command = `${codeqlPath} database analyze --format=csv --output=${outFile} ${databaseDirectory} ${queryDir}/${queryFile}.ql --rerun --verbose`;
  count++;
  const start = performance.now();
  common.runCommandSync(command);
  const end = performance.now();
  saveStat("time_analyzing_ms", getStat("time_analyzing_ms") + (end - start));
  return outFile;
}

function runPathQuery(queryFile, queryDir = queryDirectory) {
  const bqrsOutFile = `${codeqlDirectory}/results/${queryFile}-${count}-results.bqrs`;
  const jsonOutFile = `${codeqlDirectory}/results/${queryFile}-${count}-decoded.json`;
  const runQueryCmd = `${codeqlPath} query run --database=${databaseDirectory} --output=${bqrsOutFile} ${queryDir}/${queryFile}.ql`;
  const decodeFileCmd = `${codeqlPath} bqrs decode --output=${jsonOutFile} --format=json --entities=id,string,url ${bqrsOutFile}`;
  count++;
  const start = performance.now();
  common.runCommandSync(runQueryCmd);
  common.runCommandSync(decodeFileCmd);
  const end = performance.now();
  saveStat("time_analyzing_ms", getStat("time_analyzing_ms") + (end - start));
  return jsonOutFile;
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

function addDataToQuery(
  queryFile,
  sourceFile,
  startLine,
  expression,
  queryDir = queryDirectory
) {
  const data = fs.readFileSync(`${queryDir}/${queryFile}.ql`, {
    encoding: "utf8",
  });

  fs.writeFileSync(`${queryDir}/${queryFile}.ql`, "");
  // This is needed because codeql for javascript automatically sanitizes long strings
  // (https://github.com/github/codeql/blob/7361ad977a5dd5252d21f5fd23de47d75b763651/javascript/extractor/src/com/semmle/js/extractor/TextualExtractor.java#L121)
  expression = shortenCodeQLString(expression);
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

function shortenCodeQLString(input) {
  if (input.length > 20) {
    input = input.substring(0, 7) + " ... " + input.substring(input.length - 7);
  }
  return input;
}

function readCSVResults() {
  results = new Set();

  if (!fs.existsSync(resultDirectory)) {
    return [];
  }

  const files = fs.readdirSync(resultDirectory);
  for (const file of files) {
    if (path.extname(file).toLowerCase() === ".csv") {
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
  }
  return [...results];
}

function readPathResults() {
  const results = new Set();

  if (!fs.existsSync(resultDirectory)) {
    return [];
  }

  const files = fs.readdirSync(resultDirectory);
  for (const file of files) {
    if (path.extname(file).toLowerCase() === ".json") {
      const res_json = fs.readFileSync(`${resultDirectory}/${file}`, "utf-8");
      // TODO: do only add if the select tuples are not already in another object?
      results.add(res_json);
    }
  }
  return [...results].map((s) => JSON.parse(s));
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
  readCSVResults,
  readPathResults,
  runQuery,
  runQueries,
  prepareQueries,
  resetQuery,
  resetQueries,
  shortenCodeQLString,
  allQueries,
  databaseDirectory,
  queryTypes,
  resultDirectory,
  resultLocationPattern,
};
