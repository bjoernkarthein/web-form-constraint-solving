import math
import requests
import time
import json

from enum import Enum
from selenium.common.exceptions import NoSuchElementException, InvalidArgumentException
from selenium.webdriver import Chrome
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from typing import List, Dict

"""
Utility module

Provides helper functions and variables that are used throughout the project
"""


class Action(Enum):
    INTERACTION_START = "INTERACTION_START"
    INTERACTION_END = "INTERACTION_END"
    VALUE_INPUT = "VALUE_INPUT"
    ATTEMPT_SUBMIT = "ATTEMPT_SUBMIT"


class ConfigKey(Enum):
    ANALYSIS = "analysis"
    HTML_ONLY = "html-only"
    MAGIC_VALUE_AMOUNT = "magic-value-amount"
    ANALYSIS_ROUNDS = "analysis-rounds"
    GENERATION = "generation"
    REPETITIONS = "repetitions"
    TESTING = "testing"
    USE_DATALIST_OPTIONS = "use-datalist-options"
    VALID = "valid"
    BLOCK_SUBMISSION = "block-submission"


class InputType(Enum):
    BUTTON = "button"
    CHECKBOX = "checkbox"
    COLOR = "color"
    DATE = "date"
    DATETIME_LOCAL = "datetime-local"
    EMAIL = "email"
    FILE = "file"
    HIDDEN = "hidden"
    IMAGE = "image"
    MONTH = "month"
    NUMBER = "number"
    PASSWORD = "password"
    RADIO = "radio"
    RANGE = "range"
    RESET = "reset"
    SEARCH = "search"
    SUBMIT = "submit"
    TEL = "tel"
    TEXT = "text"
    TEXTAREA = "textarea"
    TIME = "time"
    URL = "url"
    WEEK = "week"


pre_built_specifications_path = "../pre-built-specifications"

service_base_url = "http://localhost:4000"
admin_controller = f"{service_base_url}/admin"
analysis_controller = f"{service_base_url}/analysis"
instrumentation_controller = f"{service_base_url}/instrumentation"

one_line_text_input_types = [
    InputType.PASSWORD.value,
    InputType.SEARCH.value,
    InputType.TEL.value,
    InputType.TEXT.value,
]
binary_input_types = [InputType.CHECKBOX.value, InputType.RADIO.value]
non_writable_input_types = [
    InputType.SUBMIT.value,
    InputType.HIDDEN.value,
    InputType.RESET.value,
    InputType.RANGE.value,
    InputType.FILE.value,
    InputType.COLOR.value,
    InputType.IMAGE.value,
]

__current_value_map: Dict = {}


def clear_value_mapping() -> None:
    __current_value_map = {}


def get_current_values_from_form() -> List[str]:
    return list(__current_value_map.values())


def get_current_value_mapping() -> Dict:
    return __current_value_map


def load_file_content(file_name: str) -> str:
    try:
        with open(file_name) as file:
            file_content = file.read()
    except FileNotFoundError:
        return ""

    return file_content


def write_to_file(file_name: str, data: str | Dict) -> None:
    with open(file_name, "w") as file:
        if isinstance(data, str):
            file.write(data)
        else:
            json.dump(data, file, indent=4)


def start_trace_recording(data) -> None:
    url = f"{analysis_controller}/record"
    requests.post(
        url,
        json={
            "action": Action.INTERACTION_START.value,
            "args": data,
            "time": math.floor(time.time() * 1000),
            "pageFile": 0,
        },
    )


def stop_trace_recording(data) -> None:
    url = f"{analysis_controller}/record"
    requests.post(
        url,
        json={
            "action": Action.INTERACTION_END.value,
            "args": data,
            "time": math.floor(time.time() * 1000),
            "pageFile": 0,
        },
    )


def record_trace(action: Action, args=None) -> None:
    url = f"{analysis_controller}/record"
    requests.post(
        url,
        json={
            "action": action.value,
            "args": args,
            "time": math.floor(time.time() * 1000),
            "pageFile": 0,
        },
    )


def get_constraint_candidates() -> Dict:
    url = f"{analysis_controller}/candidates"
    return requests.get(url).json()


def load_page(driver: Chrome, url: str) -> None:
    try:
        driver.get(url)
    except InvalidArgumentException:
        print(
            "The provided url can not be loaded by selenium web driver. Please provide a url of the format http(s)://(www).example.com"
        )


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


def write_to_web_element(
    web_element: WebElement, value: str, element_reference
) -> None:
    try:
        record_trace(
            Action.VALUE_INPUT,
            {"reference": element_reference.get_as_dict(), "value": value},
        )
        web_element.send_keys(value)
    except Exception:
        pass


def clear_value_of_web_element(driver: Chrome, web_element: WebElement) -> None:
    set_value_of_web_element(driver, web_element, "")


def set_value_of_web_element(
    driver: Chrome, web_element: WebElement, value: str
) -> None:
    try:
        driver.execute_script(
            'arguments[0].setAttribute("value", arguments[1])', web_element, value
        )
    except Exception:
        pass


def get_web_element_by_reference(driver: Chrome, html_element_reference) -> WebElement:
    try:
        if html_element_reference.access_method == "id":
            return driver.find_element(By.ID, html_element_reference.access_value)
        elif html_element_reference.access_method == "xpath":
            return driver.find_element(By.XPATH, html_element_reference.access_value)
        elif html_element_reference.access_method == "name":
            return driver.find_element(By.NAME, html_element_reference.access_value)
    except NoSuchElementException:
        return None


def get_web_elements_by_reference(
    driver: Chrome, html_element_reference
) -> List[WebElement]:
    try:
        if html_element_reference.access_method == "id":
            return driver.find_elements(By.ID, html_element_reference.access_value)
        elif html_element_reference.access_method == "xpath":
            return driver.find_elements(By.XPATH, html_element_reference.access_value)
        elif html_element_reference.access_method == "name":
            return driver.find_elements(By.NAME, html_element_reference.access_value)
    except NoSuchElementException:
        return None


def click_web_element_by_reference(driver: Chrome, html_element_reference) -> None:
    web_element = get_web_element_by_reference(driver, html_element_reference)
    if web_element is not None:
        click_web_element(web_element)


def click_web_element_by_reference_with_clear(
    driver: Chrome, html_element_reference
) -> None:
    web_element = get_web_element_by_reference(driver, html_element_reference)
    if web_element is not None:
        clear_web_element(web_element)
        click_web_element(web_element)


def write_to_web_element_by_reference(
    driver: Chrome, html_element_reference, value: str
) -> None:
    web_element = get_web_element_by_reference(driver, html_element_reference)
    if web_element is not None:
        write_to_web_element(web_element, value)


def write_to_web_element_by_reference_with_clear(
    driver: Chrome, type: str, html_element_reference, value: str
) -> None:
    if type == InputType.CHECKBOX.value:
        if value == "1":
            __current_value_map[html_element_reference] = "on"
    else:
        __current_value_map[html_element_reference] = value

    web_element = get_web_element_by_reference(driver, html_element_reference)
    if web_element is None:
        return

    # TODO: move every input type to dedicated function
    match type:
        case InputType.CHECKBOX.value:
            # deselect if already selected
            if web_element.is_selected():
                click_web_element(web_element)
            if int(value):
                click_web_element(web_element)
        case InputType.DATE.value:
            [year, month, day] = value.split("-")
            web_element.clear()
            web_element.send_keys(month)
            web_element.send_keys(day)
            web_element.send_keys(year)
        case InputType.DATETIME_LOCAL.value:
            split_char = "T" if "T" in value else " "
            [date, time] = value.split(split_char)
            [year, month, day] = date.split("-")
            [hours, minutes] = time.split(":")
            period_of_day = "AM"
            if int(hours) == 0:
                hours = int(hours) + 12
            elif int(hours) == 12:
                period_of_day = "PM"
            elif int(hours) > 12:
                hours = int(hours) - 12
                period_of_day = "PM"
            hours = f"{int(hours):02d}"
            web_element.clear()
            web_element.send_keys(month)
            web_element.send_keys(day)
            web_element.send_keys(year)
            ActionChains(driver).key_down(Keys.TAB).key_up(Keys.TAB).perform()
            web_element.send_keys(hours)
            web_element.send_keys(minutes)
            web_element.send_keys(period_of_day)
        case InputType.MONTH.value:
            [year, month] = value.split("-")
            web_element.clear()
            web_element.send_keys(month)
            ActionChains(driver).key_down(Keys.TAB).key_up(Keys.TAB).perform()
            web_element.send_keys(year)
        case InputType.RADIO.value:
            elements = get_web_elements_by_reference(driver, html_element_reference)
            for elem in elements:
                if elem.get_attribute("value") == value:
                    elem.click()
        case InputType.TIME.value:
            [hours, minutes] = value.split(":")
            period_of_day = "AM"
            if int(hours) == 0:
                hours = int(hours) + 12
            elif int(hours) == 12:
                period_of_day = "PM"
            elif int(hours) > 12:
                hours = int(hours) - 12
                period_of_day = "PM"
            hours = f"{int(hours):02d}"
            web_element.clear()
            web_element.send_keys(hours)
            web_element.send_keys(minutes)
            web_element.send_keys(period_of_day)
        case InputType.WEEK.value:
            [year, week] = value.split("-W")
            web_element.clear()
            web_element.send_keys(week)
            web_element.send_keys(year)
        case _:
            clear_web_element(web_element)
            write_to_web_element(web_element, value, html_element_reference)


def set_value_of_web_element_by_reference(
    driver: Chrome, html_element_reference, value: str
) -> None:
    web_element = get_web_element_by_reference(driver, html_element_reference)
    if web_element is not None:
        set_value_of_web_element(driver, web_element, value)


def set_value_of_web_element_by_reference_with_clear(
    driver: Chrome, html_element_reference, value: str
) -> None:
    web_element = get_web_element_by_reference(driver, html_element_reference)
    if web_element is not None:
        clear_value_of_web_element(driver, web_element)
        set_value_of_web_element(driver, web_element, value)


def clamp_to_range(input: int, start: int, end: int | None) -> int:
    if end is None:
        return max(start, input)
    else:
        return max(start, min(input, end))
