import sys
import getopt
import yaml

from driver import TestAutomationDriver


def main(argv):
    global automation

    try:
        opts, args = getopt.getopt(argv, "?hu:", ["help", "url="])
    except getopt.GetoptError:
        print("Wrong format provided")
        print_help()
        sys.exit()

    if len(opts) == 0:
        print_help()
        sys.exit()

    for opt, arg in opts:
        if opt in ("-?", "-h", "--help"):
            print_help()
            sys.exit()
        if opt in ("-u", "--url"):
            config = yaml.safe_load(open("config.yml"))
            print(config)
            test_automation_driver = TestAutomationDriver()
            test_automation_driver.load_page(arg)


def print_help():
    print("""usage: python main.py [option] -u <url>
Options and arguments:
-?, -h, --help: print this help message and exit
-u, --url:      url of the web page that includes the form which is to be tested""")


if __name__ == "__main__":
    main(sys.argv[1:])
