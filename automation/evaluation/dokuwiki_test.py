import os
import sys
import yaml

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.interaction.driver import TestAutomationDriver
from evaluation.util.helpers import Evaluation

if __name__ == "__main__":
    config = yaml.safe_load(open("evaluation/config_test.yml"))

    # evaluation
    file = os.path.basename(__file__)[:-3]
    eval = Evaluation(file=f"{file}_stats")

    # run test
    driver = TestAutomationDriver(
        config,
        setup_function=None,
    )

    driver.run_test(
        "evaluation/specifications/dokuwiki/specification.json",
        f"evaluation/{file}_report.json",
    )
