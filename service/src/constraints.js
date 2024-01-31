const events = require("events");
const fs = require("fs");
const readline = require("readline");
const codeql = require("./codeql");
const trace = require("./trace");

let allTraces = [];

function hasValue(object, value) {
  for (const [key, elem] of Object.entries(object)) {
    if (typeof elem === "string") {
      if (elem === value) {
        return [true, object, key];
      }
    } else if (typeof elem === "object") {
      return hasValue(elem, value);
    }
  }

  return [false, {}, ""];
}

async function analyseTraces() {
  const fileStream = fs.createReadStream(trace.traceLogFile);
  const rl = readline.createInterface({
    input: fileStream,
    crlfDelay: Infinity,
  });

  rl.on("line", (line) => {
    if (!line) {
      return;
    }
    allTraces.push(JSON.parse(line));
  });

  await events.once(rl, "close");
  const pointsOfInterest = processTraces();
  runQueries(pointsOfInterest);
  return extractConstraintCandidates();
}

function processTraces() {
  trace.cleanUp();
  const start = allTraces.filter(
    (t) => t.action == trace.ACTION_ENUM.INTERACTION_START
  )[0].time;
  const end = allTraces.filter(
    (t) => t.action == trace.ACTION_ENUM.INTERACTION_END
  )[0].time;
  const interaction_traces = allTraces.filter(
    (t) => t.time >= start && t.time <= end
  );
  interaction_traces.sort(compareTimestamps);

  // If there are no functions called in the browser we can return
  const browserTraces = interaction_traces.filter((t) => t.pageFile);
  if (browserTraces.length == 0) {
    return [];
  }

  // If the magic values are not included in the traces we can also return
  let importantTraces = findMagicValues(interaction_traces);
  if (importantTraces.length == 0) {
    return [];
  }

  return [...new Set(importantTraces.map((e) => JSON.stringify(e)))].map((e) =>
    JSON.parse(e)
  );
}

function compareTimestamps(a, b) {
  return a.time - b.time;
}

function runQueries(pointsOfInterest) {
  if (pointsOfInterest.length == 0) {
    return;
  }

  // TODO: Only rebuild database if the file set changed since last build
  const databaseDir = codeql.createDatabase(sourceDir, "db");

  const sourceDir = perpareForCodeQLQueries(allTraces);
  allTraces = [];

  for (const point of pointsOfInterest) {
    codeql.prepareQueries(
      point.location.file,
      point.location.start.line,
      point.expression
    );
    codeql.runQueries(databaseDir, codeql.allQueries);
    codeql.resetQueries();
  }

  fs.rmSync(sourceDir, { recursive: true, force: true });
  fs.rmSync(databaseDir, { recursive: true, force: true });
}

function extractConstraintCandidates() {
  const results = codeql.readResults();
  const codeLocations = results.map((res) => {
    return {
      type: res[0],
      locations: buildLocationsFromString(res[3]),
    };
  });
  console.log(JSON.stringify(codeLocations, null, 4));
  return { candidates: results };
  // fs.rmSync(codeql.resultDirectory, { recursive: true, force: true });
}

function buildLocationsFromString(value) {
  result = [];
  const locationRegExp = /\[\[([^\]]+)\|([^\]]+)\]\]/g;
  const matches = [...value.matchAll(locationRegExp)];
  for (const match of matches) {
    let sourceLoc = match[2];
    sourceLoc = sourceLoc.substring(1, sourceLoc.length - 1);
    sourceLoc = sourceLoc.split("/");
    sourceLoc = sourceLoc[sourceLoc.length - 1];
    const [file, startLine, startCol, endLine, endCol] = sourceLoc.split(":");
    result.push({
      file,
      startPos: { line: startLine, col: startCol },
      endPos: { line: endLine, col: endCol },
    });
  }
  return result;
}

function perpareForCodeQLQueries(traces) {
  if (!fs.existsSync("source")) {
    fs.mkdirSync("source");
  }

  let allFiles = traces.filter((t) => t.file).map((t) => t.file);
  allFiles = new Set(allFiles);

  for (const file of allFiles) {
    const elements = file.split("/");
    const fileName = elements[elements.length - 1];
    fs.copyFileSync(file, `source/${fileName}`);
  }

  return "source";
}

// TODO: Would be nicer if there was a universal way to get the right data for all types to only leave codeql queries and babel plugins as extension
function getExpressionByKey(t, element, key) {
  switch (t.action) {
    case trace.ACTION_ENUM.NAMED_FUNCTION_CALL:
      return key;
    case trace.ACTION_ENUM.CONDITIONAL_EXPRESSION:
    case trace.ACTION_ENUM.CONDITIONAL_STATEMENT:
      return element.name;
    default:
      // TODO
      return null;
  }
}

function findMagicValues(traceGroup) {
  const magicValues = traceGroup[0].args.values;
  const traces = traceGroup.filter((t) => t.pageFile);
  let tracesWithMagicValues = [];
  let found = true;
  for (const value of magicValues) {
    const tracesWithMagicValue = [];
    // Find first occurence of variable that contains the magic values in every execution
    for (const t of traces) {
      const [hasMagicValue, element, key] = hasValue(t, value);
      if (hasMagicValue) {
        tracesWithMagicValue.push({
          // TODO: Would be nicer if this was not needed somehow
          expression: getExpressionByKey(t, element, key),
          location: t.location,
        });
      }
    }

    tracesWithMagicValues = tracesWithMagicValues.concat(tracesWithMagicValue);
    found = found && tracesWithMagicValue.length > 0;
  }

  if (found) {
    return tracesWithMagicValues;
  } else {
    return [];
  }
}

module.exports = { analyseTraces };

// extractConstraintCandidates();
