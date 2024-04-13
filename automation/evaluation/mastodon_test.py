import os
import sys
import yaml

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.interaction.driver import TestAutomationDriver


if __name__ == "__main__":
    config = yaml.safe_load(open("evaluation/config_test.yml"))

    driver = TestAutomationDriver(
        config,
        "http://localhost/auth/sign_in",
    )

    driver.run_test(
        "evaluation/specifications/mastodon/specification.json",
        "evaluation/mastodon_test_results.json",
    )
