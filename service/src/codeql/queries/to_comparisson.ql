/**
 * @name To Comparisson
 * @kind problem
 * @problem.severity warning
 * @id javascript/to-comp
 */

import lib.input_flow

from ControlFlowNode node, Comparison comp
where
  hasLocation(node, "FILE", 12345) and // LOCATION
  node.toString() = "NAME" and // EXPRESSION
  node.getASuccessor*() = comp and
  (comp.getLeftOperand() = node or comp.getRightOperand() = node)
select comp, ""
