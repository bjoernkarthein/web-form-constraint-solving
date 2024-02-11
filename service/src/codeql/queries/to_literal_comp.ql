/**
 * @name ToLitComp
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

  override predicate isSink(DataFlow::Node sink) { isLiteralComparison(sink.asExpr()) }
}

from LiteralComparisonFlowConfiguration cfg, DataFlow::Node source, DataFlow::Node sink
where cfg.hasFlow(source, sink)
select sink.asExpr().getParentExpr(), sink.asExpr().getParentExpr().toString()
