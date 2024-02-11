/**
 * @name FindRegexVars
 * @kind problem
 * @problem.severity warning
 * @id javascript/find-regex-vars
 */

// TODO: Add placeholder for name of the variable to select the exact one
import lib.input_flow

from DeclStmt decl, Assignment ass, RegExpConstructor regex
where decl.getADecl().getInit() = regex or ass.getRhs() = regex
select regex.getParentExpr(), regex.getParentExpr().toString()
