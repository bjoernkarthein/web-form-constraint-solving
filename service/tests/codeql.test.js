require("dotenv").config({ path: "../../../.env" });
const codeqlService = require("../src/codeql");

const testDataDir = "tests/test_data/codeql";
const queryDir = "src/codeql/queries"

describe("Find flows to regex", () => {
    test("Find simple regex", () => {
        codeqlService.addDataToQuery("to_regex", "regex.js", 1, 'document.getElementById("email-field").value', queryDir);
        codeqlService.createDatabase(testDataDir);
        codeqlService.runQuery("to_regex", queryDir);
        codeqlService.resetQuery("to_regex", queryDir);
    });
});