from isla.solver import ISLaSolver
from typing import List

from mutation import ValueMutator


class InputGenerator:
    def generate_valid_inputs(self, grammar: str, formula: str | None, amount: int = 1) -> List[str]:
        values = []
        if amount < 1:
            return values

        solver = ISLaSolver(grammar, formula)

        try:
            for _ in range(amount):
                value = str(solver.solve())
                values.append(value)
            return values
        except Exception as e:
            # TODO
            print(e)
            return []

    def generate_invalid_inputs(self, grammar: str, formula: str | None, amount: int = 1) -> List[str]:
        if formula is not None:
            negated_formula = f'not ({formula})'
            return self.generate_invalid_inputs(grammar, negated_formula, amount)

        return self.__generate_invalid_values_for_non_existent_formula(grammar, amount)

    def __generate_invalid_values_for_non_existent_formula(self, grammar: str, amount: int = 1) -> List[str]:
        values = []

        for _ in range(amount):
            found_invalid_value = False

            last_value = None
            for _ in range(100):  # TODO: think of a good number here
                solver = ISLaSolver(grammar)
                value = str(solver.solve())
                # TODO: What is a good number for mutations?
                mutator = ValueMutator(value, 5)
                last_value = mutator.mutate(last_value)

                if not solver.check(value):
                    values.append(value)
                    found_invalid_value = True
                    break

            if not found_invalid_value:
                # TODO: What if I don't find something invalid
                values.append('')
