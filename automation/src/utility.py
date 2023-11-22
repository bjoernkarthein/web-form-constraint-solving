import math
import requests
import time

from enum import Enum
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from html_analysis import HTMLElementReference

"""
Utility module

Provides helper functions and variables that are used throughout the project
"""


class Action(Enum):
    INPUT_VALUE = 'INPUT_VALUE'


class ConfigKey(Enum):
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

instrumentation_service_base_url = 'http://localhost:4000'

one_line_text_input_types = [InputType.EMAIL.value, InputType.PASSWORD.value,
                             InputType.SEARCH.value, InputType.TEL.value, InputType.TEXT.value]


def load_file_content(file_name: str) -> str:
    try:
        with open(file_name) as file:
            file_content = file.read()
    except FileNotFoundError:
        return ""

    return file_content


def record_trace(action: Action, args=None):
    url = f'{instrumentation_service_base_url}/record'
    requests.post(url, data={'action': action.value, 'args': str(args),
                             'time': math.floor(time.time() * 1000), 'pageFile': 0})


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


def write_to_web_element(web_element: WebElement, value: str) -> None:
    try:
        web_element.send_keys(value)
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


def write_to_web_element_by_reference_with_clear(driver: Chrome, html_element_reference: HTMLElementReference, value: str) -> None:
    web_element = get_web_element_by_reference(driver, html_element_reference)
    if web_element is not None:
        clear_web_element(web_element)
        write_to_web_element(web_element, value)


def set_value_of_web_element_by_reference(driver: Chrome, html_element_reference: HTMLElementReference, value: str) -> None:
    web_element = get_web_element_by_reference(driver, html_element_reference)
    if web_element is not None:
        set_value_of_web_element(driver, web_element, value)


def set_value_of_web_element_by_reference_with_clear(driver: Chrome, html_element_reference: HTMLElementReference, value: str) -> None:
    web_element = get_web_element_by_reference(driver, html_element_reference)
    if web_element is not None:
        clear_value_of_web_element(driver, web_element)
        set_value_of_web_element(driver, web_element, value)
