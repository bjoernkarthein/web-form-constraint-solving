/**
 * @name Test
 * @kind problem
 * @problem.severity warning
 * @id javascript/test
 */

import input_flow

// from MethodCallExpr m
// where isDocumentGetElementCall(m)
// select m, "This is a call to get an element from the DOM"
//
// from MethodCallExpr m
// where isPositiveSetCustomValidityCall(m)
// select m, "setting custom validity to valid"
//
// from MethodCallExpr m
// where isNegativeSetCustomValidityCall(m)
// select m, "setting custom validity to invalid"
//
// from MethodCallExpr m, VarUse use
// where isRegExpCheck(m, use)
// select m, "regex check on " + m.getArgument(0).toString()
//
// from DataFlow::MethodCallNode methodCall, DataFlow::Node source
// where methodCall.getCalleeName() = "test" and source.getASuccessor*() = methodCall.getArgument(0)
// select source, "Source flowing into first argument of test"
//
// from Parameter source, MethodCallExpr methodCall, VarUse use
// where
//   isRegExpCheck(methodCall, use) and
//   source.flow().getASuccessor*() = methodCall.getArgument(0).flow()
// select source, "Function parameter going into first argument of regex check"
//
// TODO: Somehow only check if it is an actual string value that is passed to the test method (document.get...('id').value)
// from DataFlow::Node source, MethodCallExpr methodCall, VarUse use
// where
//   isRegExpCheck(methodCall, use) and
//   source.getASuccessor*() = methodCall.getArgument(0).flow() and
//   isDocumentGetElementCall(source.asExpr())
// select methodCall, source.toString() + " going into regex check"
//
// from DataFlow::SourceNode source, MethodCallExpr methodCall, VarUse use
// where isRegExpCheck(methodCall, use) and source.flowsToExpr(methodCall.getArgument(0))
// select source, source.toString() + " going into regex check"
//
// from DataFlow::SourceNode source, MethodCallExpr methodCall, VarUse use
// where
//   isRegExpCheck(methodCall, use) and
//   isDocumentGetElementCall(source.asExpr().(PropAccess).getBase()) and
//   source.flowsToExpr(methodCall.getArgument(0))
// select source, source.toString() + " going into regex check"
//
// --------------------------
//
// from DataFlow::SourceNode source, MethodCallExpr methodCall, VarUse use
// where
//   source.asExpr() instanceof PropAccess and
//   isUserControlledValue(source.asExpr().(PropAccess)) and
//   isRegExpCheck(methodCall, use) and
//   source.flowsToExpr(methodCall.getArgument(0))
// select methodCall,
//   source.toString() + " is a user controlled value going into " + methodCall.toString()
//
from ControlFlowNode node, Comparison comp
where
  isUserControlledValue(node.(PropAccess)) and
  node.getASuccessor*() = comp
select node, node.toString() + " is a user controlled value going to " + comp.toString()
