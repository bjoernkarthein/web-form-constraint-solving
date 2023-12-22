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

### Setup

Optionally change node and codeql path

## Getting started

Clone the repository.

From the /automation directory run the following command to create and start a python virtual environment with all dependencies for the test automation.

```
pipenv install
pipenv shell
```

Go to the /service directory and run

```
npm i
```

to install all required node dependencies.

To start all required services go to the application root directory and run

```
./scripts/bootstrap.sh
```

To stop all services and clean up the resources run

```
./scrpts/teardown.sh
exit
```
