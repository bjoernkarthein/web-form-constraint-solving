const { template } = require("@babel/core");
const generator = require("@babel/generator");
const op_path = require("path");

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
        }}"}\`, Date.now(), '${state.filename
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
      }}"}\`, Date.now(), '${state.filename
        .split(op_path.sep)
        .join(op_path.posix.sep)}', ${getLocation(path)}, 1);`;

      const ast = template.ast(code);
      path.insertAfter(ast);
    },
  };
  return { visitor: AssignmentVisitor };
};

function getLocation(path) {
  const location = path.node.loc;

  const start = {
    line: location.start.line,
    column: location.start.column,
    index: location.start.index,
  };

  const end = {
    line: location.end.line,
    column: location.end.column,
    index: location.end.index,
  };

  return JSON.stringify({
    start: start,
    end: end,
  });
}
