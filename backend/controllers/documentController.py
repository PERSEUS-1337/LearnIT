from datetime import datetime
import json
import os
import aiofiles
from dotenv import dotenv_values

from fastapi import status, Request, UploadFile, status
from fastapi.responses import JSONResponse

from services.nlp_chain import process_document
from utils.fileUtils import gen_uid
from utils.consts import UPLOAD_PATH, USER_DB
from middleware.apiMsg import APIMessages
from models.user import UserBase
from models.document import TSCC, UploadDoc


config = dotenv_values(".env")


async def get_uploaded_files():
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

    # Generate a unique file name using user's username
    uid = gen_uid(user.username, file.filename)

    # Construct the file path
    file_path = os.path.join(UPLOAD_PATH, uid)

    # Check if the directory exists, if not, create it
    if not os.path.exists(UPLOAD_PATH):
        os.makedirs(UPLOAD_PATH)

    try:
        # Check if the file already exists
        if os.path.exists(file_path):
            raise FileExistsError(f"File '{file.filename}' already exists")

        # Open the file in write-binary mode and save the content
        async with aiofiles.open(file_path, "wb") as out_file:
            content = await file.read()  # async read
            await out_file.write(content)  # async write

        # Add the uploaded file information to the user's uploaded_files list
        uploaded_file_info = UploadDoc(
            name=file.filename, uid=uid, uploaded_at=datetime.now()
        )
        uploaded_file_info = uploaded_file_info.model_dump()

        user.uploaded_files.append(uploaded_file_info)

        # Update the user in MongoDB with the new uploaded file information
        update_result = db.update_one(
            {"username": user.username},
            {"$set": {"uploaded_files": user.uploaded_files}},
        )

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": APIMessages.UPLOAD_SUCCESSFUL},
        )

    except FileExistsError as e:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"message": str(e)},  # Conflict status code
        )
    except Exception as e:
        # If an error occurs during upload, delete the partially uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"message": str(e)}
        )
    finally:
        # Make sure to clean up any resources here if needed
        pass


async def delete_file(req: Request, user: UserBase, filename: str):
    db = req.app.database[USER_DB]

    # Generate the unique identifier for the file using the user's username and filename
    uid = gen_uid(user.username, filename)

    # Construct the file path
    file_path = os.path.join(UPLOAD_PATH, uid)

    try:
        # Check if the file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File '{filename}' does not exist")

        # Remove the file from the filesystem
        os.remove(file_path)

        # Remove the file information from the user's uploaded_files list
        user_files = db.find_one({"username": user.username}, {"uploaded_files": 1})
        if user_files:
            uploaded_files = user_files.get("uploaded_files", [])
            updated_files = [file for file in uploaded_files if file["uid"] != uid]
            db.update_one(
                {"username": user.username},
                {"$set": {"uploaded_files": updated_files}},
            )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": f"File '{filename}' deleted successfully"},
        )
    except FileNotFoundError as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"message": str(e)}
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": str(e)},
        )


async def process_file(req: Request, user: UserBase, filename: str):
    db = req.app.database[USER_DB]

    # Generate the unique identifier for the file using the user's username and filename
    uid = gen_uid(user.username, filename)

    # Construct the file path
    file_path = os.path.join(UPLOAD_PATH, uid)
    try:
        # print(user.uploaded_files)
        
        # Check if the file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File '{filename}' does not exist in the server")
        
        for doc in user.uploaded_files:
            if doc.name == filename:
                chunks = process_document(uid)
                list_of_strings = [str(item) for item in chunks]
                

                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"message": list_of_strings},
                )
                

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": f"ok"},
        )
    except FileNotFoundError as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"message": str(e)}
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": str(e)},
        )
