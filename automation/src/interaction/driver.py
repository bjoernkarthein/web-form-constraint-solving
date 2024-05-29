import sys
import threading
import time

from copy import deepcopy
from selenium.webdriver.chrome.service import Service
from seleniumwire import webdriver
from typing import List, Tuple

from src.analysis.constraint_extraction import (
    ConstraintCandidateFinder,
    SpecificationBuilder,
)
from src.analysis.html_analysis import (
    HTMLAnalyser,
    HTMLInputSpecification,
    HTMLRadioGroupSpecification,
)
from src.interaction.form_testing import FormTester, SpecificationParser
from src.proxy.interception import NetworkInterceptor
from src.utility.helpers import (
    binary_input_types,
    ConfigKey,
    clamp_to_range,
    free_service_resources,
    load_page,
    sub_to_service_messages,
    write_to_file,
    get_chromedriver_for_platform,
)


"""
Driver module

Handles all of the browser driver management.
"""


class TestAutomationDriver:
    """Test Automation class

    provides entry methods for automatic constraint extraction and form testing
    """

    def __init__(
        self, config: dict, url: str | None = None, setup_function=None, evaluation=None
    ) -> None:
        """Initialize the Test Automation

        Set options for selenium chrome driver and selenium wire proxy
        Initilaize web driver.

        Parameters:
        config (dict): The configuration as a json dict
        url (str | None): The url of the web page to test (default None; only required for extraction)
        setup_function: The function with selenium instructions to get to the actual web form on the page (default None)
        evaluation: The evaluation tracking instance (default None; only for evaluation purposes)
        """
        self.__config = config
        self.__setup_function = setup_function
        self.__url = url
        self.__html_only = True
        self.__evaluation = evaluation

        # Options for the chrome webdriver
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        chrome_options.add_argument("--lang=en")
        chrome_options.add_argument(
            "--disable-web-security"
        )  # TODO: This is needed for the unit tests. Is it okay to keep this?

        # Options for the seleniumwire proxy
        wire_options = {
            "disable_encoding": True,
            "request_storage": "memory",
            "request_storage_max_size": 100,  # Store no more than 100 requests in memory
        }

        self.__driver = webdriver.Chrome(
            service=Service(get_chromedriver_for_platform()),
            options=chrome_options,
            seleniumwire_options=wire_options,
        )

        # Set the timeout for a page load. This can be adjusted to be longer for pages with a lot of js files to instrument
        self.__driver.set_page_load_timeout(1000)

        self.__interceptor = NetworkInterceptor(self.__driver)
        self.web_driver = self.__driver

        if (
            ConfigKey.ANALYSIS.value in self.__config
            and ConfigKey.HTML_ONLY.value in self.__config[ConfigKey.ANALYSIS.value]
        ):
            self.__html_only = self.__config[ConfigKey.ANALYSIS.value][
                ConfigKey.HTML_ONLY.value
            ]

    def run_analysis(self) -> None:
        """Run the code analysis

        Connects to the server for status messages, starts instrumentation of JavaScript files,
        analyzes HTML and builds the specification from HTML and JavaScript validation.
        """

        # subscribe to server messages
        message_thread = threading.Thread(target=sub_to_service_messages, daemon=True)
        message_thread.start()

        # start network interception for instrumentation if the analysis is not HTML only
        if not self.__html_only:
            self.__interceptor.instrument_files()

        # load the page and optionally execute setup function to get to the actual web form
        load_page(self.__driver, self.__url)
        if self.__setup_function is not None:
            self.__setup_function(self)

        # build specification from HTML validation
        html_input_specifications = self.__analyse_html(self.__driver.page_source)
        if self.__html_only:
            self.__build_specification(html_input_specifications)
            self.__exit()

        # extract additional JavaScript constrants
        self.__start_constraint_extraction(html_input_specifications)

        self.__exit()

    def run_test(
        self, specification_file: str | None = None, report_path: str | None = None
    ) -> None:
        """Start the testing of a web form.

        Parses either the extracted specification or a custom, user-defined spec and initiates the test.

        Parameters:
        specification_file (str | None): The file path to a valid specification file (default None; See "automation\pre-built-specifications\specification_example.json" for an example)
        report_path (str |  None): The path for the generated report file (default None; only for evaluation)
        """

        # parse specification file
        specification_parser = SpecificationParser(specification_file)
        spec, specification_dir = specification_parser.parse()
        if spec is None:
            self.__exit()

        # start value generation and form testing
        url = spec["url"]
        form_tester = FormTester(
            self.__driver, url, spec, specification_dir, self.__config, report_path
        )
        form_tester.start_generation(self.__setup_function, self)

        self.__exit()

    def __analyse_html(
        self, html_string: str
    ) -> List[HTMLInputSpecification | HTMLRadioGroupSpecification]:
        """Analyse the HTML content of the web page.

        Selects a web form and extract the built-in HTML constraints for it's inputs.

        Parameters:
        html_string (str): The snapchot of the DOM to analyze as a string

        Returns:
        List[HTMLInputSpecification | HTMLRadioGroupSpecification]: The specification for all form fields including the built-in HTML constraints
        """
        self.__html_analyser = HTMLAnalyser(html_string, self.__evaluation)
        (form, access) = self.__html_analyser.select_form()

        # if the page does not contain a form we exit
        if form is None or access is None:
            self.__exit()

        # colecting HTML constraints
        html_constraints = self.__html_analyser.extract_static_constraints(form)
        if html_constraints is None:
            self.__exit()

        return html_constraints

    def __start_constraint_extraction(
        self,
        html_specifications: List[HTMLInputSpecification | HTMLRadioGroupSpecification],
    ) -> None:
        """Start the extraction of client-side validation constraints for a set of specified HTML inputs.

        Starts with the identified HTML constraints for one input field and iteratively builds a specification, looks for new JavaScript constraint candidates,
        adds them to the current specification for the field and starts over.
        This is done for as many rounds per input as specified in the config and until all input fields are analyzed.

        Parameters:
        html_specifications (List[HTMLInputSpecification | HTMLRadioGroupSpecification]): List of specifications for all form fields
        """

        analysis_rounds = self.__config[ConfigKey.ANALYSIS.value][
            ConfigKey.ANALYSIS_ROUNDS.value
        ]
        analysis_rounds = clamp_to_range(analysis_rounds, 1)
        stop_on_first_success = self.__config[ConfigKey.ANALYSIS.value][
            ConfigKey.STOP_ON_SUCCESS.value
        ]

        self.__constraint_candidate_finder = ConstraintCandidateFinder(
            self.__driver,
            self.__html_analyser.submit_element,
            self.__interceptor,
            stop_on_first_success,
            self.__exit,
            self.__evaluation,
        )

        next_specifications: (
            List[
                Tuple[
                    HTMLInputSpecification | HTMLRadioGroupSpecification,
                    str,
                    str | None,
                ]
            ]
            | None
        ) = None

        for _ in range(analysis_rounds):
            specifications = next_specifications or self.__build_specification(
                html_specifications
            )
            next_specifications = []

            for elem in specifications:
                spec, grammar, formula = elem
                self.__constraint_candidate_finder.set_valid_value_sequence(
                    spec, grammar, formula, self.__magic_value_amount
                )

            for elem in specifications:
                spec, grammar, formula = elem
                constraint_candidates = self.__constraint_candidate_finder.get_constraint_candidates_for_value_sequence(
                    spec
                )

                # TODO: When to stop? How do I not apply the same candidates twice?
                (
                    grammar,
                    formula,
                ) = self.__specification_builder.add_constraints_to_current_specification(
                    spec.reference, spec.type, constraint_candidates
                )

                next_specifications.append((spec, grammar, formula))

    def __build_specification(
        self,
        html_specifications: List[HTMLInputSpecification | HTMLRadioGroupSpecification],
    ) -> List[
        Tuple[HTMLInputSpecification | HTMLRadioGroupSpecification, str, str | None]
    ]:
        """Converts all constraints to a human-readable and editable specification file for the whole form.

        Paramaters:
        html_specifications (List[HTMLInputSpecification | HTMLRadioGroupSpecification]): All html constraints for all input fields

        Returns:
        List[Tuple[HTMLInputSpecification | HTMLRadioGroupSpecification, str, str | None]]: A List that contains a tuple
        for each input field with the original spec, the grammar and the formula

        """
        result = []

        self.__specification_builder = SpecificationBuilder()
        use_datalist_options = self.__config[ConfigKey.GENERATION.value][
            ConfigKey.USE_DATALIST_OPTIONS.value
        ]
        magic_value_amount = self.__config[ConfigKey.ANALYSIS.value][
            ConfigKey.MAGIC_VALUE_AMOUNT.value
        ]
        self.__magic_value_amount = clamp_to_range(magic_value_amount, 1)

        next_file_index = 1
        form_specification = {
            "url": self.__url,
            "controls": [],
            "submit": self.__html_analyser.submit_element.get_as_dict(),
        }

        for specification in html_specifications:
            grammar_with_required = None
            formula_with_required = None

            if isinstance(specification, HTMLInputSpecification):

                # more diversity for magic values that are not binary
                spec_with_required = deepcopy(specification)
                if specification.constraints.type not in binary_input_types:
                    spec_with_required.constraints.required = True

                (
                    grammar_with_required,
                    formula_with_required,
                ) = self.__specification_builder.create_specification_for_html_input(
                    spec_with_required, next_file_index, use_datalist_options
                )

                (
                    grammar,
                    formula,
                ) = self.__specification_builder.create_specification_for_html_input(
                    specification, next_file_index, use_datalist_options
                )
            else:
                (
                    grammar,
                    formula,
                ) = self.__specification_builder.create_specification_for_html_radio_group(
                    specification, next_file_index
                )

            (
                grammar_file,
                formula_file,
            ) = self.__specification_builder.write_specification_to_file(
                str(next_file_index), grammar, formula
            )

            form_specification["controls"].append(
                specification.get_representation(grammar_file, formula_file)
            )
            next_file_index += 1
            result.append(
                (
                    specification,
                    grammar_with_required or grammar,
                    formula_with_required or formula,
                )
            )

        write_to_file("specification/specification.json", form_specification)
        return result

    def __exit(self, exit_code: int | None = None) -> None:
        """Free all resources and exit

        Parameters:
        exit_code (int | None): The code with which to exit the execution
        """

        free_service_resources()
        self.__driver.quit()

        # Saving measurements for evaluation
        if self.__evaluation is not None:
            self.__evaluation.save_profiling()
            self.__evaluation.save_stat(
                "html_files_instrumented",
                self.__interceptor.html_files_instrumented or 0,
            )
            self.__evaluation.save_stat(
                "js_files_instrumented", self.__interceptor.js_files_instrumented or 0
            )
            service_stats = self.__evaluation.get_service_stats()
            self.__evaluation.merge_stats(service_stats)
            self.__evaluation.write_stats_to_file()
            self.__evaluation.save_specification()

        sys.exit(exit_code)
