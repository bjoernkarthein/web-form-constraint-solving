import cProfile
import os
import sys
import yaml
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from evaluation.util.helpers import Evaluation
from src.interaction.driver import TestAutomationDriver


def setup(driver: TestAutomationDriver) -> None:
    driver.web_driver.get("http://localhost/#/Login")
    username = WebDriverWait(driver.web_driver, 5).until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                "/html/body/app-root/div/scrm-login-ui/div/form/div[2]/div/div[1]/input",
            )
        )
    )
    password = driver.web_driver.find_element(
        By.XPATH,
        "/html/body/app-root/div/scrm-login-ui/div/form/div[2]/div/div[2]/input",
    )
    login = driver.web_driver.find_element(By.ID, "login-button")
    username.send_keys("user")
    password.send_keys("bitnami")
    login.click()
    time.sleep(5)


def wait_for_form(driver: TestAutomationDriver) -> None:
    WebDriverWait(driver.web_driver, 5).until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                "/html/body/app-root/div/scrm-create-record/div/scrm-record-container/div/div/div/div/div/div/scrm-record-content/div/div/div/div/scrm-field-layout/form",
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

    driver = TestAutomationDriver(
        config,
        "http://localhost/#/contacts/edit?return_module=Contacts&return_action=DetailView",
        setup_function=wait_for_form,
        evaluation=eval,
    )

    setup(driver)
    driver.run_analysis()
