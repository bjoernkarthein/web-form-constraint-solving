import json

from lxml import etree, html
from typing import Dict, List, Union


class HTMLElementReference:
    def __init__(self, access_method: str, access_value: str) -> None:
        self.access_method = access_method
        self.access_value = access_value

    def get_as_dict(self) -> Dict[str, str]:
        return {'access_method': self.access_method, 'access_value': self.access_value}

    def __str__(self) -> str:
        return json.dumps(self.get_as_dict())


class HTMLConstraints:
    def __init__(self, list: str = None, max: str = None, maxlength: str = None, min: str = None, minlength: str = None, multiple: str = None, pattern: str = None, required: str = None, type: str = None) -> None:
        self.__list = list
        self.__max = max
        self.__maxlength = maxlength
        self.__min = min
        self.__minlength = minlength
        self.__multiple = multiple
        self.__pattern = pattern
        self.__required = required
        self.__type = type

        self.__html_constraint_dict: dict = {
            'list': list,
            'max': max,
            'maxlength': maxlength,
            'min': min,
            'minlength': minlength,
            'multiple': multiple,
            'pattern': pattern,
            'required': required,
            'type': type,
        }

    @property
    def list(self) -> str:
        """Getter for list"""
        return self.__list

    @list.setter
    def list(self, value: str) -> None:
        """Setter for list"""
        self.__list = value
        self.__html_constraint_dict['list'] = value

    @property
    def max(self) -> str:
        """Getter for max"""
        return self.__max

    @max.setter
    def max(self, value: str) -> None:
        """Setter for max"""
        self.__max = value
        self.__html_constraint_dict['max'] = value

    @property
    def maxlength(self) -> str:
        """Getter for maxlength"""
        return self.__maxlength

    @maxlength.setter
    def maxlength(self, value: str) -> None:
        """Setter for maxlength"""
        self.__maxlength = value
        self.__html_constraint_dict['maxlength'] = value

    @property
    def min(self) -> str:
        """Getter for min"""
        return self.__min

    @min.setter
    def min(self, value: str) -> None:
        """Setter for min"""
        self.__min = value
        self.__html_constraint_dict['min'] = value

    @property
    def minlength(self) -> str:
        """Getter for minlength"""
        return self.__minlength

    @minlength.setter
    def minlength(self, value: str) -> None:
        """Setter for minlength"""
        self.__minlength = value
        self.__html_constraint_dict['minlength'] = value

    @property
    def multiple(self) -> str:
        """Getter for multiple"""
        return self.__multiple

    @multiple.setter
    def multiple(self, value: str) -> None:
        """Setter for multiple"""
        self.__multiple = value
        self.__html_constraint_dict['multiple'] = value

    @property
    def pattern(self) -> str:
        """Getter for pattern"""
        return self.__pattern

    @pattern.setter
    def pattern(self, value: str) -> None:
        """Setter for pattern"""
        self.__pattern = value
        self.__html_constraint_dict['pattern'] = value

    @property
    def required(self) -> str:
        """Getter for required"""
        return self.__required

    @required.setter
    def required(self, value: str) -> None:
        """Setter for required"""
        self.__required = value
        self.__html_constraint_dict['required'] = value

    @property
    def type(self) -> str:
        """Getter for type"""
        return self.__type

    @type.setter
    def type(self, value: str) -> None:
        """Setter for type"""
        self.__type = value
        self.__html_constraint_dict['type'] = value

    def get_by_name(self, attribute_name: str) -> str:
        """Get an attributes value via the attributes name as string.
        If the provided name is not an HTML validation attribute None is returned.
        """
        return self.__html_constraint_dict[attribute_name]

    def set_by_name(self, attribute_name: str, value: str) -> None:
        """Set the value of an attribute via the attribute name as string."""
        setattr(self, attribute_name, value)

    def get_attributes(self) -> List[str]:
        """Return a list of all attribute names"""
        return list(self.__html_constraint_dict)

    def __str__(self) -> str:
        return json.dumps(self.__html_constraint_dict)


class HTMLInputSpecification:
    def __init__(self, reference: HTMLElementReference, constraints: HTMLConstraints) -> None:
        self.reference = reference
        self.contraints = constraints

    def get_as_dict(self) -> Dict[str, HTMLElementReference | HTMLConstraints]:
        return {'reference': str(self.reference), 'constraints': str(self.contraints)}

    def __str__(self) -> str:
        return f"{self.get_as_dict()}"


HTMLInputElement = Union[html.InputElement, html.TextareaElement]


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

    def extract_static_constraints(self, form: html.FormElement) -> List[HTMLInputSpecification]:
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

    def __extract_static_constraints_from_inputs(self, input_elements: List[HTMLInputElement]) -> List[HTMLInputSpecification]:
        result = []

        for input in input_elements:
            html_constraints = HTMLConstraints()
            if input.tag == 'textarea':
                html_constraints.type = 'textarea'

            for attribute in list(input.attrib):
                if attribute in html_constraints.get_attributes():
                    html_constraints.set_by_name(
                        attribute, input.get(attribute))

            element_reference = self.__get_element_reference(input)
            result.append(HTMLInputSpecification(
                element_reference, html_constraints))

        return result

    def __get_element_reference(self, element: etree.Element) -> HTMLElementReference:
        if element.get('id') is not None:
            return HTMLElementReference('id', element.get('id'))
        else:
            html_ast = etree.ElementTree(self.__html_tree_root)
            xpath = html_ast.getpath(element)
            return HTMLElementReference('xpath', xpath)


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
                input1.attrib, list(HTMLConstraints().get_attributes()))
            self.__keep_entries_by_key(
                input2.attrib, list(HTMLConstraints().get_attributes()))

            if input1.attrib != input2.attrib:
                # Attributes do not match
                return False

        return True

    def __keep_entries_by_key(self, dictionary: dict, keys_to_keep: List[str]) -> None:
        for key in list(dictionary):
            if not key in keys_to_keep:
                del dictionary[key]
