const { template } = require("@babel/core");
const generator = require("@babel/generator").default;

const { getLocation, toFilePath } = require("./common");

module.exports = function assignmentPlugin() {
  const AssignmentVisitor = {
    VariableDeclaration(path, state) {
      if (!path.node.loc) {
        return;
      }

      if (path.parent.type === "ForStatement") {
        return;
      }

      const declarations = path.node.declarations;
      for (let i = 0; i < declarations.length; i++) {
        let name = declarations[i].id.name;
        let value = declarations[i].init;

        let valueCode = { code: name };
        if (!!value) {
          valueCode = generator(value);
        }

        const code = `
        sendLog('VARIABLE_DECLARATION', { name: "${name}", expression: ${JSON.stringify(
          valueCode.code
        )}, value: ${valueCode.code} }, '${toFilePath(
          state.filename
        )}', ${getLocation(path, toFilePath(state.filename))}, 1);`;

        const ast = template.ast(code);

        if (path.parent.type === "ForOfStatement") {
          path.parentPath.get("body").unshiftContainer("body", ast);
        } else {
          path.insertAfter(ast);
        }
      }
    },

    AssignmentExpression(path, state) {
      if (!path.node.loc) {
        return;
      }

      if (path.parent.type === "ForStatement") {
        return;
      }

      let name = path.node.left.name;
      let value = path.node.right;
      valueCode = generator(value);

      const code = `sendLog('VARIABLE_ASSIGNMENT', { name: "${name}", expression: ${JSON.stringify(
        valueCode.code
      )}, value: ${valueCode.code} }, '${toFilePath(
        state.filename
      )}', ${getLocation(path, toFilePath(state.filename))}, 1);`;

      const ast = template.ast(code);
      if (path.parent.type === "ForOfStatement") {
        path.parent.get("body").unshiftContainer("body", ast);
      } else {
        path.insertAfter(ast);
      }
    },
  };
  return { visitor: AssignmentVisitor };
};
