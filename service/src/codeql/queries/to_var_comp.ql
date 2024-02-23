/**
 * @name To Variable Comparison
 * @kind problem
 * @problem.severity warning
 * @id javascript/to-variable-comp
 */

import lib.input_flow

class VariableComparisonFlowConfiguration extends TaintTracking::Configuration {
  VariableComparisonFlowConfiguration() { this = "VariableComparisonFlowConfiguration" }

  override predicate isSource(DataFlow::Node source) {
    hasLocation(source.asExpr(), "FILE", 12345) and // LOCATION
    source.asExpr().toString() = "NAME" // EXPRESSION
  }

  override predicate isSink(DataFlow::Node sink) { isInVarComparison(sink.asExpr()) }
}

from VariableComparisonFlowConfiguration cfg, DataFlow::Node source, DataFlow::Node sink, Expr parent
where cfg.hasFlow(source, sink) and hasVarComparisonParent(sink.asExpr(), parent)
select parent, parent.toString()
