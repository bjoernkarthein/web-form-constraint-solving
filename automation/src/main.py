import getopt
import sys
import yaml

from driver import TestAutomationDriver

"""
Main module

Handles all command line options and arguments.
"""


def main(argv):
    """Handle command line arguments and start the test automation."""

    try:
        opts, _ = getopt.getopt(argv, '?hu:', ['help', 'url='])
    except getopt.GetoptError:
        print('Wrong format provided')
        print_help()
        sys.exit()

    if len(opts) == 0:
        print_help()
        sys.exit()

    for opt, arg in opts:
        if opt in ('-?', '-h', '--help'):
            print_help()
            sys.exit()
        if opt in ('-u', '--url'):
            config = yaml.safe_load(open('../config/config.yml'))
            test_automation_driver = TestAutomationDriver(config, arg)
            test_automation_driver.run()


def print_help():
    """Print the help message."""

    print("""usage: python main.py [option] -u <url>
Options and arguments:
-?, -h, --help: print this help message and exit
-u, --url:      url of the web page that includes the form which is to be tested""")


if __name__ == '__main__':
    main(sys.argv[1:])
