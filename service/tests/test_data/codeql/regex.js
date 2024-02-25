const value = document.getElementById("email-field").value;

const expr = new RegExp(/^.+@.+$/g);
const otherExpr = /^a/g;

expr.test(value);
otherExpr.test(value);
/^a/g.test(value);
