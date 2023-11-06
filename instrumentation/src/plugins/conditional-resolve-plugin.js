const { template } = require("@babel/core");
const generator = require("@babel/generator");
const op_path = require("path");

module.exports = function conditionalResolvePlugin() {
  const ConditionaltVisitor = {
    IfStatement(path, state) {
      if (!path.node.loc) {
        return;
      }

      if (path.node.test.type === "BinaryExpression") {
        test = path.node.test;
        left = test.left;
        right = test.right;
        operator = test.operator;

        code = `
        sendLog('CONDITIONAL_STATEMENT', \`{"type": "binary", "left": "\${${
          generator.default(left).code
        }}", "operator": ${operator}, "right": "\${${
          generator.default(right).code
        }}", "test": "\${${
          generator.default(test).code
        }}"}\`, Date.now(), '${state.filename
          .split(op_path.sep)
          .join(op_path.posix.sep)}', ${getLocation(path)}, 1);`;

        const ast = template.ast(code);
        path.insertBefore(ast);
      }
    },

    ConditionalExpression(path, state) {
      if (!path.node.loc) {
        return;
      }

      if (path.node.test.type === "BinaryExpression") {
        test = path.node.test;
        left = test.left;
        right = test.right;
        operator = test.operator;

        code = `
        sendLog('CONDITIONAL_EXPRESSION', \`{"type": "binary", "left": "\${${
          generator.default(left).code
        }}", "operator": ${operator}, "right": "\${${
          generator.default(right).code
        }}", "test": "\${${
          generator.default(test).code
        }}"}\`, Date.now(), '${state.filename
          .split(op_path.sep)
          .join(op_path.posix.sep)}', ${getLocation(path)}, 1);`;

        const ast = template.ast(code);
        path.getStatementParent().insertBefore(ast);
      }
    },
  };
  return { visitor: ConditionaltVisitor };
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
