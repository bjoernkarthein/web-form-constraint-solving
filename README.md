# Invariant Based Web Form Testing

## Prerequisites

### Software

| Required Software | Minimum Version |
| ----------------- | --------------- |
| Google Chrome     | -               |
| Node.js           | 16.13.1         |
| Python            | 3.10            |
| CodeQL            | -               |

## Setup

Clone the repository.

From the /automation directory run the following commands to create and start a python virtual environment with all dependencies for the test automation.

```sh
python3.10 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Go to the /service directory and run

```text
npm i
```

to install all required node dependencies.

Change the CodeQL path in .env file and run

```sh
node app.js
```

from the /service/src directory to start the service.

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
