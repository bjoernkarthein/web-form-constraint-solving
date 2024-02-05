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
    hasLocation(source.asExpr(), "FILE", 12345) // LOCATION
  }

  override predicate isSink(DataFlow::Node sink) { isLiteralComparison(sink.asExpr()) }
}

from LiteralComparisonFlowConfiguration cfg, DataFlow::Node source, DataFlow::Node sink
where cfg.hasFlow(source, sink)
select sink, sink.asExpr().getParentExpr().toString()
