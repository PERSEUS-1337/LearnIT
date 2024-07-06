#!/bin/bash

# Command to start the FastAPI application using Uvicorn
START_COMMAND="/usr/bin/python3 /usr/local/bin/uvicorn main:app --reload"

# Search for the Uvicorn process using the exact start command
PID=$(ps aux | grep -F "$START_COMMAND" | grep -v grep | awk '{print $2}')

# Check if PID was found
if [ -z "$PID" ]; then
    echo "Uvicorn process not found."
else
    # Terminate the Uvicorn process
    echo "Stopping Uvicorn..."
    kill $PID
    echo "Uvicorn stopped."
fi
