#!/bin/bash

# Command to start the FastAPI application using Uvicorn
COMMAND="cd backend; nohup uvicorn main:app --reload > nohup.log 2>&1 &"

# Execute the command
eval $COMMAND
