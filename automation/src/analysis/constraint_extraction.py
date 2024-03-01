from enum import Enum
from lxml.html import Element
from selenium.webdriver import Chrome
from seleniumwire.request import Request
from typing import List, Literal, Dict, Tuple

from src.analysis.html_analysis import (
    HTMLConstraints,
    HTMLElementReference,
    HTMLInputSpecification,
    HTMLRadioGroupSpecification,
)
from src.generation.input_generation import InputGenerator, ValidityEnum
from src.proxy.interception import (
    NetworkInterceptor,
    decode_bytes,
    submission_interception_header,
)
from src.utility.pattern_translation import PatternConverter
from src.utility.helpers import *

"""
Constraint Extraction module

Provides classes to define constraint candidates, extract candidates from inputs and
build a specification for these inputs.
"""


class ConstraintCandidateType(str, Enum):
    VARIABLE_COMPARISON = "VarComp"
    LITERAL_COMPARISON = "LiteralComp"
    VARIABLE_LENGTH_COMPARISON = "VarLengthComp"
    LITERAL_LENGTH_COMPARISON = "LiteralLengthComp"
    PATTERN_TEST = "PatternTest"


class ConstraintOtherValueType(str, Enum):
    UNKOWN = "unokwn variable"
    REFERENCE = "reference"


class ConstraintCandidate:
    def __init__(self, constraint_type: ConstraintCandidateType) -> None:
        self.type = constraint_type

    @classmethod
    def from_dict(cls, json: Dict):
        constraint_type = json.get("type")

        match constraint_type:
            case ConstraintCandidateType.LITERAL_COMPARISON.value:
                return LiteralCompCandidate(
                    json, ConstraintCandidateType.LITERAL_COMPARISON
                )
            case ConstraintCandidateType.LITERAL_LENGTH_COMPARISON.value:
                return LiteralCompCandidate(
                    json, ConstraintCandidateType.LITERAL_LENGTH_COMPARISON
                )
            case ConstraintCandidateType.VARIABLE_COMPARISON.value:
                return VarCompCandidate(
                    json, ConstraintCandidateType.VARIABLE_COMPARISON
                )
            case ConstraintCandidateType.VARIABLE_LENGTH_COMPARISON.value:
                return VarCompCandidate(
                    json, ConstraintCandidateType.VARIABLE_LENGTH_COMPARISON
                )
            case ConstraintCandidateType.PATTERN_TEST.value:
                return PatternMatchCandidate(json, ConstraintCandidateType.PATTERN_TEST)
            case _:
                raise ValueError(f"type {constraint_type} not recognized")

    def convert_operator(self, operator: str) -> str:
        if operator == "==" or operator == "===":
            return ISLa.EQ.value
        elif operator == "!=" or operator == "!==":
            return f"{ISLa.NOT.value} (VALUE {ISLa.EQ.value} OTHER)"
        else:
            return operator

    def __eq__(self, other):
        if isinstance(other, ConstraintCandidate):
            vars(self) == vars(other)
        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __str__(self) -> str:
        return json.dumps(vars(self))


class LiteralCompCandidate(ConstraintCandidate):
    def __init__(self, json: Dict, candidate_type: ConstraintCandidateType) -> None:
        super().__init__(candidate_type)
        self.operator = self.convert_operator(json.get("operator"))
        self.other_value = json.get("otherValue")


class VarCompCandidate(ConstraintCandidate):
    def __init__(self, json: Dict, candidate_type: ConstraintCandidateType) -> None:
        super().__init__(candidate_type)
        self.operator = self.convert_operator(json.get("operator"))
        self.other_value_type: Literal["reference", "unknown variable"] = json.get(
            "otherValue"
        ).get("type")

        other_value = json.get("otherValue").get("value")
        if self.other_value_type == "unkown variable":
            self.other_value = other_value
        else:
            method = other_value["access_method"]
            value = other_value["access_value"]
            self.other_value = HTMLElementReference(method, value)


class PatternMatchCandidate(ConstraintCandidate):
    def __init__(self, json: Dict, candidate_type: ConstraintCandidateType) -> None:
        super().__init__(candidate_type)
        self.is_regex = False

        pattern = json.get("pattern")
        if pattern[0] == "/":
            index = pattern.rfind("/")
            if index > 0:
                pattern = pattern[1:index]
                self.is_regex = True

        self.pattern = pattern


class ConstraintCandidateResult:
    def __init__(self, request_response: Dict) -> None:
        self.candidates: List[ConstraintCandidate] = []
        for elem in request_response["candidates"]:
            self.candidates.append(ConstraintCandidate.from_dict(elem))

    def __eq__(self, other):
        if isinstance(other, ConstraintCandidateResult):
            return self.candidates == other.candidates
        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __str__(self) -> str:
        return (
            f"candidates: [{(', ').join(list(map(lambda c: str(c), self.candidates)))}]"
        )


class ConstraintCandidateFinder:
    """ConstraintCandidateFinder class

    Provides methods to identify constraint candidates for a specific input of the form.
    """

    def __init__(
        self,
        web_driver: Chrome,
        submit_element: Element,
        interceptor: NetworkInterceptor,
        stop_on_first_success: bool,
        exit_method,
    ) -> None:
        self.__driver = web_driver
        self.__exit_method = exit_method
        self.__generator = InputGenerator()
        self.__interceptor = interceptor
        self.__magic_value_map: Dict[
            HTMLInputSpecification | HTMLRadioGroupSpecification, List[str]
        ] = {}
        self.__stop_on_first_success = stop_on_first_success
        self.__submit_element = submit_element

    def set_valid_value_sequence(
        self,
        html_specification: HTMLInputSpecification | HTMLRadioGroupSpecification,
        grammar: str,
        formula: str | None,
        amount=1,
    ) -> List[str]:
        print(f"generating values for {str(html_specification.reference)}")
        if isinstance(html_specification, HTMLInputSpecification):
            return self.__set_magic_value_sequence_for_input(
                html_specification, grammar, formula, amount
            )
        else:
            return self.__set_magic_value_sequence_for_radio_group(
                html_specification, grammar, formula, amount
            )

    def fill_with_valid_values(self):
        for spec, values in self.__magic_value_map.items():
            write_to_web_element_by_reference_with_clear(
                self.__driver, spec.type, spec.reference, values[0]
            )

    # def find_initial_js_constraint_candidates(
    #     self, html_specification: HTMLInputSpecification | HTMLRadioGroupSpecification
    # ) -> ConstraintCandidateResult:
    #     """Try to extract as many constraint candidates as possible from the JavaScript source code for a given input."""
    #     magic_value_sequence = self.__magic_value_map.get(html_specification)
    #     if magic_value_sequence is None:
    #         return ConstraintCandidateResult({"candidates": []})

    #     return self.__get_constraint_candidates_for_value_sequence(
    #         html_specification, magic_value_sequence
    #     )

    def find_js_constraint_candidates(
        self,
        spec: HTMLInputSpecification | HTMLRadioGroupSpecification,
        grammar: str,
        formula: str | None = None,
        amount: int = 1,
    ) -> ConstraintCandidateResult:
        generator = InputGenerator()
        values = generator.generate_inputs(grammar, formula, ValidityEnum.VALID, amount)
        values = list(map(lambda v: v.value, values))
        return self.__get_constraint_candidates_for_value_sequence(spec, values)

    def __get_constraint_candidates_for_value_sequence(
        self,
        spec: HTMLInputSpecification | HTMLRadioGroupSpecification,
        values: List[str],
    ) -> ConstraintCandidateResult:
        type = (
            spec.constraints.type
            if isinstance(spec, HTMLInputSpecification)
            else InputType.RADIO.value
        )

        start_trace_recording({"spec": spec.get_as_dict(), "values": values})

        for value in values:
            write_to_web_element_by_reference_with_clear(
                self.__driver, type, spec.reference, value
            )

            self.__attempt_submit()

        all_traces = decode_bytes(
            stop_trace_recording(
                {
                    "spec": spec.get_as_dict(),
                    "values": values,
                }
            ).content
        )

        # return ConstraintCandidateResult({"candidates": []})

        constraint_candidate_response = get_constraint_candidates(all_traces)
        response_str = decode_bytes(constraint_candidate_response.content)
        return ConstraintCandidateResult(json.loads(response_str))

    def __set_magic_value_sequence_for_input(
        self,
        html_specification: HTMLInputSpecification,
        grammar: str,
        formula: str | None,
        amount: int,
    ) -> List[str]:
        generated_values = self.__generator.generate_inputs(
            grammar, formula, ValidityEnum.VALID, amount
        )
        values = list(map(lambda v: v.value, generated_values))
        self.__magic_value_map[html_specification] = values
        return values

    def __set_magic_value_sequence_for_radio_group(
        self,
        html_specification: HTMLRadioGroupSpecification,
        grammar: str,
        formula: str | None,
        amount: int,
    ) -> List[str]:
        generated_values = self.__generator.generate_inputs(
            grammar, formula, ValidityEnum.VALID, amount
        )
        values = list(map(lambda v: v.value, generated_values))
        self.__magic_value_map[html_specification] = values
        return values

    def __attempt_submit(self) -> None:
        self.__interceptor.generated_values = get_current_values_from_form()
        clear_value_mapping()

        record_trace(Action.ATTEMPT_SUBMIT)
        click_web_element_by_reference(self.__driver, self.__submit_element)

        if not self.__stop_on_first_success:
            return None

        # Check if the submission was successful and exit if it was
        all_requests: List[Request] = self.__driver.requests
        for request in all_requests:
            if (
                request.response is not None
                and request.response.headers[submission_interception_header] is not None
            ):
                self.__exit_method()


class ISLa(Enum):
    AND = "and"
    OR = "or"
    NOT = "not"
    XOR = "xor"
    IMPLIES = "implies"
    EQ = "="
    LT = "<"
    GT = ">"
    LTE = "<="
    GTE = ">="


class SpecificationBuilder:
    def __init__(self) -> None:
        self.refrence_to_spec_map: Dict[
            HTMLElementReference, Tuple[str, str | None]
        ] = {}

    def create_specification_for_html_radio_group(
        self, html_radio_group_specification: HTMLRadioGroupSpecification
    ) -> Tuple[str, str | None]:
        grammar = load_file_content(
            f"{pre_built_specifications_path}/radio-group/radio-group.bnf"
        )
        grammar = self.__replace_by_list_options(
            grammar,
            "start",
            list(map(lambda o: f'"{o[1]}"', html_radio_group_specification.options)),
        )

        self.refrence_to_spec_map[html_radio_group_specification.reference] = (
            grammar,
            None,
        )
        return grammar, None

    def create_specification_for_html_input(
        self,
        html_input_specification: HTMLInputSpecification,
        use_datalist_options=False,
    ) -> Tuple[str, str | None]:
        match html_input_specification.constraints.type:
            case t if t in one_line_text_input_types + [None]:
                grammar, formula = self.__add_constraints_for_one_line_text(
                    html_input_specification.constraints, use_datalist_options
                )
            case t if t in binary_input_types:
                grammar, formula = self.__add_constraints_for_binary(
                    html_input_specification.constraints.required
                )
            case InputType.DATE.value:
                grammar, formula = self.__add_constraints_for_date(
                    html_input_specification.constraints, use_datalist_options
                )
            case InputType.DATETIME_LOCAL.value:
                grammar, formula = self.__add_constraints_for_datetime(
                    html_input_specification.constraints, use_datalist_options
                )
            case InputType.EMAIL.value:
                grammar, formula = self.__add_constraints_for_email(
                    html_input_specification.constraints, use_datalist_options
                )
            case InputType.MONTH.value:
                grammar, formula = self.__add_constraints_for_month(
                    html_input_specification.constraints, use_datalist_options
                )
            case InputType.NUMBER.value:
                grammar, formula = self.__add_constraints_for_number(
                    html_input_specification.constraints, use_datalist_options
                )
            case InputType.TEXTAREA.value:
                grammar, formula = self.__add_constraints_for_multi_line_text(
                    html_input_specification.constraints, use_datalist_options
                )
            case InputType.TIME.value:
                grammar, formula = self.__add_constraints_for_time(
                    html_input_specification.constraints, use_datalist_options
                )
            case InputType.URL.value:
                grammar, formula = self.__add_constraints_for_url(
                    html_input_specification.constraints, use_datalist_options
                )
            case InputType.WEEK.value:
                grammar, formula = self.__add_constraints_for_week(
                    html_input_specification.constraints, use_datalist_options
                )
            case _:
                raise ValueError(
                    "The provided type does not match any known html input type"
                )

        self.refrence_to_spec_map[html_input_specification.reference] = (
            grammar,
            formula,
        )
        return grammar, formula

    def write_specification_to_file(
        self, name: str, grammar: str, formula: str = None
    ) -> Tuple[str, str]:
        # TODO: create directory and handle permission denied error
        # Path('/specification').mkdir(exist_ok=True)
        grammar_file_name = f"{name}.bnf"
        formula_file_name = f"{name}.isla"

        write_to_file(f"specification/{grammar_file_name}", grammar)
        write_to_file(
            f"specification/{formula_file_name}", formula if formula is not None else ""
        )

        return grammar_file_name, formula_file_name

    def add_constraints_to_current_specification(
        self,
        reference: HTMLElementReference,
        input_type: str,
        new_constraints: ConstraintCandidateResult,
    ) -> Tuple[str, str]:
        existing_spec = self.refrence_to_spec_map.get(reference)
        if existing_spec is None:
            grammar = ""
            formula = None
        else:
            grammar, formula = existing_spec

        for candidate in new_constraints.candidates:
            constraint_type = candidate.type
            match constraint_type:
                case ConstraintCandidateType.LITERAL_COMPARISON.value:
                    grammar, formula = self.__handle_literal_comparison_candidate(
                        input_type, grammar, formula, candidate
                    )
                # case ConstraintCandidateType.LITERAL_LENGTH_COMPARISON.value:
                #     grammar, formula = (
                #         self.__handle_literal_length_comparison_candidate(
                #             input_type, grammar, formula, candidate
                #         )
                #     )
                case ConstraintCandidateType.VARIABLE_COMPARISON.value:
                    grammar, formula = self.__handle_var_comparison_candidate(
                        grammar, formula, candidate
                    )
                # case ConstraintCandidateType.VARIABLE_LENGTH_COMPARISON.value:
                #     grammar, formula = self.__handle_var_length_comparison_candidate(
                #         grammar, formula, candidate
                #     )
                case ConstraintCandidateType.PATTERN_TEST.value:
                    grammar, formula = self.__handle_pattern_candidate(
                        input_type, grammar, formula, candidate
                    )
                case _:
                    raise TypeError(f"type {constraint_type} not recognized")

        self.refrence_to_spec_map[reference] = grammar, formula
        return grammar, formula

    def __handle_literal_comparison_candidate(
        self,
        input_type: str,
        grammar: str,
        formula: str,
        candidate: LiteralCompCandidate,
    ) -> Tuple[str, str | None]:
        formula = self.__add_to_formula(
            f'<{input_type}> {candidate.operator} "{candidate.other_value}"',
            formula,
            ISLa.OR,
        )
        return grammar, formula

    def __handle_literal_length_comparison_candidate(
        self,
        input_type: str,
        grammar: str,
        formula: str,
        candidate: LiteralCompCandidate,
    ) -> Tuple[str, str | None]:
        formula = self.__add_to_formula(
            f'str.len(<{input_type}>) {candidate.operator} "{candidate.other_value}"',
            formula,
            ISLa.OR,
        )
        return grammar, formula

    def __handle_var_comparison_candidate(
        self, grammar: str, formula: str, candidate: VarCompCandidate
    ) -> Tuple[str, str | None]:
        if candidate.other_value_type == ConstraintOtherValueType.REFERENCE.value:
            other_spec = self.refrence_to_spec_map.get(candidate.other_value)
            if other_spec is not None:
                other_grammar, other_formula = other_spec
                other_grammar_dict = self.__grammar_string_to_dict(other_grammar)
                grammar_dict = self.__grammar_string_to_dict(grammar)
                new_grammar_dict, formula = self.__combine_grammars_and_formulas(
                    grammar_dict,
                    other_grammar_dict,
                    formula,
                    other_formula,
                    candidate.operator,
                )
                grammar = self.__grammar_dict_to_string(new_grammar_dict)

        return formula, grammar

    def __handle_var_length_comparison_candidate(
        self, grammar: str, formula: str, candidate: VarCompCandidate
    ) -> Tuple[str, str | None]:
        # TODO: This is hard, what if the length of the current field is compared to a numerical value in another field, what if it is
        # compared to the length of another field? Would probaby need other codeql queries to do something reasonable here.
        return grammar, formula

    def __handle_pattern_candidate(
        self,
        input_type: str,
        grammar: str,
        formula: str,
        candidate: PatternMatchCandidate,
    ) -> Tuple[str, str | None]:
        if not candidate.is_regex:
            formula = self.__add_to_formula(
                f'str.contains(<{input_type}>, "{candidate.pattern}")', formula, ISLa.OR
            )
        else:
            pattern_converter = PatternConverter(candidate.pattern)
            pattern_grammar = pattern_converter.convert_pattern_to_grammar()
            start_symbol = "<start> ::= "
            if pattern_grammar.startswith(start_symbol):
                pattern_grammar = pattern_grammar[len(start_symbol) :]

            grammar = self.__replace_by_any_string(grammar, input_type, pattern_grammar)

        return grammar, formula

    def __add_constraints_for_binary(self, required: str) -> Tuple[str, str | None]:
        grammar = load_file_content(
            f"{pre_built_specifications_path}/binary/binary.bnf"
            if required is None
            else f"{pre_built_specifications_path}/binary/binary-required.bnf"
        )

        return grammar, None

    def __add_constraints_for_date(
        self, html_constraints: HTMLConstraints, use_datalist_options=False
    ) -> Tuple[str, str | None]:
        grammar = load_file_content(f"{pre_built_specifications_path}/date/date.bnf")
        formula = load_file_content(f"{pre_built_specifications_path}/date/date.isla")

        if use_datalist_options and html_constraints.list is not None:
            grammar = self.__replace_by_list_options(
                grammar, "data", html_constraints.list
            )
        if html_constraints.required is not None:
            formula = self.__add_to_formula("str.len(<start>) > 0", formula, ISLa.AND)
        if html_constraints.min is not None:
            [year_str, month_str, day_str] = html_constraints.min.split("-")
            year = int(year_str)
            month = int(month_str)
            day = int(day_str)
            formula = self.__add_to_formula(
                f"str.to.int(<year>) >= {year} and str.to.int(<year>) + str.to.int(<month>) >= {year + month} and str.to.int(<year>) + str.to.int(<month>) + str.to.int(<day>) >= {year + month + day}",
                formula,
                ISLa.AND,
            )
        if html_constraints.max is not None:
            [year_str, month_str, day_str] = html_constraints.max.split("-")
            year = int(year_str)
            month = int(month_str)
            day = int(day_str)
            formula = self.__add_to_formula(
                f"str.to.int(<year>) <= {year} and str.to.int(<year>) + str.to.int(<month>) <= {year + month} and str.to.int(<year>) + str.to.int(<month>) + str.to.int(<day>) <= {year + month + day}",
                formula,
                ISLa.AND,
            )
        # TODO: step

        return grammar, formula

    def __add_constraints_for_datetime(
        self, html_constraints: HTMLConstraints, use_datalist_options=False
    ) -> Tuple[str, str | None]:
        grammar = load_file_content(
            f"{pre_built_specifications_path}/datetime/datetime.bnf"
        )
        formula = load_file_content(
            f"{pre_built_specifications_path}/datetime/datetime.isla"
        )

        if use_datalist_options and html_constraints.list is not None:
            grammar = self.__replace_by_list_options(
                grammar, "datetime", html_constraints.list
            )
        if html_constraints.required is not None:
            formula = self.__add_to_formula("str.len(<start>) > 0", formula, ISLa.AND)
        if html_constraints.min is not None:
            split_char = "T" if "T" in html_constraints.min else " "
            [date_str, time_str] = html_constraints.min.split(split_char)
            [year_str, month_str, day_str] = date_str.split("-")
            [hour_str, minute_str] = time_str.split(":")
            # TODO
        if html_constraints.max is not None:
            split_char = "T" if "T" in html_constraints.max else " "
            [date_str, time_str] = html_constraints.max.split(split_char)
            [year_str, month_str, day_str] = date_str.split("-")
            [hour_str, minute_str] = time_str.split(":")
            # TODO
        # TODO: step
        # if html_constraints.step is not None:
        #     formula = self.__add_to_formula(f'(str.to.int(<year>) + str.to.int(<month>)) mod {html_constraints.step} = 0',
        #                                     formula, ISLa.AND)

        return grammar, formula

    def __add_constraints_for_email(
        self, html_constraints: HTMLConstraints, use_datalist_options=False
    ) -> Tuple[str, str | None]:
        grammar = load_file_content(f"{pre_built_specifications_path}/email/email.bnf")
        # TODO: change email grammar (and formula) to not generate only stupid values and take forever
        # formula = load_file_content(f"{pre_built_specifications_path}/email/email.isla")
        formula = None

        if use_datalist_options and html_constraints.list is not None:
            grammar = self.__replace_by_list_options(
                grammar, "email", html_constraints.list
            )
        if html_constraints.required is not None:
            formula = self.__add_to_formula(f"str.len(<start>) >= 3", formula, ISLa.AND)
        if html_constraints.minlength is not None:
            formula = self.__add_to_formula(
                f"str.len(<email>) >= {html_constraints.minlength}",
                formula,
                ISLa.AND,
            )
        if html_constraints.maxlength is not None:
            formula = self.__add_to_formula(
                f"str.len(<email>) <= {html_constraints.maxlength}",
                formula,
                ISLa.AND,
            )
        if html_constraints.multiple is not None:
            # TODO
            pass
        if html_constraints.pattern is not None:
            # TODO
            pass

        return grammar, formula

    def __add_constraints_for_month(
        self, html_constraints: HTMLConstraints, use_datalist_options=False
    ) -> Tuple[str, str | None]:
        grammar = load_file_content(f"{pre_built_specifications_path}/month/month.bnf")
        formula = load_file_content(f"{pre_built_specifications_path}/month/month.isla")

        if use_datalist_options and html_constraints.list is not None:
            grammar = self.__replace_by_list_options(
                grammar, "month", html_constraints.list
            )
        if html_constraints.required is not None:
            formula = self.__add_to_formula("str.len(<start>) > 0", formula, ISLa.AND)
        if html_constraints.min is not None:
            [year_str, month_str] = html_constraints.min.split("-")
            year = int(year_str)
            month = int(month_str)
            formula = self.__add_to_formula(
                f"str.to.int(<year>) >= {year} and str.to.int(<year>) + str.to.int(<month>) >= {year + month}",
                formula,
                ISLa.AND,
            )
        if html_constraints.max is not None:
            [year_str, month_str] = html_constraints.max.split("-")
            year = int(year_str)
            month = int(month_str)
            formula = self.__add_to_formula(
                f"str.to.int(<year>) <= {year} and str.to.int(<year>) + str.to.int(<month>) <= {year + month}",
                formula,
                ISLa.AND,
            )
        # TODO: step not working because can not set calculation in parantheses
        # if html_constraints.step is not None:
        #     formula = self.__add_to_formula(f'(str.to.int(<year>) + str.to.int(<month>)) mod {html_constraints.step} = 0',
        #                                     formula, ISLa.AND)

        return grammar, formula

    def __add_constraints_for_number(
        self, html_constraints: HTMLConstraints, use_datalist_options=False
    ) -> Tuple[str, str | None]:
        grammar = load_file_content(f"{pre_built_specifications_path}/number/whole.bnf")
        formula = None

        if use_datalist_options and html_constraints.list is not None:
            grammar = self.__replace_by_list_options(
                grammar, "number", html_constraints.list
            )

        if html_constraints.required is not None:
            formula = self.__add_to_formula(
                f"str.to.int(<start>) > 0", formula, ISLa.AND
            )

        if html_constraints.min is not None:
            formula = self.__add_to_formula(
                f"str.to.int(<start>) >= {html_constraints.min}",
                formula,
                ISLa.AND,
            )

        if html_constraints.max is not None:
            formula = self.__add_to_formula(
                f"str.to.int(<start>) <= {html_constraints.max}",
                formula,
                ISLa.AND,
            )

        if html_constraints.step is not None:
            formula = self.__add_to_formula(
                f"str.to.int(<start>) mod {html_constraints.step} = 0",
                formula,
                ISLa.AND,
            )

        return grammar, formula

    def __add_constraints_for_multi_line_text(
        self, html_constraints: HTMLConstraints, use_datalist_options: bool
    ) -> Tuple[str, str | None]:
        grammar = load_file_content(
            f"{pre_built_specifications_path}/text/multi-line-text.bnf"
        )
        formula = None

        if html_constraints.required is not None and html_constraints.minlength is None:
            formula = self.__add_to_formula("str.len(<start>) > 0", formula, ISLa.AND)
        elif html_constraints.minlength is not None:
            formula = self.__add_to_formula(
                f"str.len(<start>) >= {html_constraints.minlength}",
                formula,
                ISLa.AND,
            )
        if html_constraints.maxlength is not None:
            formula = self.__add_to_formula(
                f"str.len(<start>) <= {html_constraints.maxlength}",
                formula,
                ISLa.AND,
            )

        return grammar, formula

    def __add_constraints_for_one_line_text(
        self, html_constraints: HTMLConstraints, use_datalist_options: bool
    ) -> Tuple[str, str | None]:
        grammar = load_file_content(
            f"{pre_built_specifications_path}/text/one-line-text.bnf"
        )
        formula = None

        if use_datalist_options and html_constraints.list is not None:
            grammar = self.__replace_by_list_options(
                grammar, "text", html_constraints.list
            )
        if html_constraints.required is not None and html_constraints.minlength is None:
            formula = self.__add_to_formula("str.len(<start>) > 0", formula, ISLa.AND)
        elif html_constraints.minlength is not None:
            formula = self.__add_to_formula(
                f"str.len(<start>) >= {html_constraints.minlength}",
                formula,
                ISLa.AND,
            )
        if html_constraints.maxlength is not None:
            formula = self.__add_to_formula(
                f"str.len(<start>) <= {html_constraints.maxlength}",
                formula,
                ISLa.AND,
            )
        if html_constraints.pattern is not None:
            # TODO
            pass

        return grammar, formula

    def __add_constraints_for_time(
        self, html_constraints: HTMLConstraints, use_datalist_options=False
    ) -> Tuple[str, str | None]:
        grammar = load_file_content(f"{pre_built_specifications_path}/time/time.bnf")
        formula = load_file_content(f"{pre_built_specifications_path}/time/time.isla")

        if use_datalist_options and html_constraints.list is not None:
            grammar = self.__replace_by_list_options(
                grammar, "time", html_constraints.list
            )
        if html_constraints.required is not None:
            formula = self.__add_to_formula("str.len(<start>) > 0", formula, ISLa.AND)
        if html_constraints.min is not None:
            [hour_str, minute_str] = html_constraints.min.split(":")
            hours = int(hour_str)
            minutes = int(minute_str)
            formula = self.__add_to_formula(
                f"str.to.int(<hour>) >= {hours} and str.to.int(<hour>) + str.to.int(<minute>) >= {hours + minutes}",
                formula,
                ISLa.AND,
            )
        if html_constraints.max is not None:
            [hour_str, minute_str] = html_constraints.min.split(":")
            hours = int(hour_str)
            minutes = int(minute_str)
            formula = self.__add_to_formula(
                f"str.to.int(<hour>) <= {hours} and str.to.int(<hour>) + str.to.int(<minute>) <= {hours + minutes}",
                formula,
                ISLa.AND,
            )
        # TODO: step
        # if html_constraints.step is not None:
        #     formula = self.__add_to_formula(f'(str.to.int(<year>) + str.to.int(<month>)) mod {html_constraints.step} = 0',
        #                                     formula, ISLa.AND)

        return grammar, formula

    def __add_constraints_for_url(
        self, html_constraints: HTMLConstraints, use_datalist_options=False
    ) -> Tuple[str, str | None]:
        # TODO: grammar not always accepted by chrome
        grammar = load_file_content(f"{pre_built_specifications_path}/url/url.bnf")
        # TODO: formula not working
        # formula = load_file_content(
        #     f'{pre_built_specifications_path}/url/url.isla')
        formula = None

        if use_datalist_options and html_constraints.list is not None:
            grammar = self.__replace_by_list_options(
                grammar, "url", html_constraints.list
            )
        if html_constraints.required is not None and html_constraints.minlength is None:
            formula = self.__add_to_formula("str.len(<start>) >= 8", formula, ISLa.AND)
        else:
            formula = self.__add_to_formula(
                f"str.len(<start>) >= {html_constraints.minlength}",
                formula,
                ISLa.AND,
            )
        if html_constraints.maxlength is not None:
            formula = self.__add_to_formula(
                f"str.len(<start>) <= {html_constraints.maxlength}",
                formula,
                ISLa.AND,
            )
        if html_constraints.pattern is not None:
            # TODO
            pass

        return grammar, formula

    def __add_constraints_for_week(
        self, html_constraints: HTMLConstraints, use_datalist_options=False
    ) -> Tuple[str, str | None]:
        grammar = load_file_content(f"{pre_built_specifications_path}/week/week.bnf")
        formula = load_file_content(f"{pre_built_specifications_path}/week/week.isla")

        if use_datalist_options and html_constraints.list is not None:
            grammar = self.__replace_by_list_options(
                grammar, "week", html_constraints.list
            )
        if html_constraints.required is not None:
            formula = self.__add_to_formula("str.len(<start>) > 0", formula, ISLa.AND)
        if html_constraints.min is not None:
            [year_str, week_str] = html_constraints.min.split("-W")
            year = int(year_str)
            week = int(week_str)
            formula = self.__add_to_formula(
                f"str.to.int(<year>) >= {year} and str.to.int(<year>) + str.to.int(<week>) >= {year + week}",
                formula,
                ISLa.AND,
            )
        if html_constraints.max is not None:
            [year_str, week_str] = html_constraints.max.split("-W")
            year = int(year_str)
            week = int(week_str)
            formula = self.__add_to_formula(
                f"str.to.int(<year>) <= {year} and str.to.int(<year>) + str.to.int(<week>) <= {year + week}",
                formula,
                ISLa.AND,
            )
        # TODO: step not working because can not set modulo calculation in parantheses
        # if html_constraints.step is not None:
        #     formula = self.__add_to_formula(f'(str.to.int(<year>) + str.to.int(<month>)) mod {html_constraints.step} = 0',
        #                                     formula, ISLa.AND)

        return grammar, formula

    def __add_to_formula(
        self, additional_part: str, formula: str, operator: ISLa
    ) -> str:
        if formula is None or len(formula) == 0:
            return additional_part
        else:
            return f"{formula} {operator.value} {additional_part}"

    # TODO: decide which one to use. Should structure grammars in a way that disgarding the parts
    # after the list options does not matter. Otherwise we might get tokens that are unreachable and errors
    def __replace_by_list_options(
        self, grammar: str, option_identifier: str, list_options: List[str]
    ) -> str:
        head, sep, _ = grammar.partition(f"<{option_identifier}> ::= ")
        options = " | ".join(list_options)
        return f"{head}{sep}{options}"

    def __replace_by_any_string(
        self, grammar: str, option_identifier: str, replacement: str
    ) -> str:
        head, sep, _ = grammar.partition(f"<{option_identifier}> ::= ")
        return f"{head}{sep}{replacement}"

    def __grammar_string_to_dict(self, grammar: str) -> Dict[str, List[str]]:
        result: Dict[str, List[str]] = {}
        lines = grammar.split("\n")
        for line in lines:
            if line.startswith("<start> ::="):
                continue
            head, sep, tail = line.partition(" ::= ")
            result[head] = tail.split(" | ")

        return result

    def __grammar_dict_to_string(self, grammar_dict: Dict[str, List[str]]) -> str:
        result: List[str] = []
        for key, values in grammar_dict.items():
            line = f'{key} ::= {(" | ").join(values)}'
            result.append(line)

        return ("\n").join(result)

    def __combine_grammars_and_formulas(
        self,
        grammar: Dict[str, List[str]],
        other_grammar: Dict[str, List[str]],
        formula: str | None,
        other_formula: str | None,
        compOperator: str,
    ) -> Tuple[Dict[str, List[str]], str]:
        start_number = 1
        grammar, formula, next_nt_number = self.__convert_non_terminals(
            grammar, formula, start_number
        )
        other_grammar, other_formula, _ = self.__convert_non_terminals(
            other_grammar, other_formula, next_nt_number
        )

        nt1 = f"<nt{start_number}>"
        nt2 = f"<nt{next_nt_number}>"

        start = {"<start>": [f"{nt1} {nt2}"]}
        if "VALUE" in compOperator and "OTHER" in compOperator:
            compOperator = compOperator.replace("VALUE", nt1)
            compFormula = compOperator.replace("OTHER", nt2)
        else:
            compFormula = f"{nt1} {compOperator} {nt2}"

        return (start | grammar | other_grammar), (f" {ISLa.AND.value} ").join(
            filter(None, (f"({formula})", f"({other_formula})", f"({compFormula})"))
        )

    def __convert_non_terminals(
        self, grammar_dict: Dict[str, List[str]], formula: str | None, start_number
    ) -> Tuple[Dict[str, List[str]], str, int]:
        new_grammar = {}
        current_nt_number = start_number

        if formula is not None:
            formula = formula.replace("<start>", f"<nt{start_number}>")

        for key in grammar_dict.keys():
            new_key = f"<nt{current_nt_number}>"

            for values in grammar_dict.values():
                for idx, v in enumerate(values):
                    new_v = v.replace(key, new_key)
                    values[idx] = new_v

            new_grammar[new_key] = grammar_dict[key]
            if formula is not None:
                formula = formula.replace(key, new_key)

            current_nt_number += 1

        return new_grammar, formula, current_nt_number

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
