from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import *

chrome_driver_path = "../chromedriver/windows/chromedriver.exe"


class TestAutomationDriver:
    def __init__(self) -> None:
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_experimental_option(
        #     "debuggerAddress", "localhost:9222")
        chrome_options.add_experimental_option(
            'excludeSwitches', ['enable-logging'])
        chrome_options.add_argument('--lang=en')

        wire_options = {
            'disable_encoding': True
        }

        self.driver = webdriver.Chrome(
            service=Service(chrome_driver_path),
            options=chrome_options,
            seleniumwire_options=wire_options
        )

    def load_page(self, url: str) -> None:
        try:
            self.driver.get(url)
            self.add_overlay()
        except InvalidArgumentException:
            # TODO
            pass

    def add_overlay(self) -> None:
        self.driver.execute_script("""
                                    const frame = document.createElement("iframe");
                                    frame.setAttribute("src", "localhost:4000/static/ui.html");
                                    frame.style.width = "100vw";
                                    frame.style.height = "10rem";
                                    frame.style.position = "fixed";
                                    frame.style.top = 0;
                                    frame.style.left = 0;
                                    frame.style.zIndex = 1000;
                                    document.body.style.marginTop = "10rem";
                                    document.body.append(frame);
                                   """)
