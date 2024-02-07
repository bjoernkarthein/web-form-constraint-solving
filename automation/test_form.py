import getopt
import sys
import yaml

from src.interaction.driver import TestAutomationDriver

"""
Test module

Serves as the entry point for testing a web form with a given specification.
"""


def main(argv):
    """Handle command line arguments and start the test automation."""

    try:
        opts, _ = getopt.getopt(argv, "?h?s:", ["help", "specification-file="])
    except getopt.GetoptError:
        print("Wrong format provided")
        print_help()
        sys.exit()

    specification_file = None
    for opt, arg in opts:
        if opt in ("-?", "-h", "--help"):
            print_help()
            sys.exit()
        if opt in ("-s", "--specification-file"):
            specification_file = arg

    config = yaml.safe_load(open("config/test_config.yml"))
    test_automation_driver = TestAutomationDriver(config)
    test_automation_driver.run_test(specification_file)


def print_help():
    """Print the help message."""

    print(
        """usage: python test.py [option]
Options and arguments:
-?, -h, --help:                 Print this help message and exit
-s, --specification-file:       Optional path to a specification file that is used to generate inputs.
                                For an example of the structure of such a specification file see https://projects.cispa.saarland/s8bjkart/invariant-based-web-form-testing/-/blob/main/automation/pre-built-specifications/specification_example.json?ref_type=heads
                                If no file is provided an existing specification file is used.
                                Run 'analyse.py' to extract the secification for a given url automatically"""
    )


if __name__ == "__main__":
    main(sys.argv[1:])
