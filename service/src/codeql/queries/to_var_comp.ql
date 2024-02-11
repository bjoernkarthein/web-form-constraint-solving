/**
 * @name ToVarComp
 * @kind problem
 * @problem.severity warning
 * @id javascript/to-literal-comp
 */

import lib.input_flow

class VariableComparisonFlowConfiguration extends TaintTracking::Configuration {
  VariableComparisonFlowConfiguration() { this = "VariableComparisonFlowConfiguration" }

  override predicate isSource(DataFlow::Node source) {
    hasLocation(source.asExpr(), "FILE", 12345) and // LOCATION
    source.asExpr().toString() = "NAME" // EXPRESSION
  }

  override predicate isSink(DataFlow::Node sink) { isVarComparison(sink.asExpr()) }
}

from VariableComparisonFlowConfiguration cfg, DataFlow::Node source, DataFlow::Node sink
where cfg.hasFlow(source, sink)
select sink.asExpr().getParentExpr(), sink.asExpr().getParentExpr().toString()
