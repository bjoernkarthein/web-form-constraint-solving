/**
 * @name Dataflow
 * @kind problem
 * @problem.severity warning
 * @id javascript/data-flow
 */

import lib.input_flow

class InputFlowConfiguration extends TaintTracking::Configuration {
  InputFlowConfiguration() { this = "InputFlowConfiguration" }

  override predicate isSource(DataFlow::Node source) {
    hasLocation(source.asExpr(), "FILE", 12345) and // LOCATION
    source.asExpr().toString() = "NAME" // EXPRESSION
  }

  override predicate isSink(DataFlow::Node sink) { sink.asExpr().getLocation().getStartLine() > 0 }
}

from InputFlowConfiguration cfg, DataFlow::Node source, DataFlow::Node sink
where cfg.hasFlow(source, sink)
select sink, sink.toString()
