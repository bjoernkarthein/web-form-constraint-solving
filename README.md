# FormWhisperer: Solving Web Form Constraints Automatically

## Prerequisites

### Software

| Required Software | Minimum Version |
| ----------------- | --------------- |
| Google Chrome     | -               |
| Node.js           | 16.13.1         |
| Python            | 3.10            |
| CodeQL            | -               |

## Setup

FormWhisperer uses Selenium WebDriver for Chrome to automate all browser interactions. Before starting the constraint extraction it is important to ensure that the version of the ChromeDriver is compatible with the version of Chrome on your local machine. The `/chromedriver` directory holds a pre-selected version of the ChromeDriver for windows and linux. You can simply download any version of Chromedriver from [here](https://developer.chrome.com/docs/chromedriver/downloads) and replace the files in the right directory.

To install all required dependencies, from the `/automation` directory run the following commands to create and start a python virtual environment with all dependencies for the test automation.

```sh
python3.10 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Go to the `/service` directory and run

```text
npm i
```

to install all required node dependencies.

Set the CODEQL_PATH variable in the `.env` file to point to your CodeQL location and run

```sh
node app.js
```

from the `/service/src` directory to start the service.

## Getting Started

The entry points to both parts of FormWhisperer are python scripts in the `/automation` directory. The two parts are the constraint extraction (`extract_specification.py`) and the form testing (`test_form.py`).

### Constraint Extraction

During constraint extraction, the web form is filled out and requests are potentially sent to the application server. For this reason you should only use this tool for testing purposes on applications that are controlled by you and not public. To set up the constraint extraction for a specific web form you can edit the `extract_specification.py` file in the `automation` directory.

The python script provides two methods for setting up the constraint extraction via simple selenium automation. First, we offer a blank `setup` method that allows to handle any automation steps in order to enable the driver to successfully access the web page with the form that we would like to test. An example for such a setup step would be to log in before being able to access the application. The code of the setup function is executed before the Selenium WebDriver attempts to load the URL of the form page. In addition to the setup function, we offer the ability to define a routine to access the form, after the URL is successfully loaded, via the `access_form method`. This is handy if the form is hidden initially when loading the page and opens in a modal when pressing a button for example. The code example below shows an implementation of both functions that first authenticates the user, loads the form page and then clicks a button to open the form.

```py
def setup(automation: TestAutomationDriver) -> None:
    automation.web_driver.get("<login-url>")
    WebDriverWait(automation.web_driver, 5).until(
        EC.visibility_of_element_located((By.ID, "loginForm"))
    )

    user = automation.web_driver.find_element(By.ID, "username")
    password = automation.web_driver.find_element(By.ID, "password")
    submit = automation.web_driver.find_element(By.XPATH, "/html/body/form/button")

    user.send_keys("user")
    password.send_keys("12345678")
    submit.click()


def access_form(automation: TestAutomationDriver) -> None:
    add = WebDriverWait(automation.web_driver, 5).until(
        EC.visibility_of_element_located((By.ID, "openFormButton"))
    )
    add.click()
```

The constraint extraction phase can be configured via the `analysis_config.yml` in the `/config` directory. By default, HTML and JavaScript are analyzed and for each form field we generate a magic value sequence of length two and do a single analysis round. To start the constraint extraction, we run `python extract_specification.py -u <url-of-the-form-page>` from the `/automation` directory.

Once the constraint extraction is complete, the extracted specification can be found in the `/specification` folder in the `/automation` directory. The folder constains one main `specification.json` file and several `.bnf` and `.isla` files that define the properties for all form inputs. You can see an example of an `specification.json` file below. It contains the url of the form page, an entry for each identified form input or control and a reference to the submit element. For each control we can see a `"grammar"` and a `"formula"` entry that hold the names of the respective files for that field.

```json
{
  "url": "https://some-web-page-with-a-form.com",
  "controls": [
    {
      "name": "mail",
      "type": "email",
      "reference": {
        "access_method": "id",
        "access_value": "mail"
      },
      "grammar": "grammar_example.bnf",
      "formula": "formula_example.isla"
    },
    {
      "name": "username",
      "type": "text",
      "reference": {
        "access_method": "xpath",
        "access_value": "/html/body/form/input[1]"
      },
      "grammar": "...",
      "formula": "..."
    },
    {
      "name": "age",
      "type": "radio",
      "reference": {
        "access_method": "name",
        "access_value": "of-legal-age"
      },
      "options": [
        {
          "reference": {
            "access_method": "xpath",
            "access_value": "/html/body/form/input[2]"
          },
          "value": "1"
        },
        {
          "reference": {
            "access_method": "xpath",
            "access_value": "/html/body/form/input[3]"
          },
          "value": "0"
        }
      ],
      "grammar": "...",
      "formula": "..."
    }
  ],
  "submit": {
    "access_method": "xpath",
    "access_value": "/html/form/button[1]"
  }
}
```

To change the specification for any input, simply alter the respective `.bnf` and `.isla` file.

### Form Testing

Given a valid specification, FormWhisperer allows you to generate many test inpput values on the basis of that specification. You can either use the automatic constraint extraction to obtain such a specification or simply create your own custom one. The `/automation/pre-built-specifications` directory provides example files for a specification, grammar and formula in case you want to create your own.

The form testing can be configured via the `/automation/config/test_config.yml` file. It allows you to specify how many valid and invalid form instances should be generated during testing. Invalid instances are created by selecting random form fields and generating values that purposely violate the given specification.

To test the form with a previously automatically extracted specification you simply run `python test_form.py` from the automation directory, making sure that the setup functions are correctly configured in the testing script. If you wanted to provide your own custom specification to test any web form, you would be able to do so by passing the path to a custom specification file via the `-s` command line flag.

The results are saved in a JSON file in the `/automation/results` directory. For every round of testing, the result file lists all generated form values with their respective validity and the response of the application:

```json
{
  "test_round_1": {
    "generated_values": [
      "(validity: ValidityEnum.VALID, value: private)",
      "(validity: ValidityEnum.VALID, value: )0N9kkpwVtJ2cb=wcINN>rx%1",
      "(validity: ValidityEnum.VALID, value: )",
      "(validity: ValidityEnum.VALID, value: .@H)",
      "(validity: ValidityEnum.VALID, value: 0001-04-01)",
      "(validity: ValidityEnum.VALID, value: 1)",
      "(validity: ValidityEnum.VALID, value: 1)",
      "(validity: ValidityEnum.VALID, value: 0)",
      "(validity: ValidityEnum.VALID, value: j)"
    ],
    "server_response": "200 OK"
  },
  ...
  "test_round_10": {
    "generated_values": [
      "(validity: ValidityEnum.VALID, value: public)",
      "(validity: ValidityEnum.INVALID, value: A2#k)",
      "(validity: ValidityEnum.VALID, value: )",
      "(validity: ValidityEnum.VALID, value: .@a)",
      "(validity: ValidityEnum.VALID, value: 0400-01-01)",
      "(validity: ValidityEnum.VALID, value: 1)",
      "(validity: ValidityEnum.VALID, value: 1)",
      "(validity: ValidityEnum.VALID, value: 1)",
      "(validity: ValidityEnum.VALID, value: [)"
    ],
    "server_response": "Submission did not cause any outgoing requests."
  },
  "stats": {
    "total": 10,
    "valid": 5,
    "invalid": 5,
    "tp": 5,
    "fp": 0,
    "tn": 5,
    "fn": 0
  }
}
```

## Tests

### Unit Tests

#### Automation

From automation directory

```sh
python -m unittest discover -s tests/unit -b
```

to run all tests without logs, or

```sh
python -m unittest tests.unit.<file-name>.<class-name>.<test-name>
```

to run any specific test alone.

#### Service

From /service/src directory

```sh
npm test --tests=./tests/
```
