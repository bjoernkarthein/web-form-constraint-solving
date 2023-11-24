import numpy

from enum import Enum
from lxml.html import Element
from selenium.webdriver import Chrome
from typing import List, Dict

from html_analysis import HTMLConstraints, HTMLElementReference, HTMLInputSpecification
from input_generation import InputGenerator
from utility import InputType, one_line_text_input_types, pre_built_specifications_path, load_file_content, write_to_web_element_by_reference_with_clear, click_web_element_by_reference, start_trace_recording, stop_trace_recording

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

    def __init__(self, web_driver: Chrome, submit_element: Element) -> None:
        self.__driver = web_driver
        self.__generator = InputGenerator()
        self.__magic_value_map: Dict[HTMLElementReference, List[str]] = {}
        self.__submit_element = submit_element

    def find_constraint_candidates(self, html_input_specifications: List[HTMLInputSpecification]) -> None:
        """Try to extract as many constraint candidates as possible from the JavaScript source code for a given input."""
        for specification in html_input_specifications:
            write_to_web_element_by_reference_with_clear(
                self.__driver, specification.reference, self.__magic_value_map.get(specification.reference)[0])

        for specification in html_input_specifications:
            self.__find_constraint_candidates_for_input(specification)

        # TODO

    def set_magic_value_sequence_for_input(self, html_input_reference: HTMLElementReference, grammar: str, formula: str | None, amount=1) -> List[str | int]:
        values = self.__generator.generate_valid_inputs(
            grammar, formula, amount)
        self.__magic_value_map[html_input_reference] = values
        return values

    def __find_constraint_candidates_for_input(self, html_specification: HTMLInputSpecification) -> List[ConstraintCandidate]:
        reference = html_specification.reference
        magic_value_sequence = self.__magic_value_map.get(reference)

        start_trace_recording(
            {'spec': html_specification.get_as_dict(), 'values': magic_value_sequence})

        for magic_value in magic_value_sequence:
            write_to_web_element_by_reference_with_clear(
                self.__driver, html_specification.reference, magic_value)

        click_web_element_by_reference(
            self.__driver, self.__submit_element)

        stop_trace_recording(
            {'spec': html_specification.get_as_dict(), 'values': magic_value_sequence})

    # def get_magic_value_sequence_by_type(self, type: str) -> List[str | int]:
    #     """Get a sequence of 'magic values' for a given HTML input type.

    #     'Magic values' are used to find the important code parts for validation during dynamic analysis of the source code.
    #     """
    #     match type:
    #         case t if t in one_line_text_input_types:
    #             return 'magic_value_why_would_someone_add_this_to_their_code'
    #         case InputType.CHECKBOX.value:
    #             return self.__get_random_checked_states(10)
    #         case InputType.RADIO.value:
    #             return self.__get_random_checked_states(10)
    #         case _:
    #             raise ValueError(
    #                 'The provided type does not match any known html input type')

    # def __get_random_checked_states(self, amount: int) -> List[int]:
    #     """Get a sequence of of 0s and 1s in random order, the length of which is specified by amount."""

    #     checked_states = numpy.ones(amount, dtype=numpy.int0)
    #     checked_states[:amount // 2] = 0
    #     numpy.random.shuffle(checked_states)
    #     return checked_states.tolist()


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
        head, sep, _ = grammar.partition(f'<{option_identifier}> ::= ')
        options = ' | '.join(list_options)
        return f'{head}{sep}{options}'
