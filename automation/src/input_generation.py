from isla.solver import ISLaSolver
from typing import List


class InputGenerator:
    def __init__(self) -> None:
        self.required_string = 'str.len(<start>) > 0'

    def generate_valid_inputs(self, grammar: str, formula: str | None, amount: int = 1, required=False) -> List[str]:
        if amount < 1:
            return []

        if required and not self.required_string in formula:
            formula = f'{formula} and {self.required_string}'

        solver = ISLaSolver(grammar, formula)

        try:
            values = []
            for _ in range(amount):
                value = str(solver.solve())
                values.append(value)
            return values
        except Exception as e:
            # TODO
            print(e)
            return []
