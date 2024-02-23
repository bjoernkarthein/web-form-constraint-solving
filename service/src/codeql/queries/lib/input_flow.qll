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

predicate hasRegExpCheckParent(Expr expr, Expr parent, RegExpConstructor regex) {
  parent = expr.getParent*() and
  parent instanceof MethodCallExpr and
  (regex = parent.(MethodCallExpr).getReceiver() or
  exists(VarUse use |
    use = parent.(MethodCallExpr).getReceiver() and
    regex = use.getADef().getSource() and
    parent.(MethodCallExpr).getCalleeName() = "test"
  ))
}

predicate isInRegExpCheck(Expr expr) {
  exists (Expr parent, RegExpConstructor regex |
    hasRegExpCheckParent(expr, parent, regex)
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

predicate hasStringMatchParent(Expr expr, Expr parent, Expr matcher) {
  parent = expr.getParent*() and
  parent instanceof MethodCallExpr and
  matcher = parent.(MethodCallExpr).getArgument(0) and
  (isString(matcher) or isRegexpLiteral(matcher)) and
  parent.(MethodCallExpr).getCalleeName() = "match"
}

predicate isInStringMatch(Expr expr) {
  exists (Expr parent, Expr matcher |
    hasStringMatchParent(expr, parent, matcher)
  )
}

predicate hasLiteralComparisonParent(Expr expr, Expr parent) {
  parent = expr.getParent*() and
  parent instanceof Comparison and
  parent.(Comparison).getRightOperand() instanceof Literal
}

predicate isInLiteralComparison(Expr expr) {
  exists (Expr parent |
    hasLiteralComparisonParent(expr, parent)
  )
}

predicate hasVarComparisonParent(Expr expr, Expr parent) {
  parent = expr.getParent*() and
  parent instanceof Comparison and
  not parent.(Comparison).getRightOperand() instanceof Literal
}

predicate isInVarComparison(Expr expr) {
  exists (Expr parent |
    hasVarComparisonParent(expr, parent)
  )
}

predicate hasLiteralLengthComparisonParent(Expr expr, Expr parent) {
  parent = expr.getParent*() and
  parent instanceof Comparison and
  parent.(Comparison).getRightOperand() instanceof NumberLiteral and
  parent.(Comparison).getLeftOperand() instanceof PropAccess and
  parent.(Comparison).getLeftOperand().(PropAccess).getPropertyName() = "length"
}

predicate isInLiteralLengthComparison(Expr expr) {
  exists (Expr parent |
    hasLiteralLengthComparisonParent(expr, parent)
  )
}

predicate hasVarLengthComparisonParent(Expr expr, Expr parent) {
  parent = expr.getParent*() and
  parent instanceof Comparison and
  not parent.(Comparison).getRightOperand() instanceof NumberLiteral and
  parent.(Comparison).getLeftOperand() instanceof PropAccess and
  parent.(Comparison).getLeftOperand().(PropAccess).getPropertyName() = "length"
}

predicate isInVarLengthComparison(Expr expr) {
  exists(Expr parent |
    hasVarLengthComparisonParent(expr, parent)
  )
}
