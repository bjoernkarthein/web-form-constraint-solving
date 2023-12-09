/**
 * @name To Comparisson
 * @kind problem
 * @problem.severity warning
 * @id javascript/to-comp
 */

import input_flow

from ControlFlowNode node, Comparison comp
where
  hasLocation(node, "FILE", 12345) and
  node.getASuccessor*() = comp
select node, node.toString() + " is a user controlled value going to " + comp.toString()
