/**
 * @name ToVarLengthComp
 * @kind problem
 * @problem.severity warning
 * @id javascript/to-var-length-comp
 */

import lib.input_flow

class VarLengthCompFlowConfiguration extends TaintTracking::Configuration {
  VarLengthCompFlowConfiguration() { this = "VarLengthCompFlowConfiguration" }

  override predicate isSource(DataFlow::Node source) {
    hasLocation(source.asExpr(), "FILE", 12345) and // LOCATION
    source.asExpr().toString() = "NAME" // EXPRESSION
  }

  override predicate isSink(DataFlow::Node sink) { isVarLengthComparison(sink.asExpr()) }
}

from VarLengthCompFlowConfiguration cfg, DataFlow::Node source, DataFlow::Node sink
where cfg.hasFlow(source, sink)
select sink.asExpr().getParentExpr(), sink.asExpr().getParentExpr().toString()
