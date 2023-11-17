import json

from lxml import etree, html
from typing import Dict, List, Union


class ElementReference:
    def __init__(self, access_method: str, access_value: str) -> None:
        self.access_method = access_method
        self.access_value = access_value

    def __str__(self) -> str:
        return json.dumps(self.get_as_dict())

    def get_as_dict(self) -> Dict[str, str]:
        return {'access_method': self.access_method, 'access_value': self.access_value}


HTMLInputElement = Union[html.InputElement, html.TextareaElement]
HTMLStaticConstraintObject = Dict[str, Dict[str, str] | ElementReference]

html_constraint_template: dict = {
    'type': None,
    'required': None,
    'multiple': None,
    'pattern': None,
    'min': None,
    'max': None,
    'minlength': None,
    'maxlength': None,
    'list': None,
}


class HTMLAnalyser:
    def __init__(self, html_dom_snapshot: str) -> None:
        self.__html_tree_root = html.fromstring(html_dom_snapshot)

    def select_form(self) -> (etree.Element, str):
        all_forms = self.__html_tree_root.xpath('//form')
        if len(all_forms) == 0:
            print('The page for the provided url does not seem to contain any HTML form elements. Maybe try another url?')
            return None
        elif len(all_forms) == 1:
            self.__form_access_xpath = '//form[1]'
            return (all_forms[0], self.__form_access_xpath)
        else:
            forms: Dict[int, str] = dict()
            for i in range(len(all_forms)):
                forms[i + 1] = etree.tostring(all_forms[i]).decode('utf-8')

            print('Found multiple forms on the page. Please enter the position of the form that you want to analyse.')
            print('All forms:')
            print(json.dumps(forms, indent=4))
            position = int(input('Position of the form (starting with 1): '))
            if position < 1 or position > len(all_forms):
                print('The entered position does not match any form.')
                return (None, None)

            self.__form_access_xpath = f'//form[{position}]'
            return (all_forms[position - 1], self.__form_access_xpath)

    def extract_static_constraints(self, form: html.FormElement) -> List[HTMLStaticConstraintObject]:
        all_inputs: List[HTMLInputElement] = form.xpath(
            f'{self.__form_access_xpath}/descendant::input') + form.xpath(f'{self.__form_access_xpath}/descendant::textarea')
        all_buttons = form.xpath(
            f'{self.__form_access_xpath}/descendant::button')

        # Find the submit element
        self.submit_element = None
        for elem in all_inputs + all_buttons:
            if elem.get('type') == 'submit':
                self.submit_element = elem

        if self.submit_element is None:
            print('The form does not contain an element with type submit')
            return None

        # Remove inputs that have type submit
        all_inputs = [
            input for input in all_inputs if input.get('type') != 'submit']

        return self.__extract_static_constraints_from_inputs(all_inputs)

    def __extract_static_constraints_from_inputs(self, input_elements: List[HTMLInputElement]) -> List[HTMLStaticConstraintObject]:
        result = []

        for input in input_elements:
            html_constraints = html_constraint_template.copy()
            if input.tag == 'textarea':
                html_constraints['type'] = 'textarea'

            for attribute in list(input.attrib):
                if attribute in html_constraints:
                    html_constraints[attribute] = input.get(attribute)

            element_reference = self.__get_element_reference(input)
            result.append({'reference': str(element_reference),
                          'constraints': html_constraints})

        return result

    def __get_element_reference(self, element: etree.Element) -> ElementReference:
        if element.get('id') is not None:
            return ElementReference('id', element.get('id'))
        else:
            html_ast = etree.ElementTree(self.__html_tree_root)
            xpath = html_ast.getpath(element)
            return ElementReference('xpath', xpath)


class FormObserver:
    def __init__(self, form: etree.Element, access: str) -> None:
        self.__most_recent_form_snapshot = form
        self.__access = access

    def check_for_form_changes(self, html_string: str) -> bool:
        html_tree_root = html.fromstring(html_string)
        form = html_tree_root.xpath(self.__access)[0]

        result = self.__are_forms_similar(
            self.__most_recent_form_snapshot, form)

        self.__most_recent_form_snapshot = form
        return result

    def __are_forms_similar(self, root1: html.FormElement, root2: html.FormElement) -> bool:
        form1_inputs = root1.xpath(
            f'{self.__access}/descendant::input') + root1.xpath(
            f'{self.__access}/descendant::textarea')
        form2_inputs = root2.xpath(
            f'{self.__access}/descendant::input') + root2.xpath(
            f'{self.__access}/descendant::textarea')

        if len(form1_inputs) != len(form2_inputs):
            # Not the same amount of inputs in both forms
            return False

        for input1, input2 in zip(form2_inputs, form2_inputs):
            self.__keep_entries_by_key(
                input1.attrib, list(html_constraint_template))
            self.__keep_entries_by_key(
                input2.attrib, list(html_constraint_template))

            if input1.attrib != input2.attrib:
                # Attributes do not match
                return False

        return True

    def __keep_entries_by_key(self, dictionary: dict, keys_to_keep: List[str]) -> None:
        for key in list(dictionary):
            if not key in keys_to_keep:
                del dictionary[key]
