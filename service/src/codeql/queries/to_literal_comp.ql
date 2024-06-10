/**
 * @name To Literal Comparison
 * @kind problem
 * @problem.severity warning
 * @id javascript/to-literal-comp
 */

import lib.input_flow
import DataFlow

class LiteralComparisonFlowConfiguration extends TaintTracking::Configuration {
  LiteralComparisonFlowConfiguration() { this = "LiteralComparisonFlowConfiguration" }

  override predicate isSource(Node source) {
    hasLocation(source.asExpr(), "FILE", 12345) and // LOCATION
    source.asExpr().toString() = "NAME" // EXPRESSION
  }

  override predicate isSink(Node sink) { isInLiteralComparison(sink.asExpr()) }
}

from
  LiteralComparisonFlowConfiguration cfg, Node source, Node sink, Expr parent,
  Literal lit
where cfg.hasFlow(source, sink) and hasLiteralComparisonParent(sink.asExpr(), parent, lit)
select parent, "Full Comparison: $@, Compared Value: $@", parent, parent.toString(), lit,
  lit.toString()
