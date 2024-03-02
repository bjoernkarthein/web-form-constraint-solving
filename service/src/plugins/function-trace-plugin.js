const { template } = require("@babel/core");
const generator = require("@babel/generator").default;

const { getLocation, toExpressionString, toFilePath } = require("./common");

module.exports = function functionTracePlugin() {
  const FunctionVisitor = {
    FunctionDeclaration(path, state) {
      if (!path.node.loc) {
        return;
      }
      const code = `
      sendLog('NAMED_FUNCTION_CALL', ${getCallStatement(path)}, '${toFilePath(
        state.filename
      )}', ${getLocation(path, toFilePath(state.filename))}, 1);`;

      try {
        const ast = template.ast(code);
        path.get("body").unshiftContainer("body", ast);
      } catch (e) {
        // Do nothing
      }
    },
    FunctionExpression(path, state) {
      if (!path.node.loc) {
        return;
      }
      const code = `
      sendLog('UNNAMED_FUNCTION_CALL', ${getExpressionStatement(
        path
      )}, '${toFilePath(state.filename)}', ${getLocation(
        path,
        toFilePath(state.filename)
      )}, 1);`;

      try {
        const ast = template.ast(code);
        path.get("body").unshiftContainer("body", ast);
      } catch (e) {
        // Do nothing
      }
    },
  };
  return { visitor: FunctionVisitor };
};

function getCallStatement(path) {
  const functionName = path.node.id.name;
  const params = path.node.params;

  const paramList = [];

  for (let i = 0; i < params.length; i++) {
    let paramName = params[i].name;
    paramList.push(`{ expression: "${paramName}", value: ${paramName} }`);
  }

  return `{ name: "${functionName}", args: [ ${paramList.join(", ")} ] }`;
}

function getExpressionStatement(path) {
  if (path.parent.type === "CallExpression") {
    const property = path.parent.callee.property || { name: "unkown" };
    const params = path.parent.arguments;

    let paramList = [];

    for (let i = 0; i < params.length; i++) {
      if (params[i].type !== "FunctionExpression") {
        const generatedCode = generator(params[i]);
        paramList.push(
          `{ expression: ${toExpressionString(generatedCode.code)}, value: ${
            generatedCode.code
          } }`
        );
      }
    }

    return `{ property: "${property.name}", args: [ ${paramList.join(", ")} ]}`;
  }

  return "{}";
}
