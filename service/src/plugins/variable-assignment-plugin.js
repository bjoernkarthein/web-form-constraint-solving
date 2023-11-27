const { template } = require("@babel/core");
const generator = require("@babel/generator");
const op_path = require("path");

const { getLocation } = require("./common");

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

        valueCode = generator.default(value);

        code = `
        sendLog('VARIABLE_DECLARATION', \`{"name": "${name}", "value": "\${${
          valueCode.code
        }}"}\`, '${state.filename
          .split(op_path.sep)
          .join(op_path.posix.sep)}', ${getLocation(path)}, 1);`;

        const ast = template.ast(code);
        path.insertAfter(ast);
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
      valueCode = generator.default(value);

      code = `sendLog('VARIABLE_ASSIGNMENT', \`{"name": "${name}", "value": "\${${
        valueCode.code
      }}"}\`, '${state.filename
        .split(op_path.sep)
        .join(op_path.posix.sep)}', ${getLocation(path)}, 1);`;

      const ast = template.ast(code);
      path.insertAfter(ast);
    },
  };
  return { visitor: AssignmentVisitor };
};
