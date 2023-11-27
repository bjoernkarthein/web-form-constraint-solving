#!/bin/bash

# Check the operating system
if [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    # Linux
    node_command="node"
    pipenv_command="pipenv"
elif [ "$(expr substr $(uname -s) 1 10)" == "MINGW32_NT" ] || [ "$(expr substr $(uname -s) 1 10)" == "MINGW64_NT" ]; then
    # Windows
    node_command="node"
    pipenv_command="pipenv"
else
    echo "Unsupported operating system"
    exit 1
fi

# Set the path to your Node.js application
app_path="service/src/"
cd $app_path

# Start the Node.js server in the background
$node_command "app.js" &
echo $! > ../../scripts/server_pid.txt
