/**
 * @name To Length Comparison
 * @kind problem
 * @problem.severity warning
 * @id javascript/to-length-comp
 */

import lib.input_flow

class LengthCompFlowConfiguration extends TaintTracking::Configuration {
  LengthCompFlowConfiguration() { this = "LengthCompFlowConfiguration" }

  override predicate isSource(DataFlow::Node source) {
    hasLocation(source.asExpr(), "FILE", 12345) // LOCATION
  }

  override predicate isSink(DataFlow::Node sink) { isLiteralLengthComparison(sink.asExpr()) }
}

from LengthCompFlowConfiguration cfg, DataFlow::Node source, DataFlow::Node sink
where cfg.hasFlow(source, sink)
select sink, sink.asExpr().getParentExpr().toString()
