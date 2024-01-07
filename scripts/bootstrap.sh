#!/bin/bash

source .env

# Check if required software is installed
echo "Checking Node installation"
if $NODE_COMMAND "--version"; then
    echo "Found Node installation"
else
    echo "No Node installation found here: " $NODE_COMMAND
    read
    exit 1
fi

echo "Checking CodeQL installation"
if $CODEQL_PATH "--version"; then
    echo "Found CodeQL installation"
else
    echo "No CodeQL installation found here: " $CODEQL_PATH
    read
    exit 1
fi

# Start the Node.js server in the background
app_path="service/src/"
cd $app_path
$NODE_COMMAND "app.js" &
pid=$!

sleep 2

# Check if the Node.js server is running
if ps -p $pid > /dev/null; then
    echo "Node.js server started successfully with PID: $pid"
    echo $pid > ../../scripts/server_pid.txt
else
    echo "Error: Node.js server failed to start"
    read
    exit 1
fi

exit 0
