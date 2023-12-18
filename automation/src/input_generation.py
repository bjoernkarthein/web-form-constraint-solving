from isla.solver import ISLaSolver
from typing import List


class InputGenerator:
    def generate_valid_inputs(self, grammar: str, formula: str | None, amount: int = 1) -> List[str]:
        if amount < 1:
            return []

        print(grammar)
        print(formula)
        solver = ISLaSolver(grammar, formula)

        # try:
        values = []
        for _ in range(amount):
            value = str(solver.solve())
            values.append(value)
        return values
        # except Exception as e:
        #     # TODO
        #     print(e)
        #     return []
