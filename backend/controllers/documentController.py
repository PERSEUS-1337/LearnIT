from dotenv import dotenv_values
from fastapi import Depends, HTTPException, status, Request, Body, FastAPI, UploadFile, File, status
from fastapi.responses import JSONResponse

from middleware.apiMsg import APIMessages

from typing import Annotated, Optional
from fastapi.responses import JSONResponse
import aiofiles
import os


config = dotenv_values(".env")

async def upload_file(req: Request, file: UploadFile):
    # Define the directory where you want to save the file
    directory = "uploaded_files"
    
    # Check if the directory exists, if not, create it
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    try:
        # Construct the full path to the file
        file_path = os.path.join(directory, file.filename)
        # return {"filename": file.filename}
        
        # # Open the file in write-binary mode and save the content
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read() # async read
            await out_file.write(content) # async write
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={'message': str(e)}
        )
    else:
        return JSONResponse(
            status_code=200,
            content={"result": 'success'}
        )
    

async def get_uploaded_files(req: Request):
    # Define the directory where uploaded files are stored
    directory = "uploaded_files"
    
    # Check if the directory exists
    if not os.path.exists(directory):
        # If directory does not exist, return an empty list
        return []
    
    try:
        # Get a list of all files in the directory
        files = os.listdir(directory)
        # Filter out directories (if any)
        files = [file for file in files if os.path.isfile(os.path.join(directory, file))]
        return files
    except Exception as e:
        # Handle any errors and return an empty list
        return []
