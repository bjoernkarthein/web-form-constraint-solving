# Invariant Based Web Form Testing

## Prerequisites

### Software

| Required Software | Minimum Version |
| ----------------- | --------------- |
| Google Chrome     | -               |
| Node.js           | 16.13.1         |
| Python            | 3.10            |

### Setup

Chrome needs to be added to the PATH

## Getting started

Clone the repository.

From the root run the following command to initialize all services. This creates a python virtual environment for the test automation.

```
./scripts/init.sh
```

To install all required python packages go into the _automation_ directory and run

```
./venv/Scripts/actiate
```

on Windows or

```
source venv/bin/activate
```

on Linux and install all required packages with

```
python -m pip install -r requirements.txt
```

To start all required services run

```
./scripts/start.sh
```

from the application root.
