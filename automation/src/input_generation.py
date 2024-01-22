from isla.solver import ISLaSolver
from typing import List

from enum import Enum

from mutation import ValueMutator


class ValidityEnum(Enum):
    VALID = "valid"
    INVALID = "invalid"


class GeneratedValue:
    def __init__(self, value: str, validtity: ValidityEnum) -> None:
        self.__value = value
        self.__validity = validtity

    @property
    def value(self) -> str:
        return self.__value

    @property
    def validity(self) -> ValidityEnum:
        return self.__validity

    def __str__(self) -> str:
        return f'("{self.value}",{self.validity.value})'


class InputGenerator:
    def generate_inputs(
        self,
        grammar: str,
        formula: str,
        validity: ValidityEnum = ValidityEnum.VALID,
        amount: int = 1,
    ) -> List[GeneratedValue]:
        if validity == ValidityEnum.VALID:
            return self.__generate_valid_inputs(grammar, formula, amount)
        else:
            return self.__generate_invalid_inputs(grammar, formula, amount)

    def __generate_valid_inputs(
        self, grammar: str, formula: str | None, amount: int = 1
    ) -> List[GeneratedValue]:
        values: List[GeneratedValue] = []
        if amount < 1:
            return []

        solver = ISLaSolver(grammar, formula)

        try:
            for _ in range(amount):
                str_value = str(solver.solve())
                value = GeneratedValue(str_value, ValidityEnum.VALID)
                values.append(value)
            return values
        except Exception as e:
            # TODO
            print(e)
            return []

    # TODO: Needs to be tested a lot to see if it works reliably
    def __generate_invalid_inputs(
        self, grammar: str, formula: str | None, amount: int = 1
    ) -> List[GeneratedValue]:
        if formula is not None:
            negated_formula = f"not ({formula})"
            values = self.__generate_valid_inputs(grammar, negated_formula, amount)
            return list(
                map(lambda v: GeneratedValue(v.value, ValidityEnum.INVALID), values)
            )

        return self.__generate_invalid_values_for_non_existent_formula(grammar, amount)

    def __generate_invalid_values_for_non_existent_formula(
        self, grammar: str, amount: int = 1
    ) -> List[GeneratedValue]:
        values = []

        for _ in range(amount):
            found_invalid_value = False

            last_value = None
            for _ in range(100):  # TODO: think of a good number here
                solver = ISLaSolver(grammar)
                str_value = str(solver.solve())
                # TODO: What is a good number for mutations?
                mutator = ValueMutator(str_value, 5)
                last_value = mutator.mutate(last_value)

                if not solver.check(last_value):
                    value = GeneratedValue(last_value, ValidityEnum.INVALID)
                    values.append(value)
                    found_invalid_value = True
                    break

            if not found_invalid_value:
                # TODO: What if I don't find something invalid
                values.append(GeneratedValue("", ValidityEnum.INVALID))
