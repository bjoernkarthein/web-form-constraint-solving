#!/bin/bash

source .env

# Check if required software is installed
if $NODE_COMMAND "--version"; then
    echo "Found node installation"
else
    echo "No node installation found"
    read
    exit 1
fi

if $CODEQL_PATH "--version"; then
    echo "Found codeql installation"
else
    echo "No codeql installation found"
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
