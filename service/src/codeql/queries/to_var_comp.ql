/**
 * @name To Variable Comparison
 * @kind problem
 * @problem.severity warning
 * @id javascript/to-variable-comp
 */

import lib.input_flow
import DataFlow

class VariableComparisonFlowConfiguration extends TaintTracking::Configuration {
  VariableComparisonFlowConfiguration() { this = "VariableComparisonFlowConfiguration" }

  override predicate isSource(Node source) {
    hasLocation(source.asExpr(), "FILE", 12345) and // LOCATION
    source.asExpr().toString() = "NAME" // EXPRESSION
  }

  override predicate isSink(Node sink) { isInVarComparison(sink.asExpr()) }
}

from
  VariableComparisonFlowConfiguration cfg, Node source, Node sink, Expr parent,
  Expr varValue
where cfg.hasFlow(source, sink) and hasVarComparisonParent(sink.asExpr(), parent, varValue)
select parent, "Full Comparison: $@, Compared Value: $@", parent, parent.toString(), varValue,
  varValue.toString()
