import javascript

predicate isDocument(Expr e) { e.toString() = "document" }

predicate isGetElementById(string s) { s = "getElementById" }

predicate isGetElementByClassName(string s) { s = "getElementByClassName" }

predicate isGetElementByTagName(string s) { s = "getElementByTagName" }

predicate isQuerySelector(string s) { s = "querySelector" }

predicate isQuerySelectorAll(string s) { s = "querySelectorAll" }

predicate isDocumentGetElementCall(MethodCallExpr methodCall) {
  isDocument(methodCall.getReceiver()) and
  (
    isGetElementById(methodCall.getMethodName()) or
    isGetElementByClassName(methodCall.getMethodName()) or
    isGetElementByTagName(methodCall.getMethodName()) or
    isQuerySelector(methodCall.getMethodName()) or
    isQuerySelectorAll(methodCall.getMethodName())
  )
}

predicate isUserControlledValue(PropAccess access) {
  isDocumentGetElementCall(access.getBase().getAPredecessor*())
}

predicate isEmptyStringExpr(Expr e) {
  exists(string s |
    e instanceof StringLiteral and
    e.getStringValue() = s and
    s = ""
  )
}

predicate isSetCustomValidityCall(MethodCallExpr methodCall) {
  methodCall.getMethodName() = "setCustomValidity"
}

predicate isPositiveSetCustomValidityCall(MethodCallExpr methodCall) {
  isSetCustomValidityCall(methodCall) and isEmptyStringExpr(methodCall.getArgument(0))
}

predicate isNegativeSetCustomValidityCall(MethodCallExpr methodCall) {
  isSetCustomValidityCall(methodCall) and not isEmptyStringExpr(methodCall.getArgument(0))
}

predicate hasValidityEffects(IfStmt ifStatement) {
  isSetCustomValidityCall(ifStatement.getThen().getAChildExpr()) or
  isSetCustomValidityCall(ifStatement.getElse().getAChildExpr())
}

class RegExpConstructor extends InvokeExpr {
  RegExpConstructor() { this instanceof NewExpr and this.getCallee().toString() = "RegExp" }
}

class VariableAssignment extends ControlFlowNode {
  VariableAssignment() { this instanceof DeclStmt or this instanceof Assignment }
}

predicate isRegExpCheck(MethodCallExpr methodCall) {
  exists(VarUse use |
    use = methodCall.getReceiver() and
    use.getADef().getSource() instanceof RegExpConstructor and
    methodCall.getCalleeName() = "test"
  )
}

predicate hasLocation(ControlFlowNode node, string file, int startLine) {
  node.getLocation().getFile().getBaseName() = file and
  node.getLocation().getStartLine() = startLine
}
