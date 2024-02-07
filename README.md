# Invariant Based Web Form Testing

## Prerequisites

### Software

| Required Software | Minimum Version |
| ----------------- | --------------- |
| Google Chrome     | -               |
| Node.js           | 16.13.1         |
| Python            | 3.10            |
| Pipenv            | 2023.11.15      |
| CodeQL            | -               |

## Setup

Clone the repository.

From the /automation directory run the following command to create and start a python virtual environment with all dependencies for the test automation.

```sh
pipenv install
pipenv shell
```

Go to the /service directory and run

```text
npm i
```

to install all required node dependencies.

Change node and CodeQL path in environment file
To start all required services go to the application root directory and run

```sh
./scripts/bootstrap.sh
```

To stop all services and clean up the resources run

```sh
./scrpts/teardown.sh
exit
```

## Getting Started

## Tests

### Unit Tests

automation: from automation directory

```sh
python -m unittest discover -s tests/unit -b
```

service: from service directory

```sh
npm test
```

## Custom Specifications

Something about template examples and ISLa github for more information on grammar and formula.
