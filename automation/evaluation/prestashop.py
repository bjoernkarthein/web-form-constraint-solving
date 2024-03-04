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


def fill_cart(driver: TestAutomationDriver) -> None:
    driver.web_driver.get("http://localhost/")
    thumb = WebDriverWait(driver.web_driver, 5).until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "/html/body/main/section/div/div/div/section/section/section[1]/div/div[2]/article/div/div[1]/a/picture/img",
            )
        )
    )
    thumb.click()
    driver.web_driver.find_element(
        By.XPATH,
        "/html/body/main/section/div/div/div/section/div[1]/div[2]/div[2]/div[2]/form/div[2]/div/div[2]/button",
    ).click()
    time.sleep(2)


if __name__ == "__main__":
    config = yaml.safe_load(open("evaluation/config.yml"))

    # initialize profiler
    pr = cProfile.Profile()

    file = os.path.basename(__file__)[:-3]
    driver = TestAutomationDriver(
        config,
        "http://localhost/order",
        profiler=pr,
        file=file,
    )

    fill_cart(driver)
    driver.run_analysis()
