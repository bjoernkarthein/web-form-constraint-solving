/**
 * @name To RegEx
 * @kind problem
 * @problem.severity warning
 * @id javascript/to-regex
 */

import input_flow

from DataFlow::SourceNode source, MethodCallExpr methodCall, VarUse use
where
  hasLocation(source.asExpr(), "FILE", 12345) and
  isRegExpCheck(methodCall, use) and
  source.flowsToExpr(methodCall.getArgument(0))
select methodCall,
  source.toString() + " is a user controlled value going into " + methodCall.toString()
