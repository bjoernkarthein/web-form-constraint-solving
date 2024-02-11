import javascript

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

predicate hasLocation(ControlFlowNode node, string file, int startLine) {
  node.getLocation().getFile().getBaseName() = file and
  node.getLocation().getStartLine() = startLine
}

class RegExpConstructor extends InvokeExpr {
  RegExpConstructor() { this instanceof NewExpr and this.getCallee().toString() = "RegExp" }
}

predicate isRegExpCheck(MethodCallExpr methodCall) {
  methodCall.getReceiver() instanceof RegExpConstructor
  or
  exists(VarUse use |
    use = methodCall.getReceiver() and
    use.getADef().getSource() instanceof RegExpConstructor and
    methodCall.getCalleeName() = "test"
  )
}

predicate isString(Expr expr) {
  expr instanceof StringLiteral
  or
  exists(VarUse use | use = expr and use.getADef().getSource() instanceof StringLiteral)
}

predicate isRegexpLiteral(Expr expr) {
  expr instanceof RegExpLiteral
  or
  exists(VarUse use | use = expr and use.getADef().getSource() instanceof RegExpLiteral)
}

predicate isStringMatch(MethodCallExpr methodCall) {
  (
    isString(methodCall.getArgument(0)) or
    isRegexpLiteral(methodCall.getArgument(0))
  ) and
  methodCall.getCalleeName() = "match"
}

predicate isLiteralComparison(Expr expr) {
  expr.getParent() instanceof Comparison and
  expr.getParent().(Comparison).getRightOperand() instanceof Literal
}

predicate isVarComparison(Expr expr) {
  expr.getParent() instanceof Comparison and
  not expr.getParent().(Comparison).getRightOperand() instanceof Literal
}

predicate isLiteralLengthComparison(Expr expr) {
  expr.getParent() instanceof Comparison and
  expr.getParent().(Comparison).getRightOperand() instanceof NumberLiteral and
  expr.getParent().(Comparison).getLeftOperand() instanceof PropAccess and
  expr.getParent().(Comparison).getLeftOperand().(PropAccess).getPropertyName() = "length"
}

predicate isVarLengthComparison(Expr expr) {
  expr.getParent() instanceof Comparison and
  not expr.getParent().(Comparison).getRightOperand() instanceof NumberLiteral and
  expr.getParent().(Comparison).getLeftOperand() instanceof PropAccess and
  expr.getParent().(Comparison).getLeftOperand().(PropAccess).getPropertyName() = "length"
}
