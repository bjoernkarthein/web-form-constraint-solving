import json

from pathlib import Path
from selenium.webdriver import Chrome
from selenium.webdriver.remote.webelement import WebElement
from typing import Dict, List

from html_analysis import HTMLInputSpecification, HTMLRadioGroupSpecification, HTMLElementReference
from proxy import ResponseInspector
from utility import load_file_content, get_web_element_by_reference, get_web_elements_by_reference


class SpecificationParser:
    def __init__(self, specification_file_path: str) -> None:
        self.__specification_file_path = specification_file_path

    def parse(self) -> (Dict | None, str):
        file_name = 'specification/specification.json' if self.__specification_file_path is None else self.__specification_file_path
        parent_dir = str(Path(file_name).parent.absolute())
        specification_str = load_file_content(file_name)
        if specification_str == '':
            print(
                'No existing specification file found. Either pass a path to a valid specification file via the -s flag or run the analyse.py to extract a specification automatically.')
            return None

        try:
            specification = json.loads(specification_str)
        except json.JSONDecodeError as e:
            print('Error parsing specification file')
            print(e)
            return None

        if self.__specification_file_path is not None and not self.__check_specification_format(specification):
            print('The given specification file does not have the correct format')
            return None

        return specification, parent_dir

    def __check_specification_format(self, specification: Dict) -> bool:
        # TODO
        return True


class ValueGenerationSpecification:
    def __init__(self, input_spec: HTMLInputSpecification | HTMLRadioGroupSpecification, grammar: str, formula: str | None = None):
        self.input_spec = input_spec
        self.grammar = grammar
        self.formula = formula

    def __str__(self):
        return f'ValueGenenerationSpecification:\nspec: {self.input_spec}\ngrammar: {self.grammar}\nformula: {self.formula}'


class FormTester:
    def __init__(self, driver: Chrome, specification: Dict, specification_directory: str, repetitions: int = 1) -> None:
        self.__driver = driver
        self.__repetitions = repetitions
        self.__specification = specification
        self.__specification_directory = specification_directory

    def start_generation(self) -> None:
        inspector = ResponseInspector(self.__driver)
        # TODO: start inspecting

        self.__submit_element = self.__get_submit_element_from_json(
            self.__specification)
        print(self.__submit_element)

        for json_spec in self.__specification['controls']:
            generation_template = self.__convert_json_to_specification(
                json_spec)
            print(generation_template)

    def __get_submit_element_from_json(self, spec: Dict) -> WebElement:
        submit_reference = HTMLElementReference(
            spec['submit']['access_method'], spec['submit']['access_value'])
        return get_web_element_by_reference(
            self.__driver, submit_reference)

    def __convert_json_to_specification(self, control: Dict) -> ValueGenerationSpecification:
        grammar = load_file_content(
            f'{self.__specification_directory}/{control["grammar"]}')
        formula = load_file_content(
            f'{self.__specification_directory}/{control["formula"]}')

        if control['type'] == 'radio':
            name = control['reference']
            options = control['options']
            options = list(
                map(lambda o: (HTMLElementReference(o['reference']['access_method'], o['reference']['access_value']), o['value']), options))
            element_spec = HTMLRadioGroupSpecification(name, options)
        else:
            element_reference = HTMLElementReference(
                control['reference']['access_method'], control['reference']['access_value'])
            element_spec = HTMLInputSpecification(element_reference)

        return ValueGenerationSpecification(element_spec, grammar, formula if formula != "" else None)
