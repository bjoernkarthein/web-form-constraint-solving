const constraintService = require("../src/constraints");

describe("Find magic value", () => {
  test("Object that has no values should result in false", () => {
    const [result, object, key] = constraintService.hasValue({}, "test");
    expect(result).toBe(false);
    expect(object).toStrictEqual({});
    expect(key).toBe("");
  });

  test("Object that does not have value should result in false", () => {
    const [result, object, key] = constraintService.hasValue(
      { 1: ["a", "b", "c"], 2: { i: "tes", ii: "est" }, 3: "Test", 4: "tEst" },
      "test"
    );
    expect(result).toBe(false);
    expect(object).toStrictEqual({});
    expect(key).toBe("");
  });

  test("Object that has value as string should be true", () => {
    const [result, object, key] = constraintService.hasValue(
      { 1: "some", 2: "thing", 3: "test" },
      "test"
    );
    expect(result).toBe(true);
    expect(object).toStrictEqual({ 1: "some", 2: "thing", 3: "test" });
    expect(key).toBe("3");
  });

  test("Object that has value in child should be true", () => {
    const [result, object, key] = constraintService.hasValue(
      { 1: "some", 2: { 1: "thing", test: "test" }, 3: "not", 4: "equal" },
      "test"
    );
    expect(result).toBe(true);
    expect(object).toStrictEqual({ 1: "thing", test: "test" });
    expect(key).toBe("test");
  });

  test("Object that has value in child deep should be true", () => {
    const [result, object, key] = constraintService.hasValue(
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
    expect(key).toBe("here");
  });

  test("Object that has value multiple times returns true and the first object", () => {
    const [result, object, key] = constraintService.hasValue(
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
    expect(key).toBe("first");
  });

  test("Object that has value in array should be true", () => {
    const [result, object, key] = constraintService.hasValue(
      { 1: "some", 2: ["test", "thing"], 3: "not", 4: "equal" },
      "test"
    );
    expect(result).toBe(true);
    expect(object).toStrictEqual(["test", "thing"]);
    expect(key).toBe("0");
  });

  test("Object that has value in array deep should be true", () => {
    const [result, object, key] = constraintService.hasValue(
      { 1: "some", 2: [{ 1: "thing" }, { 1: "test" }], 3: "not", 4: "equal" },
      "test"
    );
    expect(result).toBe(true);
    expect(object).toStrictEqual({ 1: "test" });
    expect(key).toBe("1");
  });
});