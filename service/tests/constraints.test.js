const constraintService = require("../src/constraints");
const codeqlService = require("../src/codeql");

describe("Find magic value", () => {
  test("Object that has no values should result in false", () => {
    const [result, object] = constraintService.hasValue({}, "test");
    expect(result).toBe(false);
    expect(object).toStrictEqual({});
  });

  test("Object that does not have value should result in false", () => {
    const [result, object] = constraintService.hasValue(
      { 1: ["a", "b", "c"], 2: { i: "tes", ii: "est" }, 3: "Test", 4: "tEst" },
      "test"
    );
    expect(result).toBe(false);
    expect(object).toStrictEqual({});
  });

  test("Object that has value as string should be true", () => {
    const [result, object] = constraintService.hasValue(
      { 1: "some", 2: "thing", 3: "test" },
      "test"
    );
    expect(result).toBe(true);
    expect(object).toStrictEqual({ 1: "some", 2: "thing", 3: "test" });
  });

  test("Object that has value in child should be true", () => {
    const [result, object] = constraintService.hasValue(
      { 1: "some", 2: { 1: "thing", test: "test" }, 3: "not", 4: "equal" },
      "test"
    );
    expect(result).toBe(true);
    expect(object).toStrictEqual({ 1: "thing", test: "test" });
  });

  test("Object that has value in child deep should be true", () => {
    const [result, object] = constraintService.hasValue(
      {
        1: "some",
        2: {
          1: "thing",
          test: {
            a: "s",
            b: "d",
            c: { i: "q", ii: { here: "test" }, iii: { x: "y" } },
          },
        },
        3: "not",
        4: "equal",
      },
      "test"
    );
    expect(result).toBe(true);
    expect(object).toStrictEqual({ here: "test" });
  });

  test("Object that has value multiple times returns true and the first object", () => {
    const [result, object] = constraintService.hasValue(
      {
        1: "some",
        2: {
          1: "thing",
          test: {
            b: "d",
            c: { i: "q", ii: { first: "test" }, iii: { x: "y" } },
            second: "test",
          },
        },
        3: "not",
        4: "equal",
      },
      "test"
    );
    expect(result).toBe(true);
    expect(object).toStrictEqual({ first: "test" });
  });

  test("Object that has value in array should be true", () => {
    const [result, object] = constraintService.hasValue(
      { 1: "some", 2: ["test", "thing"], 3: "not", 4: "equal" },
      "test"
    );
    expect(result).toBe(true);
    expect(object).toStrictEqual(["test", "thing"]);
  });

  test("Object that has value in array deep should be true", () => {
    const [result, object] = constraintService.hasValue(
      { 1: "some", 2: [{ 1: "thing" }, { 1: "test" }], 3: "not", 4: "equal" },
      "test"
    );
    expect(result).toBe(true);
    expect(object).toStrictEqual({ 1: "test" });
  });

  test("Object should have value under key expression", () => {
    const [result, object] = constraintService.hasValue(
      {
        action: "CONDITIONAL_STATEMENT",
        args: {
          type: "binary",
          left: { expression: "input.value", value: ".+Y" },
          operator: "!=",
          right: {
            expression: 'document.getElementById("mail").value',
            value: "%g2]w",
          },
          test: true,
        },
        time: 1709121930721,
        file: "C:/Users/Björn/Documents/git/invariant-based-web-form-testing/service/src/original/script.js",
        location: {
          file: "script.js",
          start: { line: 12, column: 2, index: 344 },
          end: { line: 16, column: 3, index: 512 },
        },
        pageFile: 1,
      },
      "%g2]w"
    );
    expect(result).toBe(true);
    expect(object).toStrictEqual({
      expression: 'document.getElementById("mail").value',
      value: "%g2]w",
    });
    expect(object.expression).toBe('document.getElementById("mail").value');
  });
});

const testDataDir = "tests/test_data/source";
const queryDir = "src/codeql/queries";

function runCodeQLQueryOnFile(query, file, startLine, expression) {
  codeqlService.addDataToQuery(query, file, startLine, expression, queryDir);
  codeqlService.createDatabase(testDataDir);
  const resultFile = codeqlService.runQuery(query, queryDir);
  codeqlService.resetQuery(query, queryDir);
  return resultFile;
}

describe("Extract constraint candidates", () => {
  // test("Get constraint candidates for literal comparison", () => {
  //   runCodeQLQueryOnFile("to_literal_comp", "litcomp.js", 2, "input.value");
  //   const candidates =
  //     constraintService.extractConstraintCandidates(testDataDir);
  //   expect(candidates.length).toBe(1);
  //   expect(candidates[0].type).toBe("LitComp");
  //   expect(candidates[0].operator).toBe("<=");
  //   expect(candidates[0].otherValue).toBe("0");
  // });

  // test("Get constraint candidates for variable comparison", () => {
  //   runCodeQLQueryOnFile("to_var_comp", "varcomp.js", 2, "input.value");
  //   const candidates =
  //     constraintService.extractConstraintCandidates(testDataDir);
  //   console.log(candidates);
  //   expect(candidates.length).toBe(1);
  //   expect(candidates[0].type).toBe("VarComp");
  //   expect(candidates[0].operator).toBe(">=");
  //   expect(candidates[0].otherValue).toStrictEqual({
  //     type: "unknown variable",
  //     value: "otherValue",
  //   });
  // });

  test("Get constraint candidates for regex test", () => {
    runCodeQLQueryOnFile(
      "to_regex",
      "regex.js",
      2,
      'document.getElementById("mail").value'
    );
    const candidates =
      constraintService.extractConstraintCandidates(testDataDir);

    expect(candidates.length).toBe(1);
    expect(candidates[0]).toStrictEqual({
      type: "PatternTest",
      pattern: "/^.*@.*$/g",
    });
  });
});
