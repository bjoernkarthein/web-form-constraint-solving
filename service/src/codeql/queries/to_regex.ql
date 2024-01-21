/**
 * @name To RegEx
 * @kind problem
 * @problem.severity warning
 * @id javascript/to-regex
 */

import lib.input_flow

from DataFlow::SourceNode source, MethodCallExpr methodCall
where
  hasLocation(source.asExpr(), "FILE", 12345) and // LOCATION
  source.asExpr().toString() = "NAME" and // EXPRESSION
  isRegExpCheck(methodCall) and
  source.flowsToExpr(methodCall.getArgument(0))
select methodCall, ""
