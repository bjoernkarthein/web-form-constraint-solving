import time

from enum import Enum
from lxml.html import Element
from selenium.webdriver import Chrome
from typing import List, Dict

from html_analysis import HTMLConstraints, HTMLElementReference, HTMLInputSpecification
from input_generation import InputGenerator
from utility import *

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

    def set_magic_value_sequence_for_input(self, html_specification: HTMLInputSpecification, grammar: str, formula: str | None, amount=1) -> List[str | int]:
        html_input_reference = html_specification.reference

        # allows to make the magic values more diverse for inputs that are not required instead of only getting empty strings
        required = html_specification.contraints.type in one_line_text_input_types + \
            [InputType.DATE.value, InputType.MONTH.value]

        values = self.__generator.generate_valid_inputs(
            grammar, formula, amount, required)
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

            record_trace(Action.ATTEMPT_SUBMIT)
            click_web_element_by_reference(
                self.__driver, self.__submit_element)

        stop_trace_recording(
            {'spec': html_specification.get_as_dict(), 'values': magic_value_sequence})


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
            case t if t in binary_input_types:
                return self.__add_constraints_for_checkbox(html_input_specification.contraints.required)
            case InputType.MONTH.value:
                return self.__add_constraints_for_month(html_input_specification.contraints, use_datalist_options)
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

    def __add_constraints_for_checkbox(self, required: str) -> (str, str | None):
        grammar = load_file_content(
            f'{pre_built_specifications_path}/checkbox/checkbox.bnf')
        formula = None

        if required is not None:
            grammar = load_file_content(
                f'{pre_built_specifications_path}/checkbox/checkbox_required.bnf')

        return grammar, formula

    def __add_constraints_for_month(self, html_constraints: HTMLConstraints, use_datalist_options=False) -> (str, str | None):
        grammar = load_file_content(
            f'{pre_built_specifications_path}/month/month.bnf')
        formula = load_file_content(
            f'{pre_built_specifications_path}/month/month.isla')

        if use_datalist_options and html_constraints.list is not None:
            grammar = self.__replace_by_list_options(
                grammar, 'yearmonth', html_constraints.list)
        if html_constraints.required is not None:
            formula = self.__add_to_formula('str.len(<start>) > 0',
                                            formula, LogicalOperator.AND)
        if html_constraints.min is not None:
            [year_str, month_str] = html_constraints.min.split('-')
            year = int(year_str)
            month = int(month_str)
            formula = self.__add_to_formula(f'str.to.int(<year>) >= {year} and str.to.int(<year>) + str.to.int(<month>) >= {year + month}',
                                            formula, LogicalOperator.AND)
        if html_constraints.max is not None:
            [year_str, month_str] = html_constraints.max.split('-')
            year = int(year_str)
            month = int(month_str)
            formula = self.__add_to_formula(f'str.to.int(<year>) <= {year} and str.to.int(<year>) + str.to.int(<month>) <= {year + month}',
                                            formula, LogicalOperator.AND)
        # TODO: step not working because can not set calculation in parantheses
        # if html_constraints.step is not None:
        #     formula = self.__add_to_formula(f'(str.to.int(<year>) + str.to.int(<month>)) mod {html_constraints.step} = 0',
        #                                     formula, LogicalOperator.AND)

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
