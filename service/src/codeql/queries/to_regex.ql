/**
 * @name To Regex Test
 * @kind problem
 * @problem.severity warning
 * @id javascript/to-regex
 */

import lib.input_flow
import DataFlow

class RegExFlowConfiguration extends TaintTracking::Configuration {
  RegExFlowConfiguration() { this = "RegExFlowConfiguration" }

  override predicate isSource(Node source) {
    hasLocation(source.asExpr(), "FILE", 12345) and // LOCATION
    source.asExpr().toString() = "NAME" // EXPRESSION
  }

  override predicate isSink(Node sink) { isInRegExpCheck(sink.asExpr()) }
}

from
  RegExFlowConfiguration cfg, Node source, Node sink, Expr parent,
  RegExpConstructorOrLiteral regex
where cfg.hasFlow(source, sink) and hasRegExpCheckParent(sink.asExpr(), parent, regex)
select parent, "Whole Test: $@, Pattern: $@", parent, parent.toString(), regex.getPattern(),
  regex.getPattern().toString()
