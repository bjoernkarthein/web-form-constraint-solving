# Invariant Based Web Form Testing

## Prerequisites

### Software

| Required Software | Minimum Version |
| ----------------- | --------------- |
| Google Chrome     | -               |
| Node.js           | 16.13.1         |
| Python            | 3.10            |
| Pipenv            | 2023.11.15      |

### Setup

Chrome needs to be added to the PATH

## Getting started

Clone the repository.

From the /automation directory run the following command to create and start a python virtual environment with all dependencies for the test automation.

```
pipenv install
pipenv shell
```

To start all required services go to the application root directory and run

```
./scripts/bootstrap.sh
```

To stop all services and clean up the resources run

```
./scrpts/teardown.sh
exit
```
