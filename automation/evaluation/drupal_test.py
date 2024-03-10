import cProfile
import os
import sys
import yaml
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from src.interaction.driver import TestAutomationDriver


def setup(driver: TestAutomationDriver) -> None:
    driver.web_driver.get("http://localhost/user/login")
    username = driver.web_driver.find_element(By.ID, "edit-name")
    password = driver.web_driver.find_element(By.ID, "edit-pass")
    username.send_keys("user")
    password.send_keys("bitnami")

    ActionChains(driver.web_driver).key_down(Keys.ENTER).key_up(Keys.ENTER).perform()


if __name__ == "__main__":
    config = yaml.safe_load(open("evaluation/config_test.yml"))

    # initialize profiler
    pr = cProfile.Profile()

    file = os.path.basename(__file__)[:-3]
    driver = TestAutomationDriver(
        config,
        "http://localhost/admin/people/create"
    )

    setup(driver)
    driver.run_test("evaluation/specifications/drupal/specification.json", "evaluation/drupal_test_results.json")
