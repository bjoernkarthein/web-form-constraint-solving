const { template } = require("@babel/core");
const generator = require("@babel/generator").default;

const {
  buildTraceFunctionCall,
  getLocation,
  toFilePath,
  toExpressionString,
} = require("./common");

module.exports = function assignmentPlugin() {
  const AssignmentVisitor = {
    VariableDeclaration(path, state) {
      try {
        const declarations = path.node.declarations;
        const decls = [];
        for (const decl of declarations) {
          decls.push(
            `{ "expression": "${decl.id.name}", "value": ${decl.id.name}}`
          );
        }
        const code = getVarDeclCode(path, state, decls);
        path.insertAfter(template.ast(code));
      } catch (e) {
        // Do nothing
        console.error("Error instrumenting variable declaration:", e.message);
      }

      // if (!path.node.loc) {
      //   return;
      // }
      // if (path.parent.type === "ForStatement") {
      //   return;
      // }
      // const declarations = path.node.declarations;
      // for (let i = 0; i < declarations.length; i++) {
      //   let name = declarations[i].id.name;
      //   let value = declarations[i].init;
      //   let valueCode = { code: name };
      //   if (!!value) {
      //     valueCode = generator(value);
      //   }
      //   const expression = valueCode.code;
      //   const code = `
      //   b0aed879_987c_461b_af34_c9c06fe3ed46('VARIABLE_DECLARATION', { name: "${name}", expression: ${toExpressionString(
      //     expression
      //   )}, value: ${expression} }, '${toFilePath(
      //     state.filename
      //   )}', ${getLocation(path, toFilePath(state.filename))}, 1);`;

      //   try {
      //     const ast = template.ast(code);
      //     if (path.parent.type === "ForOfStatement") {
      //       path.parentPath.get("body").unshiftContainer("body", ast);
      //     } else {
      //       path.insertAfter(ast);
      //     }
      //   } catch (e) {
      //     // Do nothing
      //   }
      // }
    },
    // AssignmentExpression(path, state) {
    //   if (!path.node.loc) {
    //     return;
    //   }
    //   if (path.parent.type === "ForStatement") {
    //     return;
    //   }
    //   let name = path.node.left.name;
    //   let value = path.node.right;
    //   const valueCode = generator(value);
    //   const expression = valueCode.code;
    //   const code = `b0aed879_987c_461b_af34_c9c06fe3ed46('VARIABLE_ASSIGNMENT', { name: "${name}", expression: ${toExpressionString(
    //     expression
    //   )}, value: ${expression} }, '${toFilePath(
    //     state.filename
    //   )}', ${getLocation(path, toFilePath(state.filename))}, 1);`;

    //   try {
    //     const ast = template.ast(code);
    //     if (path.parent.type === "ForOfStatement") {
    //       path.parent.get("body").unshiftContainer("body", ast);
    //     } else {
    //       path.insertAfter(ast);
    //     }
    //   } catch (e) {
    //     // Do nothing
    //   }
    // },
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
