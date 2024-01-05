---
runme:
  id: 01HKCDGW3HZ1RYVV08RQWDD5QS
  version: v2.0
---

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

Change node and CodeQL path

## Getting Started

Clone the repository.

From the /automation directory run the following command to create and start a python virtual environment with all dependencies for the test automation.

```sh {"id":"01HKCDGW3HZ1RYVV08RFY3K3VN"}
pipenv install
pipenv shell

```

Go to the /service directory and run

```text {"id":"01HKCDGW3HZ1RYVV08RHN0PK2B"}
npm i

```

to install all required node dependencies.

To start all required services go to the application root directory and run

```sh {"id":"01HKCDGW3HZ1RYVV08RM0RRE44"}
./scripts/bootstrap.sh

```

To stop all services and clean up the resources run

```sh {"id":"01HKCDGW3HZ1RYVV08RMVKGFSD"}
./scrpts/teardown.sh
exit

```

## Custom Specifications

Something about template examples and ISLa github for more information on grammar and formula.
