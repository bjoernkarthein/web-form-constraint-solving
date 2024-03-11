import cProfile
import os
import sys
import yaml
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.interaction.driver import TestAutomationDriver

if __name__ == "__main__":
    config = yaml.safe_load(open("evaluation/config_test.yml"))

    file = os.path.basename(__file__)[:-3]
    driver = TestAutomationDriver(
        config,
        "http://localhost/",
    )

    driver.run_test(
        "evaluation/specifications/ghost/specification.json",
        "evaluation/ghost_test_results.json",
    )