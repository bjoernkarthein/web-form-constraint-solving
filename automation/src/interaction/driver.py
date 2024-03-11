import os
import threading
import sys

import cProfile
import io
import pandas as pd
import pstats

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
    FormObserver,
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
)


chrome_driver_path = "chromedriver/windows/chromedriver.exe"
# chrome_driver_path = "chromedriver/linux/chromedriver"
chrome_driver_abs_path = os.path.abspath(chrome_driver_path)
disable_csp_extension_path = "chromedriver/chrome-csp-disable.crx"
disable_csp_extension_path = os.path.abspath(disable_csp_extension_path)


"""
Driver module

Handles all of the browser driver management.
"""


class TestAutomationDriver:
    """Test Automation class

    ...
    """

    def __init__(
        self,
        config: dict,
        url: str = None,
        setup_function=None,
        profiler=None,
        file=None,
    ) -> None:
        self.__pr = None
        if profiler is not None:
            self.__pr = profiler
            self.__file = file
            self.__pr.enable()

        """Initialize the Test Automation

        Set options for selenium chrome driver and selenium wire proxy
        Initilaize web driver.
        """
        self.__config = config
        self.__setup_function = setup_function
        self.__url = url

        # Options for the chrome webdriver
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_extension(disable_csp_extension_path)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        chrome_options.add_argument("--lang=en")

        # Options for the seleniumwire proxy
        wire_options = {"disable_encoding": True}

        self.__driver = webdriver.Chrome(
            service=Service(chrome_driver_abs_path),
            options=chrome_options,
            seleniumwire_options=wire_options,
        )
        self.__interceptor = NetworkInterceptor(self.__driver)

        self.web_driver = self.__driver

        html_only = True
        if (
            ConfigKey.ANALYSIS.value in self.__config
            and ConfigKey.HTML_ONLY.value in self.__config[ConfigKey.ANALYSIS.value]
        ):
            html_only = self.__config[ConfigKey.ANALYSIS.value][
                ConfigKey.HTML_ONLY.value
            ]

        if not html_only:
            self.__interceptor.instrument_files()

    def run_analysis(self) -> None:
        # subscribe to server messages
        # message_thread = threading.Thread(
        #     target=sub_to_service_messages, daemon=True
        # )
        # message_thread.start()

        load_page(self.__driver, self.__url)
        # self.__interceptor.block_form_submission()

        if self.__setup_function is not None:
            self.__setup_function(self)

        html_input_specifications = self.__analyse_html(self.__driver.page_source)
        self.__start_constraint_extraction(html_input_specifications)

        self.__exit()

    # TODO: Selection dependent inputs during testing?
    def run_test(
        self, specification_file: str | None = None, report_path: str | None = None
    ) -> None:
        specification_parser = SpecificationParser(specification_file)
        spec, specification_dir = specification_parser.parse()
        if spec is None:
            self.__exit()

        url = spec["url"]
        form_tester = FormTester(
            self.__driver, url, spec, specification_dir, self.__config, report_path
        )
        form_tester.start_generation()

        self.__exit()

    def __analyse_html(
        self, html_string: str
    ) -> List[HTMLInputSpecification | HTMLRadioGroupSpecification]:
        """Analyse the HTML content of the web page.

        Select a web form and extract the built-in HTML constraints for it's inputs.
        """
        self.__html_analyser = HTMLAnalyser(html_string)
        (form, access) = self.__html_analyser.select_form()

        if form is None or access is None:
            self.__exit()

        # TODO check for form changes and handle
        self.__form_observer = FormObserver(form, access)

        html_constraints = self.__html_analyser.extract_static_constraints(form)
        if html_constraints is None:
            self.__exit()

        return html_constraints

    # TODO refactor to not be that complex - is this the right class?
    def __start_constraint_extraction(
        self,
        html_specifications: List[HTMLInputSpecification | HTMLRadioGroupSpecification],
    ) -> None:
        """Start the extraction of client-side validation constraints for a set of specified HTML inputs."""

        html_only = self.__config[ConfigKey.ANALYSIS.value][ConfigKey.HTML_ONLY.value]
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
        )

        specifications = self.__build_html_specification(html_specifications)
        if html_only:
            self.__exit()

        for elem in specifications:
            spec, grammar, formula = elem
            self.__constraint_candidate_finder.set_valid_value_sequence(
                spec, grammar, formula
            )

        self.__constraint_candidate_finder.fill_with_valid_values()

        for elem in specifications:
            spec, grammar, formula = elem
            previous_constraints = {"candidates": []}

            for _ in range(analysis_rounds):
                constraint_candidates = (
                    self.__constraint_candidate_finder.find_js_constraint_candidates(
                        spec, grammar, formula, self.__magic_value_amount
                    )
                )

                # TODO: When to stop? How do I not apply the same candidates twice?

                if len(constraint_candidates.candidates) == 0:
                    break

                if constraint_candidates == previous_constraints:
                    break

                (
                    grammar,
                    formula,
                ) = self.__specification_builder.add_constraints_to_current_specification(
                    spec.reference, spec.constraints.type, constraint_candidates
                )

                previous_constraints = constraint_candidates

    # TODO: refactor to not be this complex - is this the right class?
    def __build_html_specification(
        self,
        html_specifications: List[HTMLInputSpecification | HTMLRadioGroupSpecification],
    ) -> List[Tuple[HTMLInputSpecification | HTMLInputSpecification, str, str | None]]:
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
            if isinstance(specification, HTMLInputSpecification):

                # more diversity for magic values that are not binary
                grammar_with_required = None
                formula_with_required = None

                spec_with_required = deepcopy(specification)
                if specification.constraints.type not in binary_input_types:
                    spec_with_required.constraints.required = True

                (
                    grammar_with_required,
                    formula_with_required,
                ) = self.__specification_builder.create_specification_for_html_input(
                    spec_with_required, use_datalist_options
                )

                (
                    grammar,
                    formula,
                ) = self.__specification_builder.create_specification_for_html_input(
                    specification, use_datalist_options
                )
            else:
                (
                    grammar,
                    formula,
                ) = self.__specification_builder.create_specification_for_html_radio_group(
                    specification
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

    def __exit(self, exit_code: int = None) -> None:
        """Free all resources and exit"""
        # free_service_resources()
        self.__driver.quit()

        # write performance to file
        if self.__pr is not None:
            self.__pr.disable()
            csv = self.prof_to_csv(self.__pr)
            with open(
                f"evaluation/{self.__file}_stats.csv", "w+", encoding="utf-8"
            ) as f:
                f.write(csv)

            self.clean_csv(f"evaluation/{self.__file}_stats")
            self.get_isla_csv(f"evaluation/{self.__file}_stats")

        sys.exit(exit_code)

    def prof_to_csv(self, pr: cProfile.Profile) -> None:
        out_stream = io.StringIO()
        stats = pstats.Stats(pr, stream=out_stream)
        stats.sort_stats(pstats.SortKey.CUMULATIVE)
        stats.print_stats()
        result = out_stream.getvalue()

        result = "ncalls" + result.split("ncalls")[-1]
        lines = [",".join(line.rstrip().split(None, 5)) for line in result.split("\n")]
        lines = list(filter(lambda l: l != "", lines))
        return "\n".join(lines)

    def clean_csv(self, file: str) -> None:
        df = pd.read_csv(f"{file}.csv", encoding="utf-8")
        my_functions = df["filename:lineno(function)"].str.contains(
            "invariant-based-web-form-testing"
        )
        df = df[my_functions]
        df.reset_index(drop=True, inplace=True)

        df.to_csv(f"{file}_clean.csv", index=False)

    def get_isla_csv(self, file: str) -> None:
        df = pd.read_csv(f"{file}.csv", encoding="utf-8")
        my_functions = df["filename:lineno(function)"].str.contains("isla")
        df = df[my_functions]
        df.reset_index(drop=True, inplace=True)

        df.to_csv(f"{file}_isla.csv", index=False)
