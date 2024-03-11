import cProfile
import os
import sys
import yaml
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.interaction.driver import TestAutomationDriver


def agree(driver: TestAutomationDriver) -> None:
    driver.web_driver.find_element(By.ID, "agreed").click()
    time.sleep(2)


if __name__ == "__main__":
    config = yaml.safe_load(open("evaluation/config_test.yml"))

    file = os.path.basename(__file__)[:-3]
    driver = TestAutomationDriver(
        config,
        "https://localhost/ucp.php?mode=register",
        setup_function=agree,
    )

    driver.run_test(
        "evaluation/specifications/phpbb/specification.json",
        "evaluation/phpbb_test_results.json",
    )
