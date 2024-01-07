import json
import time

from pathlib import Path
from selenium.webdriver import Chrome
from typing import Dict, List

from html_analysis import HTMLInputSpecification, HTMLRadioGroupSpecification, HTMLElementReference
from input_generation import InputGenerator
from proxy import ResponseInspector
from utility import ConfigKey, load_file_content, load_page, write_to_web_element_by_reference_with_clear, click_web_element_by_reference


class SpecificationParser:
    def __init__(self, specification_file_path: str) -> None:
        self.__specification_file_path = specification_file_path

    def parse(self) -> (Dict | None, str):
        file_name = 'specification/specification.json' if self.__specification_file_path is None else self.__specification_file_path
        parent_dir = str(Path(file_name).parent.absolute())
        specification_str = load_file_content(file_name)
        if specification_str == '':
            print(
                'No existing specification file found. Either pass a path to a valid specification file via the -s flag or run the analyse.py to extract a specification automatically.\nRun test.py -h for help.')
            return None, ""

        try:
            specification = json.loads(specification_str)
        except json.JSONDecodeError as e:
            print('Error parsing specification file')
            print(e)
            return None, ""

        if self.__specification_file_path is not None and not self.__check_specification_format(specification):
            print('The given specification file does not have the correct format')
            return None, ""

        return specification, parent_dir

    def __check_specification_format(self, specification: Dict) -> bool:
        # TODO
        return True


class ValueGenerationSpecification:
    def __init__(self, input_spec: HTMLInputSpecification | HTMLRadioGroupSpecification, type: str, grammar: str, formula: str | None = None):
        self.input_spec = input_spec
        self.type = type
        self.grammar = grammar
        self.formula = formula

    def __str__(self):
        return f'ValueGenenerationSpecification:\nspec: {self.input_spec}\ngrammar: {self.grammar}\nformula: {self.formula}'


class FormTester:
    def __init__(self, driver: Chrome, url: str, specification: Dict, specification_directory: str, config: Dict) -> None:
        self.__driver = driver
        self.__repetitions = config[ConfigKey.TESTING.value][ConfigKey.REPETITIONS.value]
        self.__specification = specification
        self.__specification_directory = specification_directory
        self.__url = url

    def start_generation(self) -> None:
        inspector = ResponseInspector(self.__driver)
        # TODO: start inspecting

        self.__submit_element_reference = self.__get_submit_element_from_json(
            self.__specification)

        self.__generation_templates: List[ValueGenerationSpecification] = []
        for json_spec in self.__specification['controls']:
            self.__generation_templates.append(self.__convert_json_to_specification(
                json_spec))

        generator = InputGenerator()
        # TODO generate all values in advance for better diversity and just fill in afterwards?
        for _ in range(self.__repetitions):
            load_page(self.__driver, self.__url)
            self.__fill_form_with_values_and_submit(generator)

    def __get_submit_element_from_json(self, spec: Dict) -> HTMLElementReference:
        return HTMLElementReference(
            spec['submit']['access_method'], spec['submit']['access_value'])

    def __convert_json_to_specification(self, control: Dict) -> ValueGenerationSpecification:
        grammar = load_file_content(
            f'{self.__specification_directory}/{control["grammar"]}')
        formula = load_file_content(
            f'{self.__specification_directory}/{control["formula"]}')
        type = control['type']

        if control['type'] == 'radio':
            name = control['reference']['access_value']
            options = control['options']
            options = list(
                map(lambda o: (HTMLElementReference(o['reference']['access_method'], o['reference']['access_value']), o['value']), options))
            element_spec = HTMLRadioGroupSpecification(name, options)
        else:
            element_reference = HTMLElementReference(
                control['reference']['access_method'], control['reference']['access_value'])
            element_spec = HTMLInputSpecification(element_reference)

        return ValueGenerationSpecification(element_spec, type, grammar, formula if formula != "" else None)

    # TODO: handle invalid value generation here
    def __fill_form_with_values_and_submit(self, generator: InputGenerator) -> None:
        for template in self.__generation_templates:
            value = generator.generate_valid_inputs(
                template.grammar, template.formula)[0]
            write_to_web_element_by_reference_with_clear(
                self.__driver, template.type, template.input_spec.reference, value)

        click_web_element_by_reference(
            self.__driver, self.__submit_element_reference)