/**
 * @name ToLitLengthComp
 * @kind problem
 * @problem.severity warning
 * @id javascript/to-literal-length-comp
 */

import lib.input_flow

class LiteralLengthCompFlowConfiguration extends TaintTracking::Configuration {
  LiteralLengthCompFlowConfiguration() { this = "LiteralLengthCompFlowConfiguration" }

  override predicate isSource(DataFlow::Node source) {
    hasLocation(source.asExpr(), "FILE", 12345) and // LOCATION
    source.asExpr().toString() = "NAME" // EXPRESSION
  }

  override predicate isSink(DataFlow::Node sink) { isLiteralLengthComparison(sink.asExpr()) }
}

from LiteralLengthCompFlowConfiguration cfg, DataFlow::Node source, DataFlow::Node sink
where cfg.hasFlow(source, sink)
select sink.asExpr().getParentExpr(), sink.asExpr().getParentExpr().toString()
