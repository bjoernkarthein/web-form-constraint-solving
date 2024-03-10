import re
import time

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
        timeout_seconds: int = 60,
    ) -> List[GeneratedValue]:
        if validity == ValidityEnum.VALID:
            return self.__generate_valid_inputs(
                grammar, formula, amount, timeout_seconds
            )
        else:
            return self.__generate_invalid_inputs(
                grammar, formula, amount, timeout_seconds
            )

    def __generate_valid_inputs(
        self,
        grammar: str,
        formula: str | None,
        amount: int = 1,
        timeout_seconds: int = 60,
    ) -> List[GeneratedValue]:
        print(f"Generating {amount} valid values for")
        print("Grammar:")
        print(grammar)
        print("Formula")
        print(formula)

        values: List[GeneratedValue] = []
        if amount < 1:
            return []

        solver = ISLaSolver(
            grammar,
            formula,
            timeout_seconds=timeout_seconds,
        )

        values = []
        for _ in range(amount):
            try:
                str_value = str(solver.solve())
                values.append(GeneratedValue(str_value, ValidityEnum.VALID))
            except TimeoutError as te:
                print(f"value generation timed out after {te} seconds")
                values.append(GeneratedValue("", ValidityEnum.VALID))
            except Exception as e:
                print(e)
                values.append(GeneratedValue("", ValidityEnum.VALID))

        for v in values:
            print(str(v))
        return values

    def __generate_invalid_inputs(
        self,
        grammar: str,
        formula: str | None,
        amount: int = 1,
        timeout_seconds: int = 60,
    ) -> List[GeneratedValue]:
        print(f"Generating {amount} invalid values for")
        print("Grammar:")
        print(grammar)
        print("Formula")
        print(formula)

        if formula is not None:
            negated_formula = f"not ({formula})"
            values = self.__generate_valid_inputs(
                grammar, negated_formula, amount, timeout_seconds
            )
            return list(
                map(lambda v: GeneratedValue(v.value, ValidityEnum.INVALID), values)
            )

        return self.__generate_invalid_values_for_non_existent_formula(
            grammar, amount, timeout_seconds
        )

    def __generate_invalid_values_for_non_existent_formula(
        self, grammar: str, amount: int = 1, timeout_seconds: int = 60
    ) -> List[GeneratedValue]:
        values: List[GeneratedValue] = []
        grammar_terminals = self.__get_terminal_characters_from_grammar(grammar)

        for _ in range(amount):
            try:
                invalid_value = self.__look_for_value_not_in_grammar(
                    grammar, grammar_terminals, timeout_seconds
                )
                values.append(invalid_value)
            except TimeoutError as te:
                print(f"value generation timed out after {te} seconds")
                values.append(GeneratedValue("", ValidityEnum.VALID))
            except Exception as e:
                print(e)
                values.append(GeneratedValue("", ValidityEnum.INVALID))

        for v in values:
            print(str(v))
        return values

    def __look_for_value_not_in_grammar(
        self, grammar: str, grammar_terminals: Set[str], timeout_seconds: int = 60
    ) -> None:
        start_time = int(time.time())
        last_value = None

        while int(time.time()) - start_time < timeout_seconds:
            solver = ISLaSolver(
                grammar,
                timeout_seconds=timeout_seconds,
            )
            str_value = str(solver.solve())
            mutator = ValueMutator(str_value, grammar_terminals)
            last_value = mutator.mutate(last_value)

            if not solver.check(last_value):
                value = GeneratedValue(last_value, ValidityEnum.INVALID)
                return value

        print(f"value generation timed out after {timeout_seconds} seconds")
        return GeneratedValue("", ValidityEnum.INVALID)

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
