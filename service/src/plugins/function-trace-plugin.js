const { template } = require("@babel/core");
const generator = require("@babel/generator").default;

const {
  buildTraceFunctionCall,
  getLocation,
  toExpressionString,
  toFilePath,
} = require("./common");

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
    // FunctionDeclaration(path, state) {
    //   if (!path.node.loc) {
    //     return;
    //   }
    //   const code = `
    //   b0aed879_987c_461b_af34_c9c06fe3ed46('NAMED_FUNCTION_CALL', ${getCallStatement(
    //     path
    //   )}, '${toFilePath(state.filename)}', ${getLocation(
    //     path,
    //     toFilePath(state.filename)
    //   )}, 1);`;

    //   try {
    //     const ast = template.ast(code);
    //     path.get("body").unshiftContainer("body", ast);
    //   } catch (e) {
    //     // Do nothing
    //   }
    // },
    // FunctionExpression(path, state) {
    //   if (!path.node.loc) {
    //     return;
    //   }
    //   const code = `
    //   b0aed879_987c_461b_af34_c9c06fe3ed46('UNNAMED_FUNCTION_CALL', ${getExpressionStatement(
    //     path
    //   )}, '${toFilePath(state.filename)}', ${getLocation(
    //     path,
    //     toFilePath(state.filename)
    //   )}, 1);`;

    //   try {
    //     const ast = template.ast(code);
    //     path.get("body").unshiftContainer("body", ast);
    //   } catch (e) {
    //     // Do nothing
    //   }
    // },
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
