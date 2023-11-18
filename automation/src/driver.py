import sys

from selenium.common.exceptions import *
from selenium.webdriver.chrome.service import Service
from seleniumwire import webdriver

from html_analysis import HTMLAnalyser, FormObserver
from interceptor import NetworkInterceptor, ResponseInspector
from utility import record_trace

chrome_driver_path = '../chromedriver/windows/chromedriver.exe'

"""
Driver module

Handles all of the browser driver management.
"""


class TestAutomationDriver:
    """Test Automation class

    ...
    """

    def __init__(self, config: dict, url: str) -> None:
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

        interceptor = NetworkInterceptor(self.__driver)
        # interceptor.instrument_files()

        inspector = ResponseInspector(self.__driver)

    def run(self) -> None:
        self.__load_page(self.__url)
        self.__analyse_html(self.__driver.page_source)

    def __load_page(self, url: str) -> None:
        """ Open the web page by url.
        Page is opened in a headless chrome instance controlled by selenium.
        """
        try:
            self.__driver.get(url)
        except InvalidArgumentException:
            # TODO
            pass

    def __analyse_html(self, html_string: str) -> None:
        html_analyser = HTMLAnalyser(html_string)
        (form, access) = html_analyser.select_form()

        if form is None or access is None:
            self.__exit()

        self.__form_observer = FormObserver(form, access)

        html_constraints = html_analyser.extract_static_constraints(form)
        if html_constraints is None:
            self.__exit()

        for constraint in html_constraints:
            print(constraint)

    def __exit(self, exit_code=None) -> None:
        """Free all resources and exit"""

        self.__driver.quit()
        sys.exit(exit_code)
