import cProfile
import os
import sys
import yaml
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


from src.interaction.driver import TestAutomationDriver


def setup(driver: TestAutomationDriver) -> None:
    driver.web_driver.get("http://localhost/wp-admin")
    username = WebDriverWait(driver.web_driver, 5).until(
        EC.visibility_of_element_located(
            (
                By.ID,
                "user_login",
            )
        )
    )
    password = driver.web_driver.find_element(
        By.ID,
        "user_pass",
    )
    login = driver.web_driver.find_element(By.ID, "wp-submit")
    username.send_keys("user")
    password.send_keys("bitnami")
    login.click()

    WebDriverWait(driver.web_driver, 10).until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                "/html/body/div[1]/div[2]/div[2]/div[1]/div[3]/h1",
            )
        )
    )


if __name__ == "__main__":
    config = yaml.safe_load(open("evaluation/config_test.yml"))

    file = os.path.basename(__file__)[:-3]
    driver = TestAutomationDriver(
        config,
        "http://localhost/wp-admin/user-new.php",
    )

    setup(driver)
    driver.run_test(
        "evaluation/specifications/wordpress/specification_edited.json",
        "evaluation/wordpress_edited_test_results.json",
    )
