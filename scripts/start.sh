#!/bin/bash

# Check the operating system
if [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    # Linux
    node_command="node"
elif [ "$(expr substr $(uname -s) 1 10)" == "MINGW32_NT" ] || [ "$(expr substr $(uname -s) 1 10)" == "MINGW64_NT" ]; then
    # Windows
    node_command="node"
else
    echo "Unsupported operating system"
    exit 1
fi

# Set the path to your Node.js application
app_path="instrumentation/src/app.js"

# Start the Node.js server in the background
$node_command $app_path > /dev/null 2>&1 &
echo $! > scripts/server_pid.txt

echo "Node.js server started in the background."
