import cProfile
import os
import sys
import yaml
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from evaluation.util.helpers import Evaluation
from src.interaction.driver import TestAutomationDriver


if __name__ == "__main__":
    config = yaml.safe_load(open("evaluation/config.yml"))

    # evaluation
    pr = cProfile.Profile()
    file = os.path.basename(__file__)[:-3]
    eval = Evaluation(pr, file)
    eval.start_profiling()

    driver = TestAutomationDriver(
        config,
        "http://localhost/web/login",
        evaluation=eval,
    )

    driver.run_analysis()
