/**
 * @name To Variable Length Comparison
 * @kind problem
 * @problem.severity warning
 * @id javascript/to-var-length-comp
 */

import lib.input_flow

class VarLengthCompFlowConfiguration extends TaintTracking::Configuration {
  VarLengthCompFlowConfiguration() { this = "VarLengthCompFlowConfiguration" }

  override predicate isSource(DataFlow::Node source) {
    hasLocation(source.asExpr(), "FILE", 12345) // LOCATION
  }

  override predicate isSink(DataFlow::Node sink) { isVarLengthComparison(sink.asExpr()) }
}

from VarLengthCompFlowConfiguration cfg, DataFlow::Node source, DataFlow::Node sink
where cfg.hasFlow(source, sink)
select sink, sink.asExpr().getParentExpr().toString()
