import cProfile
import os
import sys
import yaml

import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from selenium.webdriver.common.by import By

from src.interaction.driver import TestAutomationDriver


def login(driver: TestAutomationDriver) -> None:
    driver.web_driver.get("http://localhost/login")
    username = driver.web_driver.find_element(By.ID, "username")
    password = driver.web_driver.find_element(By.ID, "password")
    submit = driver.web_driver.find_element(By.ID, "login-submit")
    username.send_keys("user")
    password.send_keys("bitnami1")
    submit.click()


if __name__ == "__main__":
    config = yaml.safe_load(open("evaluation/config.yml"))

    # initialize profiler
    pr = cProfile.Profile()

    file = os.path.basename(__file__)[:-3]
    driver = TestAutomationDriver(
        config,
        "http://localhost/projects/new",
        profiler=pr,
        file=file,
    )

    login(driver)
    driver.run_analysis()
