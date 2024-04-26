const { template } = require("@babel/core");
const generator = require("@babel/generator").default;

const { buildTraceFunctionCall } = require("./common");

module.exports = function assignmentPlugin() {
  const AssignmentVisitor = {
    VariableDeclaration(path, state) {
      try {
        const declarations = path.node.declarations;
        const decls = [];
        for (const decl of declarations) {
          const init = generator(decl.init).code || decl.id.name;
          decls.push(
            `{ "expression": ${JSON.stringify(init)}, "value": ${
              decl.id.name
            }, "line": ${decl.loc.start.line}}`
          );
        }
        const code = getVarDeclCode(path, state, decls);
        path.insertAfter(template.ast(code));
      } catch (e) {
        // Do nothing
        console.error("Error instrumenting variable declaration:", e.message);
      }
    },
  };
  return { visitor: AssignmentVisitor };
};

function getVarDeclCode(path, state, declarations) {
  return buildTraceFunctionCall(
    path,
    state,
    "'VARIABLE_DECLARATION'",
    `[${declarations}]`
  );
}
