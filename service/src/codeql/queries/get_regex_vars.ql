import lib.input_flow

from DeclStmt decl, Assignment ass, RegExpConstructor regex
where decl.getADecl().getInit() = regex or ass.getRhs() = regex
select regex.getParentExpr(), regex.getParentExpr().toString()
