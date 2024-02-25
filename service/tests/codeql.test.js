require("dotenv").config({ path: "../../../.env" });
const fs = require("fs");

const codeqlService = require("../src/codeql");

const testDataDir = "tests/test_data/codeql";
const queryDir = "src/codeql/queries";

describe("Find flows to regex", () => {
  test("Find simple regex", () => {
    codeqlService.addDataToQuery(
      "to_regex",
      "regex.js",
      1,
      'document.getElementById("email-field").value',
      queryDir
    );
    codeqlService.createDatabase(testDataDir);
    const resultFile = codeqlService.runQuery("to_regex", queryDir);
    codeqlService.resetQuery("to_regex", queryDir);

    const resultContent = fs.readFileSync(resultFile, "utf-8");
    expect(resultContent).toContain("expr.test(value)");
    expect(resultContent).toContain("/^a/g");
  });

  test("Find simple string match", () => {
    codeqlService.addDataToQuery(
      "to_string_match",
      "match.js",
      1,
      'document.getElementById("email-field").value',
      queryDir
    );
    codeqlService.createDatabase(testDataDir);
    const resultFile = codeqlService.runQuery("to_string_match", queryDir);
    codeqlService.resetQuery("to_string_match", queryDir);

    const resultContent = fs.readFileSync(resultFile, "utf-8");
    expect(resultContent).toContain("value.match(expr)");
    expect(resultContent).toContain("someEmail");
    expect(resultContent).toContain("value.match(regex)");
    expect(resultContent).toContain("/^test/g");
  });
});
