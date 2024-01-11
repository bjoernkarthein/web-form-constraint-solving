import sys
import time

from selenium.common.exceptions import InvalidArgumentException
from selenium.webdriver.chrome.service import Service
from seleniumwire import webdriver
from typing import List

from constraint_extraction import ConstraintCandidateFinder, SpecificationBuilder
from form_testing import FormTester, SpecificationParser
from html_analysis import HTMLAnalyser, HTMLInputSpecification, FormObserver, HTMLRadioGroupSpecification
from proxy import NetworkInterceptor, ResponseInspector
from utility import binary_input_types, ConfigKey, load_page, clean_instrumentation_resources, write_to_file

# chrome_driver_path = '../chromedriver/windows/chromedriver.exe'
chrome_driver_path = '../chromedriver/linux/chromedriver'

"""
Driver module

Handles all of the browser driver management.
"""


class TestAutomationDriver:
    """Test Automation class

    ...
    """

    def __init__(self, config: dict, url: str = None) -> None:
        """Initialize the Test Automation

        Set options for selenium chrome driver and selenium wire proxy
        Initilaize web driver.
        """
        self.__config = config
        self.__url = url

        # Options for the chrome webdriver
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option(
            'excludeSwitches', ['enable-logging'])
        chrome_options.add_argument('--lang=en')

        # Options for the selenium wire proxy
        wire_options = {
            'disable_encoding': True
        }

        self.__driver = webdriver.Chrome(
            service=Service(chrome_driver_path),
            options=chrome_options,
            seleniumwire_options=wire_options
        )

    def run_analysis(self) -> None:
        html_only = self.__config[ConfigKey.ANALYSIS.value][ConfigKey.HTML_ONLY.value]

        if not html_only:
            interceptor = NetworkInterceptor(self.__driver)
            interceptor.instrument_files()

        inspector = ResponseInspector(self.__driver)
        # TODO Start inspecting

        load_page(self.__driver, self.__url)
        html_input_specifications = self.__analyse_html(
            self.__driver.page_source)
        self.__start_constraint_extraction(html_input_specifications)

        self.__exit()

    def run_test(self, specification_file: str | None = None) -> None:
        specification_parser = SpecificationParser(specification_file)
        spec, specification_dir = specification_parser.parse()
        if spec is None:
            self.__exit()

        url = spec['url']
        form_tester = FormTester(
            self.__driver, url, spec, specification_dir, self.__config)
        form_tester.start_generation()

        self.__exit()

    def __analyse_html(self, html_string: str) -> List[HTMLInputSpecification | HTMLRadioGroupSpecification]:
        """Analyse the HTML content of the web page.

        Select a web form and extract the built-in HTML constraints for it's inputs.
        """
        self.__html_analyser = HTMLAnalyser(html_string)
        (form, access) = self.__html_analyser.select_form()

        if form is None or access is None:
            self.__exit()

        # TODO check for form changes and handle
        self.__form_observer = FormObserver(form, access)

        html_constraints = self.__html_analyser.extract_static_constraints(
            form)
        if html_constraints is None:
            self.__exit()

        return html_constraints

    def __start_constraint_extraction(self, html_specifications: List[HTMLInputSpecification | HTMLRadioGroupSpecification]) -> None:
        """Start the extraction of client-side validation constraints for a set of specified HTML inputs."""
        html_only = self.__config[ConfigKey.ANALYSIS.value][ConfigKey.HTML_ONLY.value]

        self.__constraint_candidate_finder = ConstraintCandidateFinder(
            self.__driver, self.__html_analyser.submit_element)
        self.__generate_valid_html_magic_values(html_specifications)

        if html_only:
            self.__exit()

        self.__constraint_candidate_finder.find_js_constraint_candidates(
            html_specifications)

        time.sleep(5)
        self.__exit()

    # TODO: refactor to not be this complex
    def __generate_valid_html_magic_values(self, html_specifications: List[HTMLInputSpecification | HTMLRadioGroupSpecification]) -> None:
        self.__specification_builder = SpecificationBuilder()
        use_datalist_options = self.__config[ConfigKey.GENERATION.value][ConfigKey.USE_DATALIST_OPTIONS.value]
        magic_value_amount = self.__config[ConfigKey.ANALYSIS.value][ConfigKey.MAGIC_VALUE_AMOUNT.value]

        next_file_index = 1
        form_specification = {'url': self.__url, 'controls': [
        ], 'submit': self.__html_analyser.submit_element.get_as_dict()}

        for specification in html_specifications:
            if isinstance(specification, HTMLInputSpecification):
                # more diversity for magic values that are not binary
                if specification.contraints.type not in binary_input_types:
                    specification.contraints.required = True

                grammar, formula = self.__specification_builder.create_specification_for_html_input(
                    specification, use_datalist_options)
            else:
                grammar, formula = self.__specification_builder.create_specification_for_html_radio_group(
                    specification)

            grammar_file, formula_file = self.__specification_builder.write_specification_to_file(
                str(next_file_index), grammar, formula)
            form_specification['controls'].append(
                specification.get_representation(grammar_file, formula_file))
            next_file_index += 1

            self.__constraint_candidate_finder.set_magic_value_sequence(
                specification, grammar, formula, magic_value_amount)

        write_to_file('specification/specification.json', form_specification)

    def __exit(self, exit_code=None) -> None:
        """Free all resources and exit"""

        # clean_instrumentation_resources()
        self.__driver.quit()
        sys.exit(exit_code)
