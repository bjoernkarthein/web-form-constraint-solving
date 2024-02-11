/**
 * @name ToStringMatch
 * @kind problem
 * @problem.severity warning
 * @id javascript/to-string-match
 */

import lib.input_flow

class ToStringMatchFlowConfiguration extends TaintTracking::Configuration {
  ToStringMatchFlowConfiguration() { this = "ToStringMatchFlowConfiguration" }

  override predicate isSource(DataFlow::Node source) {
    hasLocation(source.asExpr(), "FILE", 12345) and // LOCATION
    source.asExpr().toString() = "NAME" // EXPRESSION
  }

  override predicate isSink(DataFlow::Node sink) { isStringMatch(sink.asExpr().getParentExpr()) }
}

from ToStringMatchFlowConfiguration cfg, DataFlow::Node source, DataFlow::Node sink
where cfg.hasFlow(source, sink)
select sink.asExpr().getParentExpr(), sink.asExpr().getParentExpr().toString()
