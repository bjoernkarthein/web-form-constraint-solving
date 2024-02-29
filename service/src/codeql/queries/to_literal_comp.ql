/**
 * @name To Literal Comparison
 * @kind problem
 * @problem.severity warning
 * @id javascript/to-literal-comp
 */

import lib.input_flow

class LiteralComparisonFlowConfiguration extends TaintTracking::Configuration {
  LiteralComparisonFlowConfiguration() { this = "LiteralComparisonFlowConfiguration" }

  override predicate isSource(DataFlow::Node source) {
    hasLocation(source.asExpr(), "FILE", 12345) and // LOCATION
    source.asExpr().toString() = "NAME" // EXPRESSION
  }

  override predicate isSink(DataFlow::Node sink) { isInLiteralComparison(sink.asExpr()) }
}

from
  LiteralComparisonFlowConfiguration cfg, DataFlow::Node source, DataFlow::Node sink, Expr parent,
  Literal lit
where cfg.hasFlow(source, sink) and hasLiteralComparisonParent(sink.asExpr(), parent, lit)
select parent, "Full Comparison: $@, Compared Value: $@", parent, parent.toString(), lit,
  lit.toString()
