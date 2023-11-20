import numpy

from enum import Enum
from selenium.webdriver import Chrome
from typing import List, Literal

from html_analysis import HTMLConstraints, HTMLElementReference, HTMLInputSpecification
from utility import load_file_content, InputType, one_line_text_input_types, pre_built_specifications_path

"""
Constraint Extraction module

Provides classes to define constraint candidates, extract candidates from inputs and
build a specification for these inputs.
"""


class ConstraintCandidate:
    def __init__(self) -> None:
        pass


class ConstraintCandidateFinder:
    """ConstraintCandidateFinder class

    Provides methods to identify constraint candidates for a specific input of the form.
    """

    def __init__(self, web_driver: Chrome) -> None:
        self.__driver = web_driver

    def find_constraint_candidates_for_input(self, html_input_specification: HTMLInputSpecification) -> List[ConstraintCandidate]:
        """Try to extract as many constraint candidates as possible from the source code for a given input."""

        magic_values = self.get_magic_value_sequence_by_type(
            html_input_specification.contraints.type)

        print(magic_values)

        return []

    def get_magic_value_sequence_by_type(self, type: str) -> List[str]:
        """Get a sequence of 'magic values' for a given HTML input type.

        'Magic values' are used to find the important code parts for validation during dynamic analysis of the source code.
        """
        match type:
            case t if t in one_line_text_input_types:
                return 'magic_value_why_would_someone_add_this_to_their_code'
            case InputType.CHECKBOX.value:
                return self.__get_random_checked_states(10)
            case InputType.RADIO.value:
                return self.__get_random_checked_states(10)
            case _:
                raise ValueError(
                    'The provided type does not match any known html input type')

    def __get_random_checked_states(self, amount: int) -> List[int]:
        """Get a sequence of of 0s and 1s in random order, the length of which is specified by amount."""

        checked_states = numpy.ones(amount, dtype=numpy.int0)
        checked_states[:amount // 2] = 0
        numpy.random.shuffle(checked_states)
        return checked_states.tolist()


class LogicalOperator(Enum):
    AND = "and"
    OR = "or"
    NOT = "not"
    XOR = "xor"
    IMPLIES = "implies"


class SpecificationBuilder:
    def __init__(self) -> None:
        pass

    def create_specification_for_html_validation(self, html_input_specification: HTMLInputSpecification, use_datalist_options=False) -> (str, str | None):
        match html_input_specification.contraints.type:
            case t if t in one_line_text_input_types:
                return self.__add_constraints_for_one_line_text(html_input_specification.contraints, use_datalist_options)
            case None:
                return self.__add_constraints_for_one_line_text(html_input_specification.contraints, use_datalist_options)
            case _:
                raise ValueError(
                    'The provided type does not match any known html input type')

    def __add_constraints_for_one_line_text(self, html_constraints: HTMLConstraints, use_datalist_options: bool) -> (str, str | None):
        grammar = load_file_content(
            f'{pre_built_specifications_path}/one-line-text/one-line-text.bnf')
        formula = None

        if use_datalist_options and html_constraints.list is not None:
            grammar = self.__replace_by_list_options(
                grammar, 'one-line-text', html_constraints.list)
        if html_constraints.required is not None and html_constraints.minlength is None:
            formula = self.__add_to_formula('str.len(<start>) > 0',
                                            formula, LogicalOperator.AND)
        if html_constraints.required is not None and html_constraints.minlength is not None:
            formula = self.__add_to_formula(
                f'str.len(<start>) >= {html_constraints.minlength}', formula, LogicalOperator.AND)
        if html_constraints.maxlength is not None:
            formula = self.__add_to_formula(
                f'str.len(<start>) <= {html_constraints.maxlength}', formula, LogicalOperator.AND)
        if html_constraints.pattern is not None:
            # TODO
            pass

        return grammar, formula

    def __add_to_formula(self, additional_part: str, formula: str, operator: LogicalOperator) -> str:
        if formula is None or len(formula) == 0:
            return additional_part
        else:
            return f'{formula} {operator.value} {additional_part}'

    def __replace_by_list_options(self, grammar: str, option_identifier: str, list_options: List[str]) -> str:
        head, sep, tail = grammar.partition(f'<{option_identifier}> ::= ')
        options = ' | '.join(list_options)
        return f'{head}{sep}{options}'
