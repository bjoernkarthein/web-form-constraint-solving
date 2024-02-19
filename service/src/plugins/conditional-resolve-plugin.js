const { template } = require("@babel/core");
const generator = require("@babel/generator").default;

const { getLocation, toFilePath } = require("./common");

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

        const args = `{
          type: "binary",
          left: {
            name: ${JSON.stringify(generator(left).code)},
            value: ${generator(left).code},
          },
          operator: ${JSON.stringify(operator)},
          right: {
            name: ${JSON.stringify(generator(right).code)},
            value: ${generator(right).code},
          },
          test: ${generator(test).code},
        }`;

        const code = `
        sendLog('CONDITIONAL_STATEMENT', ${args}, '${toFilePath(
          state.filename
        )}', ${getLocation(path, toFilePath(state.filename))}, 1);`;

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

        const args = `{
          type: "binary",
          left: {
            name: ${JSON.stringify(generator(left).code)},
            value: ${generator(left).code},
          },
          operator: ${JSON.stringify(operator)},
          right: {
            name: ${JSON.stringify(generator(right).code)},
            value: ${generator(right).code},
          },
          test: ${generator(test).code},
        }`;

        const code = `
        sendLog('CONDITIONAL_EXPRESSION', ${args}, '${toFilePath(
          state.filename
        )}', ${getLocation(path, toFilePath(state.filename))}, 1);`;

        const ast = template.ast(code);
        path.getStatementParent().insertBefore(ast);
      }
    },
  };
  return { visitor: ConditionaltVisitor };
};
