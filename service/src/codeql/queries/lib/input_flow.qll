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

class DirectLiteralComparison extends Comparison {
  DirectLiteralComparison() { 
    this.getRightOperand() instanceof Literal and not this.getLeftOperand().(PropAccess).getPropertyName() = "length" or
    this.getLeftOperand() instanceof Literal and not this.getRightOperand().(PropAccess).getPropertyName() = "length"
  }
}

class LengthToLiteralComparison extends Comparison {
  LengthToLiteralComparison() { 
    this.getRightOperand() instanceof Literal and this.getLeftOperand().(PropAccess).getPropertyName() = "length" or
    this.getLeftOperand() instanceof Literal and this.getRightOperand().(PropAccess).getPropertyName() = "length"
  }
}

class RegExpConstructor extends InvokeExpr {
  RegExpConstructor() { this instanceof NewExpr and this.getCallee().toString() = "RegExp" }

  Literal getPattern() { result = this.getArgument(0) }
}

class RegExpConstructorOrLiteral extends Expr {
  RegExpConstructorOrLiteral() {
    this instanceof RegExpConstructor or this instanceof RegExpLiteral
  }

  Literal getPattern() {
    this instanceof RegExpConstructor and result = this.(RegExpConstructor).getPattern()
    or
    result = this
  }
}

predicate hasRegExpCheckParent(Expr expr, Expr parent, Expr regex) {
  parent = expr.getParent*() and
  parent instanceof MethodCallExpr and
  (
    (regex instanceof RegExpConstructor or regex instanceof RegExpLiteral) and
    (
      regex = parent.(MethodCallExpr).getReceiver()
      or
      exists(VarUse use |
        use = parent.(MethodCallExpr).getReceiver() and
        regex = use.getADef().getSource() and
        parent.(MethodCallExpr).getCalleeName() = "test"
      )
    )
  )
}

predicate isInRegExpCheck(Expr expr) {
  exists(Expr parent, Expr regex | hasRegExpCheckParent(expr, parent, regex))
}

predicate hasStringMatchParent(Expr expr, Expr parent, Expr matcher) {
  parent = expr.getParent*() and
  parent instanceof MethodCallExpr and
  parent.(MethodCallExpr).getCalleeName() = "match" and
  (
    matcher = parent.(MethodCallExpr).getArgument(0) and
    (matcher instanceof RegExpLiteral or matcher instanceof StringLiteral)
    or
    exists(VarUse use |
      use = parent.(MethodCallExpr).getArgument(0) and
      matcher = use.getADef().getSource() and
      (matcher instanceof RegExpLiteral or matcher instanceof StringLiteral)
    )
  )
}

predicate isInStringMatch(Expr expr) {
  exists(Expr parent, Expr matcher | hasStringMatchParent(expr, parent, matcher))
}

predicate hasLiteralComparisonParent(Expr expr, Expr parent, Literal lit) {
  parent = expr.getParent*() and
  parent instanceof Comparison and
  (lit = parent.(Comparison).getRightOperand() and
  not parent.(Comparison).getLeftOperand().(PropAccess).getPropertyName() = "length" or 
  lit = parent.(Comparison).getLeftOperand() and
  not parent.(Comparison).getRightOperand().(PropAccess).getPropertyName() = "length")
}

predicate isInLiteralComparison(Expr expr) {
  exists(Expr parent, Literal literal | hasLiteralComparisonParent(expr, parent, literal))
}

predicate hasVarComparisonParent(Expr expr, Expr parent, Expr varValue) {
  parent = expr.getParent*() and
  parent instanceof Comparison and
  not parent.(Comparison).getRightOperand() instanceof Literal and
  not parent.(Comparison).getLeftOperand() instanceof Literal and
  (
    varValue = parent.(Comparison).getRightOperand() or
    varValue = parent.(Comparison).getLeftOperand()
  ) and
  not varValue = expr.getParent*()
}

predicate isInVarComparison(Expr expr) {
  exists(Expr parent, Expr e | hasVarComparisonParent(expr, parent, e))
}

predicate hasLiteralLengthComparisonParent(Expr expr, Expr parent, NumberLiteral lit) {
  parent = expr.getParent*() and
  parent instanceof Comparison and
  (lit = parent.(Comparison).getRightOperand() and
  parent.(Comparison).getLeftOperand() instanceof PropAccess and
  parent.(Comparison).getLeftOperand().(PropAccess).getPropertyName() = "length"
  or 
  lit = parent.(Comparison).getLeftOperand() and
  parent.(Comparison).getRightOperand() instanceof PropAccess and
  parent.(Comparison).getRightOperand().(PropAccess).getPropertyName() = "length")
}

predicate isInLiteralLengthComparison(Expr expr) {
  exists(Expr parent, NumberLiteral literal |
    hasLiteralLengthComparisonParent(expr, parent, literal)
  )
}
