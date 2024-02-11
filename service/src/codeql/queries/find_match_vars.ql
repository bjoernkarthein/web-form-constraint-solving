/**
 * @name FindMatchVars
 * @kind problem
 * @problem.severity warning
 * @id javascript/find-match-vars
 */

// TODO: Add placeholder for name of the variable to select the exact one
import lib.input_flow

from DeclStmt decl, Assignment ass, Expr expr
where
  (isString(expr) or isRegexpLiteral(expr)) and
  decl.getADecl().getInit() = expr
  or
  ass.getRhs() = expr
select expr.getParentExpr(), expr.getParentExpr().toString()
