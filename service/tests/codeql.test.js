require("dotenv").config({ path: "../../../.env" });
const fs = require("fs");

const codeqlService = require("../src/codeql");

const testDataDir = "tests/test_data/codeql";
const queryDir = "src/codeql/queries";

function runCodeQLQueryOnFile(query, file, startLine, expression) {
  codeqlService.addDataToQuery(query, file, startLine, expression, queryDir);
  codeqlService.createDatabase(testDataDir);
  const resultFile = codeqlService.runQuery(query, queryDir);
  codeqlService.resetQuery(query, queryDir);
  return resultFile;
}

describe("Find flows", () => {
  test("Find simple literal variable comparison", () => {
    const resultFile = runCodeQLQueryOnFile(
      "to_literal_comp",
      "varcomp.js",
      2,
      "input.value"
    );

    const resultContent = fs.readFileSync(resultFile, "utf-8");
    expect(resultContent).toContain("value <= 0");
    expect(resultContent).not.toContain("value >= otherValue");
  });

  test("Find simple non literal variable comparison", () => {
    const resultFile = runCodeQLQueryOnFile(
      "to_var_comp",
      "varcomp.js",
      2,
      "input.value"
    );

    const resultContent = fs.readFileSync(resultFile, "utf-8");
    expect(resultContent).toContain("otherValue <= value");
    expect(resultContent).not.toContain("value <= 0");
  });

  test("Find simple regex", () => {
    const resultFile = runCodeQLQueryOnFile(
      "to_regex",
      "regex.js",
      1,
      'document.getElementById("email-field").value'
    );

    const resultContent = fs.readFileSync(resultFile, "utf-8");
    console.log(resultContent);
    expect(resultContent).toContain("expr.test(value)");
    expect(resultContent).toContain("/^a/g");
  });

  test("Find simple string match", () => {
    const resultFile = runCodeQLQueryOnFile(
      "to_string_match",
      "match.js",
      1,
      'document.getElementById("email-field").value'
    );

    const resultContent = fs.readFileSync(resultFile, "utf-8");
    expect(resultContent).toContain("value.match(expr)");
    expect(resultContent).toContain("someEmail");
    expect(resultContent).toContain("value.match(regex)");
    expect(resultContent).toContain("/^test/g");
  });
});
