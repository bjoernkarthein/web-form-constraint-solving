import getopt
import sys
import yaml

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src.interaction.driver import TestAutomationDriver
from evaluation.util.helpers import EvaluationStub

"""
Analysis module

Serves as the entry point to analyse a given url and extract
client side validation constraints.
"""


def setup(automation: TestAutomationDriver) -> None:
    automation.web_driver.get("http://localhost:3000/static/example")
    WebDriverWait(automation.web_driver, 5).until(
        EC.visibility_of_element_located(
            (By.ID, "loginForm")
        )
    )

    user = automation.web_driver.find_element(By.ID, "username")
    password = automation.web_driver.find_element(By.ID, "password")
    submit = automation.web_driver.find_element(By.XPATH, "/html/body/form/button")
    
    user.send_keys("user")
    password.send_keys("12345678")
    submit.click()

def get_to_form(automation: TestAutomationDriver) -> None:
    add = WebDriverWait(automation.web_driver, 5).until(
        EC.visibility_of_element_located(
            (By.ID, "openFormButton")
        )
    )
    add.click()

def main(argv):
    """Handle command line arguments and start the analysis."""

    try:
        opts, _ = getopt.getopt(argv, "?hu:", ["help", "url="])
    except getopt.GetoptError:
        print("Unknown argument structure")
        print_help()
        sys.exit()

    if len(opts) == 0:
        print_help()
        sys.exit()

    for opt, arg in opts:
        if opt in ("-?", "-h", "--help"):
            print_help()
            sys.exit()
        if opt in ("-u", "--url"):
            config = yaml.safe_load(open("config/analysis_config.yml"))
            test_automation_driver = TestAutomationDriver(
                config,
                arg,
                setup_function=get_to_form,
                evaluation=EvaluationStub(),  # TODO: remove when evaluation is done
            )

            setup(test_automation_driver)
            test_automation_driver.run_analysis()


def print_help():
    """Print the help message."""

    print(
        """usage: python analyse.py -u <url> [option]
Options and arguments:
-?, -h, --help: print this help message and exit
-u, --url:      url of the web page that includes the form which is to be tested"""
    )


if __name__ == "__main__":
    main(sys.argv[1:])
