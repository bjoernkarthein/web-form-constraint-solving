/**
 * @name To Literal Length Comparison
 * @kind problem
 * @problem.severity warning
 * @id javascript/to-literal-length-comp
 */

import lib.input_flow
import DataFlow

class LiteralLengthCompFlowConfiguration extends TaintTracking::Configuration {
  LiteralLengthCompFlowConfiguration() { this = "LiteralLengthCompFlowConfiguration" }

  override predicate isSource(Node source) {
    hasLocation(source.asExpr(), "FILE", 12345) and // LOCATION
    source.asExpr().toString() = "NAME" // EXPRESSION
  }

  override predicate isSink(Node sink) { isInLiteralLengthComparison(sink.asExpr()) }
}

from
  LiteralLengthCompFlowConfiguration cfg, Node source, Node sink, Expr parent,
  NumberLiteral lit
where cfg.hasFlow(source, sink) and hasLiteralLengthComparisonParent(sink.asExpr(), parent, lit)
select parent, "Full Comparison: $@, Compared Value: $@", parent, parent.toString(), lit,
  lit.toString()
