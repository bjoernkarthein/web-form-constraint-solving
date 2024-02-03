import json

from pathlib import Path
from selenium.webdriver import Chrome
from seleniumwire.request import Request, Response
from tabulate import tabulate
from typing import Dict, List, Tuple

from html_analysis import (
    HTMLInputSpecification,
    HTMLRadioGroupSpecification,
    HTMLElementReference,
)
from input_generation import InputGenerator, GeneratedValue, ValidityEnum
from proxy import NetworkInterceptor, RequestScanner, submission_interception_header
from utility import (
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

    def parse(self) -> (Dict | None, str):
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
        # TODO
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
        self.__block_successful_submissions = config[ConfigKey.TESTING.value][
            ConfigKey.BLOCK_SUBMISSION.value
        ]
        self.__driver = driver
        repetitions = config[ConfigKey.TESTING.value][ConfigKey.REPETITIONS.value]
        self.__repetitions = clamp_to_range(repetitions, 1, None)
        self.__specification = specification
        self.__specification_directory = specification_directory
        self.__url = url

    def start_generation(self) -> None:
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
        for _ in range(self.__repetitions):
            clear_value_mapping()
            load_page(self.__driver, self.__url)
            self.__fill_form_with_values_and_submit(generator)

        self.__test_monitor.process_saved_submissions()

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

    # TODO: handle invalid value generation here
    def __fill_form_with_values_and_submit(self, generator: InputGenerator) -> None:
        values: List[GeneratedValue] = []
        for template in self.__generation_templates:
            # TODO: Error handling
            generated_value = generator.generate_inputs(
                template.grammar, template.formula
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
        self.__saved_submissions: List[
            Tuple[List[GeneratedValue], Response | None]
        ] = []
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
            "For a more detailed report refer to 'automation/src/report/results.json'",
            "\n",
        )
