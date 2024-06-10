/**
 * @name To String Match
 * @kind problem
 * @problem.severity warning
 * @id javascript/to-string-match
 */

import lib.input_flow
import DataFlow

class ToStringMatchFlowConfiguration extends TaintTracking::Configuration {
  ToStringMatchFlowConfiguration() { this = "ToStringMatchFlowConfiguration" }

  override predicate isSource(Node source) {
    hasLocation(source.asExpr(), "FILE", 12345) and // LOCATION
    source.asExpr().toString() = "NAME" // EXPRESSION
  }

  override predicate isSink(Node sink) { isInStringMatch(sink.asExpr()) }
}

from
  ToStringMatchFlowConfiguration cfg, Node source, Node sink, Expr parent,
  Expr matcher
where cfg.hasFlow(source, sink) and hasStringMatchParent(sink.asExpr(), parent, matcher)
select parent, "Whole Test: $@, Pattern: $@", parent, parent.toString(), matcher, matcher.toString()
