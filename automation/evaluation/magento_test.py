import os
import sys
import yaml

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.interaction.driver import TestAutomationDriver


if __name__ == "__main__":
    config = yaml.safe_load(open("evaluation/config_test.yml"))

    driver = TestAutomationDriver(
        config,
        "http://localhost/customer/account/create/",
    )

    driver.run_test(
        "evaluation/specifications/magento/specification.json",
        "evaluation/magento_test_results.json",
    )
