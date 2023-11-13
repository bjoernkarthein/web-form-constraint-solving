#!/bin/bash

# Check if the PID file exists
if [ -f "scripts/server_pid.txt" ]; then
    # Read the PID from the file
    server_pid=$(<scripts/server_pid.txt)

    # Kill the Node.js server process
    kill $server_pid

    echo "Node.js server stopped."
    # Remove the PID file
    rm scripts/server_pid.txt
else
    echo "PID file not found. Server may not be running."
fi
