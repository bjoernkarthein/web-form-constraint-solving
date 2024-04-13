import os
import sys
import yaml

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.interaction.driver import TestAutomationDriver


def fill_cart(driver: TestAutomationDriver) -> None:
    driver.web_driver.get(
        "http://localhost/women/2-9-brown-bear-printed-sweater.html#/1-size-s"
    )
    add_to_cart = WebDriverWait(driver.web_driver, 10).until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "/html/body/main/section/div/div/div/section/div[1]/div[2]/div[2]/div[2]/form/div[2]/div/div[2]/button",
            )
        )
    )
    add_to_cart.click()

    WebDriverWait(driver.web_driver, 10).until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                "/html/body/div[1]/div/div/div[2]/div/div[2]/div/div/a",
            )
        )
    )


if __name__ == "__main__":
    config = yaml.safe_load(open("evaluation/config_test.yml"))

    driver = TestAutomationDriver(
        config,
        "http://localhost/order",
    )

    fill_cart(driver)
    driver.run_test(
        "evaluation/specifications/prestashop/specification.json",
        "evaluation/prestashop_test_results.json",
    )
