#!/bin/bash

# Command to start the FastAPI application using Uvicorn
COMMAND="cd backend; uvicorn main:app --reload"

# Execute the command
eval $COMMAND
