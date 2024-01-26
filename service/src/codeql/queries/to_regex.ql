/**
 * @name To RegEx
 * @kind problem
 * @problem.severity warning
 * @id javascript/to-regex
 */

import lib.input_flow

class InputFlowConfiguration extends TaintTracking::Configuration {
  InputFlowConfiguration() { this = "InputFlowConfiguration" }

  override predicate isSource(DataFlow::Node source) {
    hasLocation(source.asExpr(), "FILE", 12345) and // LOCATION
    source.asExpr().toString() = "NAME" // EXPRESSION
  }

  override predicate isSink(DataFlow::Node sink) { isRegExpCheck(sink.asExpr().getParentExpr()) }
}

from InputFlowConfiguration cfg, DataFlow::Node source, DataFlow::Node sink
where cfg.hasFlow(source, sink)
select sink, sink.asExpr().getParentExpr().toString()
