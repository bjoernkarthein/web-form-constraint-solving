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
        print("file not found")
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


def write_to_web_element(web_element: WebElement, value: str) -> None:
    try:
        web_element.send_keys(value)
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


def update_value_map(type: str, value: str, html_element_reference) -> None:
    if type == InputType.CHECKBOX.value:
        if value == "1":
            __current_value_map[html_element_reference] = "on"
    else:
        __current_value_map[html_element_reference] = value


def write_to_web_element_by_reference_with_clear(
    driver: Chrome, type: str, html_element_reference, value: str, record: bool = True
) -> None:
    update_value_map(type, value, html_element_reference)
    web_element = get_web_element_by_reference(driver, html_element_reference)
    if web_element is None:
        return

    match type:
        case InputType.CHECKBOX.value:
            write_to_checkbox_with_clear(web_element, value)
        case InputType.DATE.value:
            write_to_date_picker_with_clear(web_element, value)
        case InputType.DATETIME_LOCAL.value:
            write_to_datetime_picker_with_clear(driver, web_element, value)
        case InputType.MONTH.value:
            write_to_month_picker_with_clear(driver, web_element, value)
        case InputType.RADIO.value:
            write_to_radio_group(driver, html_element_reference, value)
        case InputType.TIME.value:
            write_to_time_picker_with_clear(web_element, value)
        case InputType.WEEK.value:
            write_to_week_picker_with_clear(web_element, value)
        case _:
            clear_web_element(web_element)
            write_to_web_element(web_element, value)

    if record:
        record_trace(
            Action.VALUE_INPUT,
            {"reference": html_element_reference.get_as_dict(), "value": value},
        )


def write_to_checkbox_with_clear(checkbox: WebElement, value: str) -> None:
    # deselect if already selected
    if checkbox.is_selected():
        click_web_element(checkbox)
    if int(value):
        click_web_element(checkbox)


def write_to_date_picker_with_clear(date_picker: WebElement, value: str) -> None:
    [year, month, day] = value.split("-")
    date_picker.clear()
    date_picker.send_keys(month)
    date_picker.send_keys(day)
    date_picker.send_keys(year)


def write_to_datetime_picker_with_clear(
    driver: Chrome, datetime_picker: WebElement, value: str
) -> None:
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
    datetime_picker.clear()
    datetime_picker.send_keys(month)
    datetime_picker.send_keys(day)
    datetime_picker.send_keys(year)
    ActionChains(driver).key_down(Keys.TAB).key_up(Keys.TAB).perform()
    datetime_picker.send_keys(hours)
    datetime_picker.send_keys(minutes)
    datetime_picker.send_keys(period_of_day)


def write_to_month_picker_with_clear(
    driver: Chrome, month_picker: WebElement, value: str
) -> None:
    [year, month] = value.split("-")
    month_picker.clear()
    month_picker.send_keys(month)
    ActionChains(driver).key_down(Keys.TAB).key_up(Keys.TAB).perform()
    month_picker.send_keys(year)


def write_to_radio_group(driver: Chrome, radio_reference, value: str) -> None:
    elements = get_web_elements_by_reference(driver, radio_reference)
    for elem in elements:
        if elem.get_attribute("value") == value:
            elem.click()


def write_to_time_picker_with_clear(time_picker: WebElement, value: str) -> None:
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
    time_picker.clear()
    time_picker.send_keys(hours)
    time_picker.send_keys(minutes)
    time_picker.send_keys(period_of_day)


def write_to_week_picker_with_clear(week_picker: WebElement, value: str) -> None:
    [year, week] = value.split("-W")
    week_picker.clear()
    week_picker.send_keys(week)
    week_picker.send_keys(year)


def clamp_to_range(input: int, start: int, end: int | None) -> int:
    if end is None:
        return max(start, input)
    else:
        return max(start, min(input, end))
