import cProfile
import os
import sys
import yaml
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from evaluation.util.helpers import Evaluation
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
    config = yaml.safe_load(open("evaluation/config.yml"))

    # evaluation
    pr = cProfile.Profile()
    file = os.path.basename(__file__)[:-3]
    eval = Evaluation(pr, file)
    eval.start_profiling()

    driver = TestAutomationDriver(config, "http://localhost/order", evaluation=eval)

    fill_cart(driver)
    driver.run_analysis()
