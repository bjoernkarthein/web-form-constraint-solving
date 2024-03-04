import cProfile
import os
import sys
import yaml

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.interaction.driver import TestAutomationDriver


if __name__ == "__main__":
    config = yaml.safe_load(open("evaluation/config.yml"))

    # initialize profiler
    pr = cProfile.Profile()

    file = os.path.basename(__file__)[:-3]
    driver = TestAutomationDriver(
        config,
        "http://localhost/index.php?title=Special:CreateAccount&returnto=Main+Page",
        profiler=pr,
        file=file,
    )

    driver.run_analysis()
