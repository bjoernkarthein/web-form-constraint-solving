import os
import unittest
import time

from selenium.webdriver.common.by import By
from seleniumwire.request import Request

from src.interaction.driver import TestAutomationDriver
from src.proxy.interception import RequestScanner


class TestRequestScanner(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.__driver = TestAutomationDriver({}).web_driver
        cls.__scanner = RequestScanner()
        file_path = os.path.abspath("tests/unit/test_data/test_form.html")
        cls.__url = "file://" + file_path

    @classmethod
    def tearDownClass(cls):
        cls.__driver.quit()

    def setUp(self):
        self.__driver.get(self.__url)
        self.__driver.request_interceptor = self.__block_all

    def tearDown(self):
        del self.__driver.request_interceptor
        del self.__driver.requests

    def __block_all(self, request: Request):
        request.create_response(200)

    def __fill_form(self, name_prefix: str, check: bool = True):
        self.__driver.find_element(By.NAME, f"{name_prefix}-first").send_keys(
            "shs%//jksajksd:-o"
        )
        self.__driver.find_element(By.NAME, f"{name_prefix}-second").send_keys("")

        if check:
            self.__driver.find_element(By.NAME, f"{name_prefix}-check").click()

        self.__driver.find_element(By.ID, f"{name_prefix}-sub").click()
        time.sleep(2)

    def __get_request_by_url_match(self, pattern: str) -> Request | None:
        reqs = list(filter(lambda r: pattern in r.url, self.__driver.requests))
        if len(reqs) == 1:
            return reqs[0]

        return None

    def test_param_detection_get_request(self):
        self.__fill_form("get")
        req = self.__get_request_by_url_match("/form/get")

        self.assertIsNotNone(req)

        self.assertTrue(
            self.__scanner.all_values_in_form_request(
                req,
                {
                    "get-first": "shs%//jksajksd:-o",
                    "get-check": "yessir",
                    "get-second": "",
                },
            )
        )

    def test_param_detection_get_request_two(self):
        self.__fill_form("get", check=False)
        req = self.__get_request_by_url_match("/form/get")

        self.assertIsNotNone(req)

        self.assertFalse(
            self.__scanner.all_values_in_form_request(
                req,
                {
                    "get-first": "shs%//jksajksd:-o",
                    "get-second": "",
                    "get-check": "yessir",
                },
            )
        )

        self.assertTrue(
            self.__scanner.all_values_in_form_request(
                req, {"get-second": "", "get-first": "shs%//jksajksd:-o"}
            )
        )

    def test_param_detection_www_encoded_post_request(self):
        self.__fill_form("post-www")
        req = self.__get_request_by_url_match("/form/post")

        self.assertIsNotNone(req)

        self.assertTrue(
            self.__scanner.all_values_in_form_request(
                req,
                {
                    "post-www-first": "shs%//jksajksd:-o",
                    "post-www-second": "",
                    "post-www-check": "yessir",
                },
            )
        )

        self.assertFalse(
            self.__scanner.all_values_in_form_request(
                req,
                {
                    "post-www-first": "shs%//jksajksd:-o",
                    "post-www-second": "",
                    "post-www-check": "yessir",
                    "bla": "bla",
                },
            )
        )

    def test_param_detection_form_data_encoded_post_request(self):
        self.__fill_form("post-fd")
        req = self.__get_request_by_url_match("/form/post")

        self.assertIsNotNone(req)

        self.assertTrue(
            self.__scanner.all_values_in_form_request(
                req,
                {
                    "post-fd-first": "shs%//jksajksd:-o",
                    "post-fd-second": "",
                    "post-fd-check": "yessir",
                },
            )
        )

        self.assertFalse(
            self.__scanner.all_values_in_form_request(
                req,
                {
                    "post-fd-first": "shs%//jksajksd:-o",
                    "post-fd-second": "",
                    "post-fd-check": "yessir",
                    "bla": "bla",
                },
            )
        )

    def test_param_detection_text_post_request(self):
        self.__fill_form("post-text")
        req = self.__get_request_by_url_match("/form/post")

        self.assertIsNotNone(req)

        self.assertTrue(
            self.__scanner.all_values_in_form_request(
                req,
                {
                    "post-text-first": "shs%//jksajksd:-o",
                    "post-text-second": "",
                    "post-text-check": "yessir",
                },
            )
        )

        self.assertFalse(
            self.__scanner.all_values_in_form_request(
                req,
                {
                    "post-fd-first": "shs%//jksajksd:-o",
                    "post-fd-second": "ssd",
                    "post-fd-check": "yessir",
                },
            )
        )

    def test_param_detection_json_post_request(self):
        self.__fill_form("post-json")
        req = self.__get_request_by_url_match("/form/post")

        self.assertIsNotNone(req)

        self.assertTrue(
            self.__scanner.all_values_in_form_request(
                req,
                {
                    "post-json-first": "shs%//jksajksd:-o",
                    "post-json-second": "",
                    "post-json-check": "yessir",
                },
            )
        )

        self.assertFalse(
            self.__scanner.all_values_in_form_request(
                req,
                {
                    "post-json-first": "shs%//jksajksd:-o",
                    "post-json-second": "ssd",
                    "post-json-check": "yessir",
                },
            )
        )
