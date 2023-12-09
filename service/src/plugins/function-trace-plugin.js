const { template } = require("@babel/core");
const generator = require("@babel/generator");

const { getLocation, toFilePath } = require("./common");

module.exports = function functionTracePlugin() {
  const FunctionVisitor = {
    FunctionDeclaration(path, state) {
      if (!path.node.loc) {
        return;
      }

      const code = `
      sendLog('NAMED_FUNCTION_CALL', \`${getCallStatement(
        path
      )}\`, '${toFilePath(state.filename)}', ${getLocation(
        path,
        toFilePath(state.filename)
      )}, 1);`;

      const ast = template.ast(code);
      path.get("body").unshiftContainer("body", ast);
    },

    FunctionExpression(path, state) {
      if (!path.node.loc) {
        return;
      }

      const code = `
      sendLog('UNNAMED_FUNCTION_CALL', \`${getExpressionStatement(
        path
      )}\`, '${toFilePath(state.filename)}', ${getLocation(
        path,
        toFilePath(state.filename)
      )}, 1);`;

      const ast = template.ast(code);
      path.get("body").unshiftContainer("body", ast);
    },
  };
  return { visitor: FunctionVisitor };
};

function getCallStatement(path) {
  const functionName = path.node.id.name;
  const params = path.node.params;

  let paramObject = {};

  for (let i = 0; i < params.length; i++) {
    let paramName = params[i].name;
    paramObject[paramName] = "${" + paramName + "}";
  }

  return `{"name":"${functionName}","args":${JSON.stringify(paramObject)}}`;
}

function getExpressionStatement(path) {
  if (path.parent.type === "CallExpression") {
    const property = path.parent.callee.property;
    const params = path.parent.arguments;

    let paramList = [];

    for (let i = 0; i < params.length; i++) {
      if (params[i].type !== "FunctionExpression") {
        const generatedCode = generator.default(params[i]);
        paramList.push(generatedCode.code);
      }
    }

    return `{"property":"${property.name}","args":[${[...paramList]}]}`;
  }

  // TODO: what in any other case?
  return "";
}
