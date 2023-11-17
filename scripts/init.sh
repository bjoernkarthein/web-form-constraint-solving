#!/bin/bash

# Check the operating system
if [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    # Linux
    python_executable="python"
elif [ "$(expr substr $(uname -s) 1 10)" == "MINGW32_NT" ] || [ "$(expr substr $(uname -s) 1 10)" == "MINGW64_NT" ]; then
    # Windows
    python_executable="python"
else
    echo "Unsupported operating system"
    exit 1
fi

# Set the desired virtual environment name
venv_name="venv"

# Create and activate the virtual environment
cd automation
$python_executable -m pip install virtualenv

if [ ! -d "venv" ]; then
  $python_executable -m venv $venv_name
fi

echo "Virtual environment $venv_name created."
