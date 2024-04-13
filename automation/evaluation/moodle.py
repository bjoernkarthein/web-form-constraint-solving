import cProfile
import os
import sys
import yaml
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from selenium.webdriver.common.by import By

from evaluation.util.helpers import Evaluation
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
    config = yaml.safe_load(open("evaluation/config.yml"))

    # evaluation
    pr = cProfile.Profile()
    file = os.path.basename(__file__)[:-3]
    eval = Evaluation(pr, file)
    eval.start_profiling()

    driver = TestAutomationDriver(
        config,
        "http://localhost/course/edit.php",
        evaluation=eval,
    )

    setup(driver)
    driver.run_analysis()
