/**
 * @name To Comparisson
 * @kind problem
 * @problem.severity warning
 * @id javascript/to-comp
 */

import lib.input_flow

class ComparisonFlowConfiguration extends TaintTracking::Configuration {
  ComparisonFlowConfiguration() { this = "ComparisonFlowConfiguration" }

  override predicate isSource(DataFlow::Node source) {
    hasLocation(source.asExpr(), "FILE", 12345) // LOCATION
  }

  override predicate isSink(DataFlow::Node sink) { isLiteralComparison(sink.asExpr()) }
}

from ComparisonFlowConfiguration cfg, DataFlow::Node source, DataFlow::Node sink
where cfg.hasFlow(source, sink)
select sink, sink.asExpr().getParentExpr().toString()
