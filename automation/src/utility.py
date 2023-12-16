import math
import requests
import time

from enum import Enum
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Chrome
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from typing import List

from html_analysis import HTMLElementReference

"""
Utility module

Provides helper functions and variables that are used throughout the project
"""


class Action(Enum):
    INTERACTION_START = 'INTERACTION_START'
    INTERACTION_END = 'INTERACTION_END'
    VALUE_INPUT = 'VALUE_INPUT'
    ATTEMPT_SUBMIT = 'ATTEMPT_SUBMIT'


class ConfigKey(Enum):
    ANALYSIS = 'analysis'
    MAGIC_VALUE_AMOUNT = 'magic-value-amount'
    GENERATION = 'generation'
    USE_DATALIST_OPTIONS = 'use-datalist-options'


class InputType(Enum):
    BUTTON = 'button'
    CHECKBOX = 'checkbox'
    COLOR = 'color'
    DATE = 'date'
    DATETIME_LOCAL = 'datetime-local'
    EMAIL = 'email'
    FILE = 'file'
    HIDDEN = 'hidden'
    IMAGE = 'image'
    MONTH = 'month'
    NUMBER = 'number'
    PASSWORD = 'password'
    RADIO = 'radio'
    RANGE = 'range'
    RESET = 'reset'
    SEARCH = 'search'
    SUBMIT = 'submit'
    TEL = 'tel'
    TEXT = 'text'
    TEXTAREA = 'textarea'
    TIME = 'time'
    URL = 'url'
    WEEK = 'week'


pre_built_specifications_path = '../pre-built-specifications'

service_base_url = 'http://localhost:4000'
admin_controller = f'{service_base_url}/admin'
analysis_controller = f'{service_base_url}/analysis'
instrumentation_controller = f'{service_base_url}/instrumentation'

one_line_text_input_types = [InputType.EMAIL.value, InputType.PASSWORD.value,
                             InputType.SEARCH.value, InputType.TEL.value, InputType.TEXT.value]

binary_input_types = [InputType.CHECKBOX.value, InputType.RADIO.value]

magic_value_required_input_types = one_line_text_input_types + \
    [InputType.DATE.value, InputType.MONTH.value, InputType.WEEK.value]


def load_file_content(file_name: str) -> str:
    try:
        with open(file_name) as file:
            file_content = file.read()
    except FileNotFoundError:
        return ""

    return file_content


def start_trace_recording(data) -> None:
    url = f'{analysis_controller}/record'
    requests.post(
        url, json={'action': Action.INTERACTION_START.value, 'args': data, 'time': math.floor(time.time() * 1000), 'pageFile': 0})


def stop_trace_recording(data) -> None:
    url = f'{analysis_controller}/record'
    requests.post(
        url, json={'action': Action.INTERACTION_END.value, 'args': data, 'time': math.floor(time.time() * 1000), 'pageFile': 0})


def record_trace(action: Action, args=None) -> None:
    url = f'{analysis_controller}/record'
    requests.post(url, json={'action': action.value, 'args': args,
                             'time': math.floor(time.time() * 1000), 'pageFile': 0})


def clean_instrumentation_resources() -> None:
    url = f'{admin_controller}/clean'
    requests.get(url)


def clear_web_element(web_element: WebElement) -> None:
    try:
        web_element.clear()
    except Exception:
        pass


def click_web_element(web_element: WebElement) -> None:
    try:
        web_element.click()
    except Exception:
        pass


def write_to_web_element(web_element: WebElement, value: str | List[str], element_reference: HTMLElementReference) -> None:
    try:
        record_trace(Action.VALUE_INPUT, {
                     'reference': element_reference.get_as_dict(), 'value': value})
        if isinstance(value, str):
            print("value is a string")
            print(value)
            web_element.send_keys(value)
        else:
            print("value is an array")
            print(value)
            for v in value:
                web_element.send_keys(v)
    except Exception:
        pass


def clear_value_of_web_element(driver: Chrome, web_element: WebElement) -> None:
    set_value_of_web_element(driver, web_element, '')


def set_value_of_web_element(driver: Chrome, web_element: WebElement, value: str) -> None:
    try:
        driver.execute_script(
            'arguments[0].setAttribute("value", arguments[1])', web_element, value)
    except Exception:
        pass


def get_web_element_by_reference(driver: Chrome, html_element_reference: HTMLElementReference) -> WebElement:
    try:
        if html_element_reference.access_method == 'id':
            return driver.find_element(By.ID, html_element_reference.access_value)
        elif html_element_reference.access_method == 'xpath':
            return driver.find_element(By.XPATH, html_element_reference.access_value)
    except NoSuchElementException:
        return None


def click_web_element_by_reference(driver: Chrome, html_element_reference: HTMLElementReference) -> None:
    web_element = get_web_element_by_reference(driver, html_element_reference)
    if web_element is not None:
        click_web_element(web_element)


def click_web_element_by_reference_with_clear(driver: Chrome, html_element_reference: HTMLElementReference) -> None:
    web_element = get_web_element_by_reference(driver, html_element_reference)
    if web_element is not None:
        clear_web_element(web_element)
        click_web_element(web_element)


def write_to_web_element_by_reference(driver: Chrome, html_element_reference: HTMLElementReference, value: str) -> None:
    web_element = get_web_element_by_reference(driver, html_element_reference)
    if web_element is not None:
        write_to_web_element(web_element, value)


def write_to_web_element_by_reference_with_clear(driver: Chrome, type: str, html_element_reference: HTMLElementReference, value: str) -> None:
    web_element = get_web_element_by_reference(driver, html_element_reference)
    if web_element is None:
        return

    # TODO: move every input type to dedicated function
    match type:
        case t if t in one_line_text_input_types:
            clear_web_element(web_element)
            write_to_web_element(web_element, value, html_element_reference)
        case t if t in binary_input_types:
            # deselect if already selected
            if web_element.is_selected():
                click_web_element(web_element)
            if int(value):
                click_web_element(web_element)
        case InputType.MONTH.value:
            [year, month] = value.split('-')
            web_element.clear()
            ActionChains(driver).click(web_element).send_keys(month).key_down(
                Keys.TAB).key_up(Keys.TAB).send_keys(year).perform()
        case InputType.WEEK.value:
            [year, week] = value.split('-W')
            web_element.clear()
            ActionChains(driver).click(web_element).send_keys(
                week).send_keys(year).perform()
        case _:
            clear_web_element(web_element)
            write_to_web_element(web_element, value, html_element_reference)


def set_value_of_web_element_by_reference(driver: Chrome, html_element_reference: HTMLElementReference, value: str) -> None:
    web_element = get_web_element_by_reference(driver, html_element_reference)
    if web_element is not None:
        set_value_of_web_element(driver, web_element, value)


def set_value_of_web_element_by_reference_with_clear(driver: Chrome, html_element_reference: HTMLElementReference, value: str) -> None:
    web_element = get_web_element_by_reference(driver, html_element_reference)
    if web_element is not None:
        clear_value_of_web_element(driver, web_element)
        set_value_of_web_element(driver, web_element, value)
