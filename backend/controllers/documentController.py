from datetime import datetime
import os
import aiofiles
from bson import ObjectId
from dotenv import dotenv_values

from fastapi import status, Request, UploadFile, status
from fastapi.responses import JSONResponse

from services.nlp_chain import summarize_tokens
from utils.fileUtils import gen_uid
from middleware.apiMsg import APIMessages
from models.user import UserBase
from models.document import TSCC, UploadDoc


config = dotenv_values(".env")


async def get_uploaded_files():
    # Define the directory where uploaded files are stored
    directory = config["UPLOAD_PATH"]

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
    db = req.app.database[config["USER_DB"]]

    # Generate a unique file name using user's username
    uid = gen_uid(user.username, file.filename)

    # Construct the file path
    file_path = os.path.join(config["UPLOAD_PATH"], uid)

    # Check if the directory exists, if not, create it
    if not os.path.exists(config["UPLOAD_PATH"]):
        os.makedirs(config["UPLOAD_PATH"])

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
    db = req.app.database[config["USER_DB"]]

    # Generate the unique identifier for the file using the user's username and filename
    uid = gen_uid(user.username, filename)

    # Construct the file path
    file_path = os.path.join(config["UPLOAD_PATH"], uid)
    print(file_path)

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


async def process_tscc(req: Request, user: UserBase, filename: str):
    db = req.app.database
    user_db = db[config["USER_DB"]]
    docs_db = db[config["DOCS_DB"]]

    # Generate the unique identifier for the file using the user's username and filename
    uid = gen_uid(user.username, filename)

    # Construct the file path
    file_path = os.path.join(config["UPLOAD_PATH"], uid)
    try:
        # Check if the file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File '{filename}' does not exist in the server")

        for doc in user.uploaded_files:
            if doc.name == filename:
                # Extract tokens and create TSCC object
                tscc = summarize_tokens(uid)
                tscc.uid = str(ObjectId())  # Set unique identifier for TSCC

                # Store the TSCC document in the docs collection
                tscc_id = docs_db.insert_one(tscc.dict()).inserted_id

                # Update the UploadDoc object with the tscc_uid
                doc.tscc_uid = str(tscc_id)
                doc.processed = True

                # Update the user document with the modified UploadDoc object
                user_db.update_one(
                    {"username": user.username, "uploaded_files.name": filename},
                    {"$set": {"uploaded_files.$": doc.dict()}},
                )

                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"message": tscc.dict()},
                )

        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": f"File '{filename}' not found in user uploaded files"},
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


async def delete_tscc(req: Request, user: UserBase, filename: str):
    db = req.app.database
    user_db = db[config["USER_DB"]]
    docs_db = db[config["DOCS_DB"]]

    # Generate the unique identifier for the file using the user's username and filename
    uid = gen_uid(user.username, filename)

    # Construct the file path
    file_path = os.path.join(config["UPLOAD_PATH"], uid)
    try:
        # Check if the file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File '{filename}' does not exist on the server")

        for doc in user.uploaded_files:
            if doc.name == filename:
                # Log the document details
                print(f"Deleting document with tscc_uid: {doc.tscc_uid}")

                # Convert tscc_uid to ObjectId if necessary
                tscc_uid = (
                    ObjectId(doc.tscc_uid)
                    if ObjectId.is_valid(doc.tscc_uid)
                    else doc.tscc_uid
                )

                # Delete the document in the docs collection
                delete_result = docs_db.delete_one({"_id": tscc_uid})

                if delete_result.deleted_count == 0:
                    raise Exception("Failed to delete document from docs database")

                # Modify the UploadedDoc object inside the user
                doc.tscc_uid = None
                doc.processed = False

                # Update the user document with the modified UploadDoc object
                update_result = user_db.update_one(
                    {"username": user.username, "uploaded_files.name": filename},
                    {"$set": {"uploaded_files.$": doc.dict()}},
                )

                if update_result.modified_count == 0:
                    raise Exception("Failed to update user document")

                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "message": f"Updated User {user.username}'s files and deleted {doc.name}'s tscc from the database"
                    },
                )

        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": f"File '{filename}' not found in user uploaded files"},
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
