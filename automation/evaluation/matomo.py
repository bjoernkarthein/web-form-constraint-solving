import cProfile
import os
import sys
import yaml

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from evaluation.util.helpers import Evaluation
from src.interaction.driver import TestAutomationDriver


def login(driver: TestAutomationDriver) -> None:
    driver.web_driver.get("http://localhost/")
    username = driver.web_driver.find_element(By.ID, "login_form_login")
    password = driver.web_driver.find_element(By.ID, "login_form_password")
    submit = driver.web_driver.find_element(By.ID, "login_form_submit")
    username.send_keys("user")
    password.send_keys("bitnami")
    submit.click()


def create_page(driver: TestAutomationDriver) -> None:
    driver.web_driver.find_element(By.CLASS_NAME, "addSite").click()
    element = WebDriverWait(driver.web_driver, 5).until(
        EC.visibility_of_element_located(
            (By.XPATH, "//div[@class='modal open']//button[1]")
        )
    )
    element.click()


if __name__ == "__main__":
    config = yaml.safe_load(open("evaluation/config.yml"))

    # evaluation
    pr = cProfile.Profile()
    file = os.path.basename(__file__)[:-3]
    eval = Evaluation(pr, file)
    eval.start_profiling()

    driver = TestAutomationDriver(
        config,
        "http://localhost/index.php?module=SitesManager&action=index&idSite=1&period=day&date=today",
        setup_function=create_page,
        evaluation=eval,
    )

    login(driver)
    driver.run_analysis()
