from datetime import datetime
import os
import aiofiles
import uuid
from dotenv import dotenv_values

from fastapi import status, Request, UploadFile, status
from fastapi.responses import JSONResponse

from utils.dbUtils import get_user_data
from utils.consts import UPLOAD_PATH, USER_DB
from middleware.apiMsg import APIMessages
from models.user import UserBase
from models.document import UploadDoc


config = dotenv_values(".env")


async def get_uploaded_files(req: Request):
    # Define the directory where uploaded files are stored
    directory = UPLOAD_PATH

    # Check if the directory exists
    if not os.path.exists(directory):
        # If directory does not exist, return an empty list
        return JSONResponse(status_code=200, content={"files": []})

    try:
        # Get a list of all files in the directory
        files = os.listdir(directory)
        # Filter out directories (if any)
        files = [
            file for file in files if os.path.isfile(os.path.join(directory, file))
        ]
        if not files:
            # If no files found, return an empty list
            return JSONResponse(status_code=200, content={"files": []})
        else:
            # Return the list of files
            return JSONResponse(status_code=200, content={"files": files})
    except Exception as e:
        # Handle any errors and return an empty list
        return JSONResponse(
            status_code=500, content={"message": "Internal server error"}
        )


async def upload_file(req: Request, file: UploadFile, user: UserBase):
    db = req.app.database[USER_DB]
    user_data = get_user_data(db, user.username)

    # Generate a unique identifier for the file
    unique_identifier = str(uuid.uuid4())

    # Check if the directory exists, if not, create it
    if not os.path.exists(UPLOAD_PATH):
        os.makedirs(UPLOAD_PATH)

    try:
        # Construct the file path
        file_path = os.path.join(UPLOAD_PATH, unique_identifier + "_" + file.filename)

        # Check if the file already exists
        if os.path.exists(file_path):
            raise FileExistsError(f"File '{file.filename}' already exists")

        # Open the file in write-binary mode and save the content
        async with aiofiles.open(file_path, "wb") as out_file:
            content = await file.read()  # async read
            await out_file.write(content)  # async write

        # Add the uploaded file information to the user's uploaded_files list
        uploaded_file_info = UploadDoc(
            filename=file.filename, date_uploaded=datetime.now()
        )
        uploaded_file_info = uploaded_file_info.model_dump
        user_data.uploaded_files.append(uploaded_file_info)

        # Update the user in MongoDB with the new uploaded file information
        update_result = db.update_one(
            {"username": user_data.username},
            {"$set": {"uploaded_files": user_data.uploaded_files}},
        )

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": APIMessages.UPLOAD_SUCCESSFUL},
        )

    except FileExistsError as e:
        return JSONResponse(
            status_code=409, content={"message": str(e)}  # Conflict status code
        )
    except Exception as e:
        return JSONResponse(status_code=400, content={"message": str(e)})


async def tokenize_file(req: Request):
    pass
