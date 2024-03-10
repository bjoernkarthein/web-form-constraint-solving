import cProfile
import os
import sys
import yaml

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.interaction.driver import TestAutomationDriver

if __name__ == "__main__":
    config = yaml.safe_load(open("evaluation/config_test.yml"))

    # run test
    file = os.path.basename(__file__)[:-3]
    driver = TestAutomationDriver(
        config,
        setup_function=None,
    )

    driver.run_test("evaluation/specifications/dokuwiki/specification.json", "evaluation/dokuwiki_test_results.json")
