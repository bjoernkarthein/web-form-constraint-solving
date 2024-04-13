import cProfile
import os
import sys
import yaml
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from selenium.webdriver.common.by import By

from evaluation.util.helpers import Evaluation
from src.interaction.driver import TestAutomationDriver


def agree(driver: TestAutomationDriver) -> None:
    driver.web_driver.find_element(By.ID, "agreed").click()
    time.sleep(2)


if __name__ == "__main__":
    config = yaml.safe_load(open("evaluation/config.yml"))

    # evaluation
    pr = cProfile.Profile()
    file = os.path.basename(__file__)[:-3]
    eval = Evaluation(pr, file)
    eval.start_profiling()

    driver = TestAutomationDriver(
        config,
        "https://localhost/ucp.php?mode=register",
        setup_function=agree,
        evaluation=eval,
    )

    driver.run_analysis()
