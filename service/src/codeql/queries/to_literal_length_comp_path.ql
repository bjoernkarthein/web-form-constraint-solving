/**
 * @name To Literal Length Comparison
 * @kind path-problem
 * @problem.severity warning
 * @id javascript/to-literal-length-comp-path
 */

import lib.input_flow
import DataFlow
import DataFlow::PathGraph

class ComparisonFlowConfiguration extends TaintTracking::Configuration {
  ComparisonFlowConfiguration() { this = "ComparisonFlowConfiguration" }

  override predicate isSource(Node source) {
    hasLocation(source.asExpr(), "FILE", 12345) and // LOCATION
    source.asExpr().toString() = "NAME" // EXPRESSION
  }

  override predicate isSink(Node sink) { sink.asExpr() instanceof LengthToLiteralComparison }

  override predicate isAdditionalTaintStep(Node pred, Node succ) {
    exists(BinaryExpr bin |
      succ = bin.flow() and
      (pred = bin.getLeftOperand().flow()
      or
      pred = bin.getRightOperand().flow())
    )
  }
}

from
  ComparisonFlowConfiguration cfg, PathNode source, PathNode sink
where cfg.hasFlowPath(source, sink)
select sink.getNode(), source, sink, "here"