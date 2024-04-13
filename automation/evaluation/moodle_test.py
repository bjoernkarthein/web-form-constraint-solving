import os
import sys
import yaml

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from selenium.webdriver.common.by import By

from src.interaction.driver import TestAutomationDriver


def setup(driver: TestAutomationDriver) -> None:
    driver.web_driver.get("http://localhost/login/index.php")
    username = driver.web_driver.find_element(By.ID, "username")
    password = driver.web_driver.find_element(By.ID, "password")
    login = driver.web_driver.find_element(By.ID, "loginbtn")
    username.send_keys("user")
    password.send_keys("bitnami")
    login.click()


if __name__ == "__main__":
    config = yaml.safe_load(open("evaluation/config_test.yml"))

    driver = TestAutomationDriver(
        config,
        "http://localhost/course/edit.php",
    )

    setup(driver)
    driver.run_test(
        "evaluation/specifications/moodle/specification_edited.json",
        "evaluation/moodle_edited_test_results.json",
    )
