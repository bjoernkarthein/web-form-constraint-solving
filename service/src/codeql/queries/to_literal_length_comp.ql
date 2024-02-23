/**
 * @name ToLitLengthComp
 * @kind problem
 * @problem.severity warning
 * @id javascript/to-literal-length-comp
 */

import lib.input_flow

class LiteralLengthCompFlowConfiguration extends TaintTracking::Configuration {
  LiteralLengthCompFlowConfiguration() { this = "LiteralLengthCompFlowConfiguration" }

  override predicate isSource(DataFlow::Node source) {
    hasLocation(source.asExpr(), "FILE", 12345) and // LOCATION
    source.asExpr().toString() = "NAME" // EXPRESSION
  }

  override predicate isSink(DataFlow::Node sink) { isInLiteralLengthComparison(sink.asExpr()) }
}

from LiteralLengthCompFlowConfiguration cfg, DataFlow::Node source, DataFlow::Node sink, Expr parent
where cfg.hasFlow(source, sink) and hasLiteralLengthComparisonParent(sink.asExpr(), parent)
select parent, parent.toString()
