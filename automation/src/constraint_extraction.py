import time

from enum import Enum
from lxml.html import Element
from selenium.webdriver import Chrome
from typing import List, Dict

from html_analysis import HTMLConstraints, HTMLElementReference, HTMLInputSpecification, HTMLRadioGroupSpecification
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

    def find_constraint_candidates(self, html_input_specifications: List[HTMLInputSpecification | HTMLRadioGroupSpecification]) -> None:
        """Try to extract as many constraint candidates as possible from the JavaScript source code for a given input."""
        for specification in html_input_specifications:
            key = specification.reference if isinstance(
                specification, HTMLInputSpecification) else specification.name

            magic_values = self.__magic_value_map.get(key)
            if magic_values is None or len(magic_values) == 0:
                continue

            if isinstance(specification, HTMLRadioGroupSpecification):
                write_to_web_element_by_reference_with_clear(
                    self.__driver, 'radio', HTMLElementReference('name', specification.name), magic_values[0])
            else:
                write_to_web_element_by_reference_with_clear(
                    self.__driver, specification.contraints.type, specification.reference, magic_values[0])

        for specification in html_input_specifications:
            self.__find_constraint_candidates_for_input(specification)

        # TODO

    def set_magic_value_sequence(self, html_specification: HTMLInputSpecification | HTMLRadioGroupSpecification, grammar: str, formula: str | None, amount=1) -> List[str]:
        if isinstance(html_specification, HTMLInputSpecification):
            return self.__set_magic_value_sequence_for_input(html_specification, grammar, formula, amount)
        else:
            return self.__set_magic_value_sequence_for_radio_group(html_specification, grammar, formula, amount)

    def __set_magic_value_sequence_for_input(self, html_specification: HTMLInputSpecification, grammar: str, formula: str | None, amount: int) -> List[str]:
        html_input_reference = html_specification.reference
        values = self.__generator.generate_valid_inputs(
            grammar, formula, amount)
        self.__magic_value_map[html_input_reference] = values
        return values

    def __set_magic_value_sequence_for_radio_group(self, html_specification: HTMLRadioGroupSpecification, grammar: str, formula: str | None, amount: int) -> List[str]:
        # html_input_reference = html_specification.reference
        values = self.__generator.generate_valid_inputs(
            grammar, formula, amount)
        self.__magic_value_map[html_specification.name] = values
        return values

    def __find_constraint_candidates_for_input(self, html_specification: HTMLInputSpecification | HTMLRadioGroupSpecification) -> List[ConstraintCandidate]:
        reference = html_specification.reference if isinstance(
            html_specification, HTMLInputSpecification) else html_specification.name
        magic_value_sequence = self.__magic_value_map.get(reference)

        if magic_value_sequence is None:
            return []

        start_trace_recording(
            {'spec': html_specification.get_as_dict(), 'values': magic_value_sequence})

        for magic_value in magic_value_sequence:
            type = html_specification.contraints.type if isinstance(
                html_specification, HTMLInputSpecification) else 'radio'
            reference = html_specification.reference if isinstance(
                html_specification, HTMLInputSpecification) else HTMLElementReference('name', html_specification.name)

            write_to_web_element_by_reference_with_clear(
                self.__driver, type, reference, magic_value)

            record_trace(Action.ATTEMPT_SUBMIT)
            click_web_element_by_reference(
                self.__driver, self.__submit_element)

            time.sleep(2)

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

    def create_specification_for_html_radio_group(self, html_radio_group_specification: HTMLRadioGroupSpecification) -> (str, str | None):
        grammar = load_file_content(
            f'{pre_built_specifications_path}/radio-group/radio-group.bnf')
        grammar = self.__replace_by_list_options(grammar, 'start', list(
            map(lambda o: f'"{o[1]}"', html_radio_group_specification.options)))

        return grammar, None

    def create_specification_for_html_input(self, html_input_specification: HTMLInputSpecification, use_datalist_options=False) -> (str, str | None):
        match html_input_specification.contraints.type:
            case t if t in one_line_text_input_types + [None]:
                return self.__add_constraints_for_one_line_text(html_input_specification.contraints, use_datalist_options)
            case t if t in binary_input_types:
                return self.__add_constraints_for_binary(html_input_specification.contraints.required)
            case InputType.DATE.value:
                return self.__add_constraints_for_date(html_input_specification.contraints, use_datalist_options)
            case InputType.DATETIME_LOCAL.value:
                return self.__add_constraints_for_datetime(html_input_specification.contraints, use_datalist_options)
            case InputType.EMAIL.value:
                return self.__add_constraints_for_email(html_input_specification.contraints, use_datalist_options)
            case InputType.MONTH.value:
                return self.__add_constraints_for_month(html_input_specification.contraints, use_datalist_options)
            case InputType.NUMBER.value:
                return self.__add_constraints_for_number(html_input_specification.contraints, use_datalist_options)
            case InputType.TEXTAREA.value:
                return self.__add_constraints_for_multi_line_text(html_input_specification.contraints, use_datalist_options)
            case InputType.TIME.value:
                return self.__add_constraints_for_time(html_input_specification.contraints, use_datalist_options)
            case InputType.URL.value:
                return self.__add_constraints_for_url(html_input_specification.contraints, use_datalist_options)
            case InputType.WEEK.value:
                return self.__add_constraints_for_week(html_input_specification.contraints, use_datalist_options)
            case _:
                raise ValueError(
                    'The provided type does not match any known html input type')

    def __add_constraints_for_binary(self, required: str) -> (str, str | None):
        grammar = load_file_content(
            f'{pre_built_specifications_path}/binary/binary.bnf' if required is None else f'{pre_built_specifications_path}/binary/binary-required.bnf')

        return grammar, None

    def __add_constraints_for_date(self, html_constraints: HTMLConstraints, use_datalist_options=False) -> (str, str | None):
        grammar = load_file_content(
            f'{pre_built_specifications_path}/date/date.bnf')
        formula = load_file_content(
            f'{pre_built_specifications_path}/date/date.isla')

        if use_datalist_options and html_constraints.list is not None:
            grammar = self.__replace_by_list_options(
                grammar, 'year-month', html_constraints.list)
        if html_constraints.required is not None:
            formula = self.__add_to_formula('str.len(<start>) > 0',
                                            formula, LogicalOperator.AND)
        if html_constraints.min is not None:
            [year_str, month_str, day_str] = html_constraints.min.split('-')
            year = int(year_str)
            month = int(month_str)
            day = int(day_str)
            formula = self.__add_to_formula(f'str.to.int(<year>) >= {year} and str.to.int(<year>) + str.to.int(<month>) >= {year + month} and str.to.int(<year>) + str.to.int(<month>) + str.to.int(<day>) >= {year + month + day}',
                                            formula, LogicalOperator.AND)
        if html_constraints.max is not None:
            [year_str, month_str, day_str] = html_constraints.max.split('-')
            year = int(year_str)
            month = int(month_str)
            day = int(day_str)
            formula = self.__add_to_formula(f'str.to.int(<year>) <= {year} and str.to.int(<year>) + str.to.int(<month>) <= {year + month} and str.to.int(<year>) + str.to.int(<month>) + str.to.int(<day>) <= {year + month + day}',
                                            formula, LogicalOperator.AND)
        # TODO: step

        return grammar, formula

    def __add_constraints_for_datetime(self, html_constraints: HTMLConstraints, use_datalist_options=False) -> (str, str | None):
        grammar = load_file_content(
            f'{pre_built_specifications_path}/datetime/datetime.bnf')
        formula = load_file_content(
            f'{pre_built_specifications_path}/datetime/datetime.isla')

        if use_datalist_options and html_constraints.list is not None:
            grammar = self.__replace_by_list_options(
                grammar, 'datetime', html_constraints.list)
        if html_constraints.required is not None:
            formula = self.__add_to_formula('str.len(<start>) > 0',
                                            formula, LogicalOperator.AND)
        if html_constraints.min is not None:
            split_char = 'T' if 'T' in html_constraints.min else ' '
            [date_str, time_str] = html_constraints.min.split(split_char)
            [year_str, month_str, day_str] = date_str.split('-')
            [hour_str, minute_str] = time_str.split(':')
            # TODO
        if html_constraints.max is not None:
            split_char = 'T' if 'T' in html_constraints.max else ' '
            [date_str, time_str] = html_constraints.max.split(split_char)
            [year_str, month_str, day_str] = date_str.split('-')
            [hour_str, minute_str] = time_str.split(':')
            # TODO
        # TODO: step
        # if html_constraints.step is not None:
        #     formula = self.__add_to_formula(f'(str.to.int(<year>) + str.to.int(<month>)) mod {html_constraints.step} = 0',
        #                                     formula, LogicalOperator.AND)

        return grammar, formula

    def __add_constraints_for_email(self, html_constraints: HTMLConstraints, use_datalist_options=False) -> (str, str | None):
        grammar = load_file_content(
            f'{pre_built_specifications_path}/email/email.bnf' if html_constraints.required is None else f'{pre_built_specifications_path}/email/email-required.bnf')
        formula = load_file_content(
            f'{pre_built_specifications_path}/email/email.isla')

        if use_datalist_options and html_constraints.list is not None:
            grammar = self.__replace_by_list_options(
                grammar, 'email', html_constraints.list)
        if html_constraints.minlength is not None:
            formula = self.__add_to_formula(f'str.len(<email>) >= {html_constraints.minlength}',
                                            formula, LogicalOperator.AND)
        if html_constraints.maxlength is not None:
            formula = self.__add_to_formula(f'str.len(<email>) <= {html_constraints.maxlength}',
                                            formula, LogicalOperator.AND)
        if html_constraints.multiple is not None:
            # TODO
            pass
        if html_constraints.pattern is not None:
            # TODO
            pass

        return grammar, formula

    def __add_constraints_for_month(self, html_constraints: HTMLConstraints, use_datalist_options=False) -> (str, str | None):
        grammar = load_file_content(
            f'{pre_built_specifications_path}/month/month.bnf')
        formula = load_file_content(
            f'{pre_built_specifications_path}/month/month.isla')

        if use_datalist_options and html_constraints.list is not None:
            grammar = self.__replace_by_list_options(
                grammar, 'date', html_constraints.list)
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

    def __add_constraints_for_number(self, html_constraints: HTMLConstraints, use_datalist_options=False) -> (str, str | None):
        grammar = load_file_content(
            f'{pre_built_specifications_path}/number/whole.bnf' if html_constraints.required is None else f'{pre_built_specifications_path}/number/whole-required.bnf')
        formula = None

        if use_datalist_options and html_constraints.list is not None:
            grammar = self.__replace_by_list_options(
                grammar, 'number', html_constraints.list)

        if html_constraints.min is not None:
            formula = self.__add_to_formula(f'str.to.int(<start>) >= {html_constraints.min}',
                                            formula, LogicalOperator.AND)

        if html_constraints.max is not None:
            formula = self.__add_to_formula(f'str.to.int(<start>) <= {html_constraints.max}',
                                            formula, LogicalOperator.AND)

        if html_constraints.step is not None:
            formula = self.__add_to_formula(f'str.to.int(<start>) mod {html_constraints.step} = 0',
                                            formula, LogicalOperator.AND)

        return grammar, formula

    def __add_constraints_for_multi_line_text(self, html_constraints: HTMLConstraints, use_datalist_options: bool) -> (str, str | None):
        grammar = load_file_content(
            f'{pre_built_specifications_path}/text/multi-line-text.bnf')
        formula = None

        if html_constraints.required is not None and html_constraints.minlength is None:
            formula = self.__add_to_formula('str.len(<start>) > 0',
                                            formula, LogicalOperator.AND)
        elif html_constraints.minlength is not None:
            formula = self.__add_to_formula(
                f'str.len(<start>) >= {html_constraints.minlength}', formula, LogicalOperator.AND)
        if html_constraints.maxlength is not None:
            formula = self.__add_to_formula(
                f'str.len(<start>) <= {html_constraints.maxlength}', formula, LogicalOperator.AND)

        return grammar, formula

    def __add_constraints_for_one_line_text(self, html_constraints: HTMLConstraints, use_datalist_options: bool) -> (str, str | None):
        grammar = load_file_content(
            f'{pre_built_specifications_path}/text/one-line-text.bnf')
        formula = None

        if use_datalist_options and html_constraints.list is not None:
            grammar = self.__replace_by_list_options(
                grammar, 'one-line-text', html_constraints.list)
        if html_constraints.required is not None and html_constraints.minlength is None:
            formula = self.__add_to_formula('str.len(<start>) > 0',
                                            formula, LogicalOperator.AND)
        elif html_constraints.minlength is not None:
            formula = self.__add_to_formula(
                f'str.len(<start>) >= {html_constraints.minlength}', formula, LogicalOperator.AND)
        if html_constraints.maxlength is not None:
            formula = self.__add_to_formula(
                f'str.len(<start>) <= {html_constraints.maxlength}', formula, LogicalOperator.AND)
        if html_constraints.pattern is not None:
            # TODO
            pass

        return grammar, formula

    def __add_constraints_for_time(self, html_constraints: HTMLConstraints, use_datalist_options=False) -> (str, str | None):
        grammar = load_file_content(
            f'{pre_built_specifications_path}/time/time.bnf')
        formula = load_file_content(
            f'{pre_built_specifications_path}/time/time.isla')

        if use_datalist_options and html_constraints.list is not None:
            grammar = self.__replace_by_list_options(
                grammar, 'time', html_constraints.list)
        if html_constraints.required is not None:
            formula = self.__add_to_formula('str.len(<start>) > 0',
                                            formula, LogicalOperator.AND)
        if html_constraints.min is not None:
            [hour_str, minute_str] = html_constraints.min.split(':')
            hours = int(hour_str)
            minutes = int(minute_str)
            formula = self.__add_to_formula(f'str.to.int(<hour>) >= {hours} and str.to.int(<hour>) + str.to.int(<minute>) >= {hours + minutes}',
                                            formula, LogicalOperator.AND)
        if html_constraints.max is not None:
            [hour_str, minute_str] = html_constraints.min.split(':')
            hours = int(hour_str)
            minutes = int(minute_str)
            formula = self.__add_to_formula(f'str.to.int(<hour>) <= {hours} and str.to.int(<hour>) + str.to.int(<minute>) <= {hours + minutes}',
                                            formula, LogicalOperator.AND)
        # TODO: step
        # if html_constraints.step is not None:
        #     formula = self.__add_to_formula(f'(str.to.int(<year>) + str.to.int(<month>)) mod {html_constraints.step} = 0',
        #                                     formula, LogicalOperator.AND)

        return grammar, formula

    def __add_constraints_for_url(self, html_constraints: HTMLConstraints, use_datalist_options=False) -> (str, str | None):
        grammar = load_file_content(
            f'{pre_built_specifications_path}/url/url.bnf')
        formula = None
        # formula = load_file_content(
        #     f'{pre_built_specifications_path}/url/url.isla')

        if use_datalist_options and html_constraints.list is not None:
            grammar = self.__replace_by_list_options(
                grammar, 'url', html_constraints.list)
        if html_constraints.required is not None and html_constraints.minlength is None:
            formula = self.__add_to_formula('str.len(<start>) > 8',
                                            formula, LogicalOperator.AND)
        else:
            formula = self.__add_to_formula(f'str.len(<start>) >= {html_constraints.minlength}',
                                            formula, LogicalOperator.AND)
        if html_constraints.maxlength is not None:
            formula = self.__add_to_formula(f'str.len(<start>) <= {html_constraints.maxlength}',
                                            formula, LogicalOperator.AND)
        if html_constraints.pattern is not None:
            # TODO
            pass

        return grammar, None

    def __add_constraints_for_week(self, html_constraints: HTMLConstraints, use_datalist_options=False) -> (str, str | None):
        grammar = load_file_content(
            f'{pre_built_specifications_path}/week/week.bnf')
        formula = load_file_content(
            f'{pre_built_specifications_path}/week/week.isla')

        if use_datalist_options and html_constraints.list is not None:
            grammar = self.__replace_by_list_options(
                grammar, 'yearmonth', html_constraints.list)
        if html_constraints.required is not None:
            formula = self.__add_to_formula('str.len(<start>) > 0',
                                            formula, LogicalOperator.AND)
        if html_constraints.min is not None:
            [year_str, week_str] = html_constraints.min.split('-W')
            year = int(year_str)
            week = int(week_str)
            formula = self.__add_to_formula(f'str.to.int(<year>) >= {year} and str.to.int(<year>) + str.to.int(<week>) >= {year + week}',
                                            formula, LogicalOperator.AND)
        if html_constraints.max is not None:
            [year_str, week_str] = html_constraints.max.split('-W')
            year = int(year_str)
            week = int(week_str)
            formula = self.__add_to_formula(f'str.to.int(<year>) <= {year} and str.to.int(<year>) + str.to.int(<week>) <= {year + week}',
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

    # TODO: decide which one to use. Should structure grammars in a way that disgarding the parts
    # after the list options does not matter. Otherwise we might get tokens that are unreachable and errors
    def __replace_by_list_options(self, grammar: str, option_identifier: str, list_options: List[str]) -> str:
        head, sep, _ = grammar.partition(f'<{option_identifier}> ::= ')
        options = ' | '.join(list_options)
        return f'{head}{sep}{options}'

    # def __replace_by_list_options(self, grammar: str, option_identifier: str, list_options: List[str]) -> str:
    #     lines = grammar.split('\n')
    #     for i in range(len(lines)):
    #         if f'<{option_identifier}> ::=' in lines[i]:
    #             new_line = lines[i]
    #             head, sep, _ = new_line.partition(
    #                 f'<{option_identifier}> ::= ')
    #             options = ' | '.join(list_options)
    #             new_line = f'{head}{sep}{options}'
    #             lines[i] = new_line

    #     return '\n'.join(lines)
