const { template } = require("@babel/core");

const { buildTraceFunctionCall } = require("./common");

module.exports = function functionTracePlugin() {
  const FunctionVisitor = {
    ArrowFunctionExpression(path, state) {
      try {
        const params = [];
        for (const p of path.node.params) {
          if (!!p.name) {
            params.push(
              `{"expression": "${p.name}", "value": ${p.name}, "line": ${p.loc.start.line}}`
            );
          }
        }

        if (params.length > 0) {
          const code = getArrowFunctionCode(path, state, params);
          const ast = template.ast(code);
          path.get("body").unshiftContainer("body", ast);
        }
      } catch (e) {
        // Do nothing
        console.error("Error instrumenting arrow function:", e.message);
      }
    },
  };
  return { visitor: FunctionVisitor };
};

function getArrowFunctionCode(path, state, args) {
  return buildTraceFunctionCall(
    path,
    state,
    "'ARROW_FUNCTION_CALL'",
    `[${args}]`
  );
}
