import cProfile
import os
import sys
import yaml

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.interaction.driver import TestAutomationDriver

if __name__ == "__main__":
    config = yaml.safe_load(open("evaluation/config.yml"))

    # setup

    # initialize profiler
    pr = cProfile.Profile()

    # run analysis
    file = os.path.basename(__file__)[:-3]
    driver = TestAutomationDriver(
        config,
        "http://localhost/start?do=register",
        setup_function=None,
        profiler=pr,
        file=file,
    )
    driver.run_analysis()
