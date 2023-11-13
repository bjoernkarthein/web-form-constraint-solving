from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import *

from interceptor import NetworkInterceptor, ResponseInspector

import sys
import time

chrome_driver_path = '../chromedriver/windows/chromedriver.exe'

"""
Driver module

Handles all of the browser driver management.
"""


class TestAutomationDriver:
    """Test Automation class

    ...
    """

    def __init__(self, config) -> None:
        """Initialize the Test Automation

        Set options for selenium chrome driver and selenium wire proxy
        Initilaize web driver.
        """
        self.__config: dict = config

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
        interceptor.instrument_files()

        inspector = ResponseInspector(self.__driver)

    def load_page(self, url: str) -> None:
        """ Open the web page by url.
        Page is opened in a headless chrome instance controlled by selenium.
        """
        try:
            self.__driver.get(url)
            time.sleep(60)
            # self.__exit()
        except InvalidArgumentException:
            # TODO
            pass

    # def add_overlay(self) -> None:
    #     self.driver.execute_script("""
    #                                 const frame = document.createElement("iframe");
    #                                 frame.setAttribute("src", "localhost:4000/static/ui.html");
    #                                 frame.style.width = "100vw";
    #                                 frame.style.height = "10rem";
    #                                 frame.style.position = "fixed";
    #                                 frame.style.top = 0;
    #                                 frame.style.left = 0;
    #                                 frame.style.zIndex = 1000;
    #                                 document.body.style.marginTop = "10rem";
    #                                 document.body.append(frame);
    #                                """)

    def __exit(self, exit_code=None) -> None:
        """Free all resources and exit"""

        self.__driver.quit()
        sys.exit(exit_code)
