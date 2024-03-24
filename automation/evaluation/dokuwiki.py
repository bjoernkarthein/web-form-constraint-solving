import cProfile
import os
import sys
import yaml

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.interaction.driver import TestAutomationDriver
from util.helpers import Evaluation

if __name__ == "__main__":
    config = yaml.safe_load(open("evaluation/config.yml"))

    # evaluation
    pr = cProfile.Profile()
    file = os.path.basename(__file__)[:-3]
    eval = Evaluation(pr, file)
    eval.start_profiling()

    # run analysis
    driver = TestAutomationDriver(
        config,
        "http://localhost/start?do=register",
        setup_function=None,
        evaluation=eval,
    )

    driver.run_analysis()
