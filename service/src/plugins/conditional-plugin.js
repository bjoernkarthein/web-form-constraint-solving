const { template } = require("@babel/core");
const generator = require("@babel/generator").default;

const { buildTraceFunctionCall } = require("./common");

module.exports = function conditionalPlugin() {
  const ConditionalVisitor = {
    BinaryExpression(path, state) {
      try {
        const parentPath = path.findParent((p) => p.isStatement());
        if (!parentPath) return;

        const left = path.node.left;
        const leftCode = generator(left).code;
        const right = path.node.right;
        const rightCode = generator(right).code;
        const op = path.node.operator;
        const params = [];

        // if (generator(left).code !== "$mainInput[0].value") return; // TODO: remove

        params.push(
          `{expression: ${JSON.stringify(
            leftCode
          )}, value: ${leftCode}, line: ${left.loc.start.line}}`
        );
        params.push(`{operator: "${op}"}`);
        params.push(
          `{expression: ${JSON.stringify(
            rightCode
          )}, value: ${rightCode}, line: ${right.loc.start.line}}`
        );

        const code = getBinaryExpressionCode(path, state, params);
        const ast = template.ast(code);
        parentPath.insertAfter(ast);
      } catch (e) {
        // Do nothing
        console.error("Error instrumenting variable declaration:", e.message);
      }
    },
  };
  return { visitor: ConditionalVisitor };
};

function getBinaryExpressionCode(path, state, args) {
  return buildTraceFunctionCall(path, state, "'BINARY_EXPRESSION'", args);
}
