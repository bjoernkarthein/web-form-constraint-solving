import json

from lxml import etree, html
from typing import Dict, List, Tuple, Union

from utility import non_writable_input_types


class HTMLElementReference:
    def __init__(self, access_method: str, access_value: str) -> None:
        self.access_method = access_method
        self.access_value = access_value

    def get_as_dict(self) -> Dict[str, str]:
        return {'access_method': self.access_method, 'access_value': self.access_value}

    def __str__(self) -> str:
        return json.dumps(self.get_as_dict())


class HTMLConstraints:
    def __init__(self, list: List[str] = None, max: str = None, maxlength: str = None, min: str = None, minlength: str = None, multiple: str = None, pattern: str = None, required: str = None, step: str = None, type: str = None) -> None:
        self.__list = list
        self.__max = max
        self.__maxlength = maxlength
        self.__min = min
        self.__minlength = minlength
        self.__multiple = multiple
        self.__pattern = pattern
        self.__required = required
        self.__step = step
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
            'step': step,
            'type': type,
        }

    @property
    def list(self) -> List[str]:
        """Getter for list"""
        return self.__list

    @list.setter
    def list(self, value: List[str]) -> None:
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
    def step(self) -> str:
        """Getter for type"""
        return self.__step

    @step.setter
    def step(self, value: str) -> None:
        """Setter for type"""
        self.__step = value
        self.__html_constraint_dict['step'] = value

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

    def get_as_dict(self) -> Dict[str, str]:
        return self.__html_constraint_dict

    def __str__(self) -> str:
        return json.dumps(self.get_as_dict())


class HTMLInputSpecification:
    def __init__(self, reference: HTMLElementReference, constraints: HTMLConstraints) -> None:
        self.reference = reference
        self.contraints = constraints

    def get_as_dict(self) -> Dict[str, HTMLElementReference | HTMLConstraints]:
        return {'reference': self.reference.get_as_dict(), 'constraints': self.contraints.get_as_dict()}

    def get_representation(self, grammar_file: str, formula_file: str) -> Dict[str, str | Dict[str, str]]:
        return {'type': self.contraints.type, 'reference': self.reference.get_as_dict(), 'grammar': grammar_file, 'formula': formula_file}

    def __str__(self) -> str:
        return json.dumps(self.get_as_dict())


HTMLInputElement = Union[html.InputElement, html.TextareaElement]


class HTMLRadioGroupSpecification:
    def __init__(self, name: str, required: bool, options: List[Tuple[HTMLElementReference, str]]) -> None:
        self.name = name
        self.required = required
        self.options = options

    def get_as_dict(self) -> Dict[str, str | bool | List[Tuple[HTMLElementReference, str]]]:
        return {'name': self.name, 'required': self.required, 'options': [(o[0].get_as_dict(), o[1]) for o in self.options]}

    def get_representation(self, grammar_file: str, formula_file: str) -> Dict[str, str | Dict[str, str]]:
        return {'type': 'radio', 'reference': self.name, 'grammar': grammar_file, 'formula': formula_file}

    def __str__(self) -> str:
        return json.dumps(self.get_as_dict())


class HTMLAnalyser:
    def __init__(self, html_dom_snapshot: str) -> None:
        self.__html_tree_root = html.fromstring(html_dom_snapshot)

    def select_form(self) -> (etree.Element, str):
        all_forms = self.__html_tree_root.xpath('//form')
        if len(all_forms) == 0:
            print('The page for the provided url does not seem to contain any HTML form elements. Maybe try another url?')
            return (None, None)
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
        self.__submit_element = None
        for elem in all_inputs + all_buttons:
            if elem.get('type') == 'submit':
                self.__submit_element = self.__get_element_reference(elem)
                break

        if self.__submit_element is None:
            for button in all_buttons:
                if button.get('type') is None:
                    self.__submit_element = self.__get_element_reference(elem)
                    break

        if self.__submit_element is None:
            print('The form does not contain an element to submit')
            return None

        # Remove inputs that have type submit
        all_inputs = [
            input for input in all_inputs if input.get('type') != 'submit']

        return self.__extract_static_constraints_from_inputs(all_inputs)

    @property
    def submit_element(self) -> HTMLElementReference:
        """Getetr for submit element of the selected form"""
        return self.__submit_element

    def __extract_static_constraints_from_inputs(self, input_elements: List[HTMLInputElement]) -> List[HTMLInputSpecification | HTMLRadioGroupSpecification]:
        result: List[HTMLInputSpecification | HTMLRadioGroupSpecification] = []
        radio_groups: Dict[str, List[HTMLInputElement]] = {}
        radio_items = list(filter(lambda i: i.get('type')
                                  == 'radio', input_elements))
        for item in radio_items:
            key = item.get('name')
            if key not in radio_groups:
                radio_groups[key] = [item]
            else:
                radio_groups[key] = radio_groups[key] + [item]

        for name, values in radio_groups.items():
            specifications: List[Tuple[HTMLElementReference, str]] = []
            required = False
            for v in values:
                ref = self.__get_element_reference(v)
                value = v.get('value')
                # TODO: this a good idea?
                # For the case that the radio option does not have a value, we do not add it to the spec
                if value is not None:
                    specifications.append((ref, value))
                    required = required or v.get('required') is not None
            if len(specifications) > 0:
                spec = HTMLRadioGroupSpecification(
                    name, required, specifications)
                result.append(spec)

        for input in input_elements:
            html_constraints = HTMLConstraints()

            if input.get('type') in ['radio'] + non_writable_input_types:
                continue

            if input.tag == 'textarea':
                html_constraints.type = 'textarea'

            for attribute in list(input.attrib):
                if attribute == 'list':
                    html_constraints.set_by_name(
                        'list', self.__get_datalist_options_by_id(input.get('list')))
                    continue
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

    def __get_datalist_options_by_id(self, datalist_id: str) -> List[str] | None:
        datalists: List[html.Element] = self.__html_tree_root.xpath(
            f'//datalist[@id = "{datalist_id}"]')

        if len(datalists) == 0:
            return None

        datalist = datalists[0]
        option_elements: List[html.Element] = datalist.getchildren()
        options = list(map(lambda option: '"' + (option.get('value') if option.get('value') is not None else option.text) +
                           '"', option_elements))

        return options


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
