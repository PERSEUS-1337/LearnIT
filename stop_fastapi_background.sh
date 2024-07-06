#!/bin/bash

# Search for the Uvicorn process
PID=$(ps aux | grep -m 1 "nohup uvicorn" | awk '{print $2}')

# Check if PID was found
if [ -z "$PID" ]; then
    echo "Uvicorn process not found."
else
    # Terminate the Uvicorn process
    echo "Stopping Uvicorn..."
    kill $PID
    echo "Uvicorn stopped."
fi
