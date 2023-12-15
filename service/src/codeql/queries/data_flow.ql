/**
 * @name Dataflow
 * @kind problem
 * @problem.severity warning
 * @id javascript/data-flow
 */

import input_flow

from DataFlow::SourceNode source, DataFlow::Node node
where
  hasLocation(source.asExpr(), "FILE", 12345) and // LOCATION
  source.asExpr().toString() = "NAME" and // EXPRESSION
  source.flowsTo(node)
select node.asExpr().getParentExpr(), node.asExpr().getParentExpr().toString()
