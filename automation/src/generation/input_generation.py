import re

from enum import Enum
from isla.solver import ISLaSolver
from typing import Dict, List, Set

from src.generation.mutation import ValueMutator


class ValidityEnum(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"


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

    def get_as_dict(self) -> Dict[str, ValidityEnum | str]:
        return {"validity": self.__validity, "value": self.__value}

    def __str__(self) -> str:
        return f"(validity: {self.validity}, value: {self.value})"


class InputGenerator:
    def generate_inputs(
        self,
        grammar: str,
        formula: str | None = None,
        validity: ValidityEnum = ValidityEnum.VALID,
        amount: int = 1,
    ) -> List[GeneratedValue]:
        print(f"generating {amount} {validity.value} inputs")
        print(grammar)
        print(formula)

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
                print(f"generated '{str_value}'")
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
        grammar_terminals = self.__get_terminal_characters_from_grammar(grammar)

        for _ in range(amount):
            found_invalid_value = False

            last_value = None
            for _ in range(100):  # TODO: think of a good number here
                solver = ISLaSolver(grammar)
                str_value = str(solver.solve())
                # TODO: What is a good number for mutations?
                mutator = ValueMutator(str_value, grammar_terminals)
                last_value = mutator.mutate(last_value)

                if not solver.check(last_value):
                    print(f"generated '{last_value}'")
                    value = GeneratedValue(last_value, ValidityEnum.INVALID)
                    values.append(value)
                    found_invalid_value = True
                    break

            if not found_invalid_value:
                # TODO: What if I don't find something invalid?
                values.append(GeneratedValue("", ValidityEnum.INVALID))

    # TODO: Can this be optimized?
    def __get_terminal_characters_from_grammar(self, grammar: str) -> Set[str]:
        result = []
        quoted_terminals = re.findall(r'("[^"]*")', grammar)
        terminals = list(map(lambda t: t[1:-1], quoted_terminals))
        seperated_terminals = list(map(lambda t: [c for c in t], terminals))
        for terminal in seperated_terminals:
            if len(terminal) > 0:
                result.extend(terminal)
            else:
                result.append("")

        return set(result)
