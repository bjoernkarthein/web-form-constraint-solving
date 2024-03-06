import json
import os
import random

from pathlib import Path
from selenium.webdriver import Chrome
from seleniumwire.request import Request, Response
from tabulate import tabulate
from typing import Dict, List, Tuple

from src.analysis.html_analysis import (
    HTMLInputSpecification,
    HTMLRadioGroupSpecification,
    HTMLElementReference,
)
from src.generation.input_generation import InputGenerator, GeneratedValue, ValidityEnum
from src.proxy.interception import (
    NetworkInterceptor,
    RequestScanner,
    submission_interception_header,
)
from src.utility.helpers import (
    ConfigKey,
    InputType,
    load_file_content,
    load_page,
    write_to_web_element_by_reference_with_clear,
    write_to_file,
    click_web_element_by_reference,
    clamp_to_range,
    clear_value_mapping,
)


class SpecificationParser:
    def __init__(self, specification_file_path: str) -> None:
        self.__specification_file_path = specification_file_path

    def parse(self) -> Tuple[Dict | None, str]:
        file_name = (
            "specification/specification.json"
            if self.__specification_file_path is None
            else self.__specification_file_path
        )
        parent_dir = str(Path(file_name).parent.absolute())
        specification_str = load_file_content(file_name)
        if specification_str == "":
            print(
                "No existing specification file found. Either pass a path to a valid specification file via the -s flag or run the analyse.py to extract a specification automatically.\nRun test.py -h for help."
            )
            return None, ""

        try:
            specification = json.loads(specification_str)
        except json.JSONDecodeError as e:
            print("Error parsing specification file")
            print(e)
            return None, ""

        if (
            self.__specification_file_path is not None
            and not self.__check_specification_format(specification)
        ):
            print("The given specification file does not have the correct format")
            return None, ""

        return specification, parent_dir

    def __check_specification_format(self, specification: Dict) -> bool:
        print("Checking provided spec file")
        if "url" not in specification:
            print("url missing")
            return False
        if "controls" not in specification:
            print("no controls specified")
            return False
        if "submit" not in specification:
            print("submit element not specified")
            return False

        # TODO check if it is a valid url?

        submit_ref = specification["submit"]
        if not self.__is_valid_reference(submit_ref):
            return False

        controls = specification["controls"]
        for control in controls:
            required_keys = set(["type", "reference", "grammar", "formula"])
            contained_keys = set(control.keys())
            if required_keys != contained_keys or self.__is_valid_reference(
                control["reference"]
            ):
                print("control is missing required fields")
                return False

            # TODO: Check if the provided value for formula and grammar is a file?

        return True

    def __is_valid_reference(self, ref: Dict) -> bool:
        if "access_method" not in ref or "access_value" not in ref:
            print("element reference has wrong format")
            return False

        return True


class ValueGenerationSpecification:
    def __init__(
        self,
        input_spec: HTMLInputSpecification | HTMLRadioGroupSpecification,
        type: str,
        grammar: str,
        formula: str | None = None,
    ):
        self.input_spec = input_spec
        self.type = type
        self.grammar = grammar
        self.formula = formula

    def __str__(self):
        return f"ValueGenenerationSpecification:\nspec: {self.input_spec}\ngrammar: {self.grammar}\nformula: {self.formula}"


class FormTester:
    def __init__(
        self,
        driver: Chrome,
        url: str,
        specification: Dict,
        specification_directory: str,
        config: Dict,
    ) -> None:
        self.__block_all_requests = config[ConfigKey.TESTING.value][
            ConfigKey.BLOCK_ALL_REQUESTS.value
        ]
        self.__block_successful_submissions = config[ConfigKey.TESTING.value][
            ConfigKey.BLOCK_SUBMISSION.value
        ]
        self.__driver = driver

        self.__valid = None
        self.__invalid = None
        repetition = config[ConfigKey.TESTING.value][ConfigKey.REPETITIONS.value]
        if isinstance(repetition, int):
            total = clamp_to_range(repetition, 1, None)
        elif isinstance(repetition, Dict):
            total = repetition[ConfigKey.TOTAL.value]
            valid = total = repetition[ConfigKey.VALID.value]
            valid = clamp_to_range(valid, 1, None)
            invalid = repetition[ConfigKey.INVALID.value]
            invalid = clamp_to_range(invalid, 1, None)

            if valid + invalid != total:
                raise ValueError(
                    f"The specified amount for valid and invalid form instances has to add up to the total.\nGot valid: {valid}, invalid: {invalid}, total: {total}"
                )

            self.__valid = valid
            self.__invalid = invalid

        self.__repetitions = total
        self.__specification = specification
        self.__specification_directory = specification_directory
        self.__url = url

    def start_generation(self, setup_function=None) -> None:
        self.__interceptor = NetworkInterceptor(self.__driver)
        if self.__block_successful_submissions:
            self.__interceptor.scan_for_form_submission()

        self.__submit_element_reference = self.__get_submit_element_from_json(
            self.__specification
        )

        self.__generation_templates: List[ValueGenerationSpecification] = []
        for json_spec in self.__specification["controls"]:
            self.__generation_templates.append(
                self.__convert_json_to_specification(json_spec)
            )

        generator = InputGenerator()
        self.__test_monitor = TestMonitor(
            self.__driver, self.__submit_element_reference, self.__interceptor
        )

        # TODO generate all values in advance for better diversity and just fill in afterwards?
        if self.__valid is None or self.__invalid is None:
            for _ in range(self.__repetitions):
                self.__prepare_next_form_filling(setup_function)
                self.__fill_form_with_values_and_submit(generator)
        else:
            for _ in range(self.__valid):
                self.__prepare_next_form_filling(setup_function)
                self.__fill_form_with_values_and_submit(generator)

            for _ in range(self.__invalid):
                self.__prepare_next_form_filling(setup_function)
                self.__fill_form_with_values_and_submit(generator, ValidityEnum.INVALID)

        self.__test_monitor.process_saved_submissions()

    def __prepare_next_form_filling(self, setup_function=None) -> None:
        clear_value_mapping()
        load_page(self.__driver, self.__url)
        if setup_function is not None:
            setup_function()

    def __get_submit_element_from_json(self, spec: Dict) -> HTMLElementReference:
        return HTMLElementReference(
            spec["submit"]["access_method"], spec["submit"]["access_value"]
        )

    def __convert_json_to_specification(
        self, control: Dict
    ) -> ValueGenerationSpecification:
        grammar = load_file_content(
            f'{self.__specification_directory}/{control["grammar"]}'
        )
        formula = load_file_content(
            f'{self.__specification_directory}/{control["formula"]}'
        )
        type = control["type"]

        if control["type"] == InputType.RADIO.value:
            name = control["reference"]["access_value"]
            options = control["options"]
            options = list(
                map(
                    lambda o: (
                        HTMLElementReference(
                            o["reference"]["access_method"],
                            o["reference"]["access_value"],
                        ),
                        o["value"],
                    ),
                    options,
                )
            )
            element_spec = HTMLRadioGroupSpecification(name, options)
        else:
            element_reference = HTMLElementReference(
                control["reference"]["access_method"],
                control["reference"]["access_value"],
            )
            element_spec = HTMLInputSpecification(element_reference)

        return ValueGenerationSpecification(
            element_spec, type, grammar, formula if formula != "" else None
        )

    def __fill_form_with_values_and_submit(
        self, generator: InputGenerator, validity: ValidityEnum = ValidityEnum.VALID
    ) -> None:
        values: List[GeneratedValue] = []
        validities = [ValidityEnum.VALID] * len(self.__generation_templates)

        # If we want to also generate invalid values we choose between 1 and n elements
        # to be invalid for a for with n input fields
        if validity == ValidityEnum.INVALID:
            num_changes = random.randint(1, len(validities))
            indices_to_change = random.sample(range(len(validities)), num_changes)
            for idx in indices_to_change:
                validities[idx] = ValidityEnum.INVALID

        for idx, template in enumerate(self.__generation_templates):
            # TODO: Error handling
            generated_value = generator.generate_inputs(
                template.grammar, template.formula, validities[idx]
            )[0]
            values.append(generated_value)

            write_to_web_element_by_reference_with_clear(
                self.__driver,
                template.type,
                template.input_spec.reference,
                generated_value.value,
                False,
            )

        self.__test_monitor.attempt_submit_and_save_response(values)


class TestMonitor:
    def __init__(
        self,
        driver: Chrome,
        submit_element: HTMLElementReference,
        interceptor: NetworkInterceptor,
    ) -> None:
        self.__driver = driver
        self.__interceptor = interceptor
        self.__request_scanner = RequestScanner()
        self.__saved_submissions: List[Tuple[List[GeneratedValue], Response | None]] = (
            []
        )
        self.__submit_element = submit_element

    def attempt_submit_and_save_response(
        self, current_values: List[GeneratedValue]
    ) -> None:
        str_values = list(map(lambda v: v.value, current_values))
        self.__interceptor.generated_values = str_values
        click_web_element_by_reference(self.__driver, self.__submit_element)

        response = None
        all_requests: List[Request] = self.__driver.requests
        # TODO: Only look at the interesting subset of requests
        for request in all_requests:
            if self.__request_scanner.all_values_in_form_request(request, str_values):
                response = request.response

        self.__saved_submissions.append((current_values, response))

    def process_saved_submissions(self) -> None:
        result = {}
        successful = 0
        failed = 0
        for i in range(len(self.__saved_submissions)):
            values, response = self.__saved_submissions[i]
            response_str = ""
            if response is None:
                response_str = "Submission did not cause any outgoing requests including the entered data."
                failed += 1
            elif response.headers[submission_interception_header] is not None:
                response_str = (
                    "Form was submitted successfully but the request was blocked."
                )
                successful += 1
            else:
                response_str = f"{response.status_code} {response.reason}"
                successful += 1

            result[f"test_round_{i + 1}"] = {
                "generated_values": list(map(lambda v: str(v), values)),
                "server_response": response_str,
            }

        os.makedirs("report", exist_ok=True)
        write_to_file("report/results.json", result)
        self.__print_summary(successful, failed)

    def __print_summary(self, successful: int, failed: int) -> None:
        print("\nSummary:")
        print("Total Form Instances generated:", len(self.__saved_submissions), "\n")
        print(
            tabulate(
                [["Successful", successful], ["Failed", failed]],
                headers=["Status (Submission)", "Amount"],
            ),
            "\n",
        )
        print(
            "For a more detailed report refer to 'automation/report/results.json'",
            "\n",
        )
