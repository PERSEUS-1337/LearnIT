from datetime import datetime
import os
import aiofiles
from bson import ObjectId
from dotenv import dotenv_values

from fastapi import status, Request, UploadFile, status
from fastapi.responses import JSONResponse

from services.nlp_chain import document_tokenizer, generate_tscc
from utils.fileUtils import gen_uid
from middleware.apiMsg import APIMessages
from models.user import UserBase
from models.document import TSCC, UploadDoc


config = dotenv_values(".env")


async def get_uploaded_files():
    # Define the directory where uploaded files are stored
    directory = config["UPLOAD_PATH"]

    try:
        # Check if the directory exists
        if not os.path.exists(directory):
            # If directory does not exist, return an empty list
            return JSONResponse(status_code=status.HTTP_200_OK, content={"files": []})

        # Get a list of all files in the directory
        files = os.listdir(directory)
        # Filter out directories (if any)
        files = [
            file for file in files if os.path.isfile(os.path.join(directory, file))
        ]

        # Return the list of files or an empty list if no files found
        return JSONResponse(
            status_code=status.HTTP_200_OK, content={"files": files if files else []}
        )
    except OSError as e:
        # Handle OS errors
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": f"OS error: {str(e)}"},
        )
    except Exception as e:
        # Handle any other unexpected errors
        print(f"Unexpected error: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Internal server error"},
        )


async def upload_file(req: Request, file: UploadFile, user: UserBase):
    db = req.app.database[config["USER_DB"]]

    # Generate a unique file name using user's username
    uid = gen_uid(user.username, file.filename)

    # Construct the file path
    file_path = os.path.join(config["UPLOAD_PATH"], uid)

    try:
        # Check if the directory exists, if not, create it
        if not os.path.exists(config["UPLOAD_PATH"]):
            os.makedirs(config["UPLOAD_PATH"])

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
        
        # Update the user in MongoDB with the new uploaded file information
        update_result = db.update_one(
            {"username": user.username},
            {"$push": {"uploaded_files": uploaded_file_info.dict()}},
        )

        if update_result.modified_count == 0:
            raise ValueError(
                f"Failed to update user '{user.username}' with the new file information"
            )

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": "Upload successful"},
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
        print(f"Unexpected error: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": str(e)},
        )


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

        # Retrieve the user's files from the database
        user_files = db.find_one({"username": user.username}, {"uploaded_files": 1})
        if not user_files:
            raise ValueError(f"User '{user.username}' does not exist in the database")

        # Get the list of all files
        uploaded_files = user_files.get("uploaded_files", [])
        # Remove the file to be deleted
        updated_files = [file for file in uploaded_files if file["uid"] != uid]

        # Update the database with the updated list without the deleted file
        update_result = db.update_one(
            {"username": user.username},
            {"$set": {"uploaded_files": updated_files}},
        )
        if update_result.modified_count == 0:
            raise ValueError(
                f"Failed to update user '{user.username}' files in the database"
            )

        # Remove the file from the filesystem
        try:
            os.remove(file_path)
        except OSError as e:
            raise OSError(f"Error removing file '{file_path}': {e.strerror}")

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": f"File '{filename}' deleted successfully"},
        )
    except FileNotFoundError as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"message": str(e)}
        )
    except ValueError as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"message": str(e)}
        )
    except OSError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": f"File system error: {str(e)}"},
        )
    except Exception as e:
        # Log unexpected errors
        print(f"Unexpected error: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": str(e)},
        )


async def generate_tokens(req: Request, user: UserBase, filename: str):
    db = req.app.database
    user_db = db[config["USER_DB"]]
    docs_db = db[config["DOCS_DB"]]

    # Generate the unique identifier for the file using the user's username and filename
    uid = gen_uid(user.username, filename)

    # Construct the file path
    file_path = os.path.join(config["UPLOAD_PATH"], uid)
    print(file_path)

    try:
        # Check if the file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File '{filename}' does not exist on the server")

        file_found = False
        for doc in user.uploaded_files:
            if doc.name == filename:
                file_found = True

                if doc.tokenized:
                    return JSONResponse(
                        status_code=status.HTTP_409_CONFLICT,
                        content={
                            "message": f"File '{filename}' has already been tokenized"
                        },
                    )

                # Extract tokens and create DocTokens object
                try:
                    doc_tokens = document_tokenizer(file_path, "PyMuPDFLoader")
                except Exception as e:
                    raise ValueError(
                        f"Tokenization failed for file '{filename}': {str(e)}"
                    )

                # Store the DocTokens document in the docs collection
                try:
                    doc_tokens_id = docs_db.insert_one(doc_tokens.dict()).inserted_id
                except Exception as e:
                    raise ValueError(
                        f"Failed to insert DocTokens into docs_db: {str(e)}"
                    )

                # Update the UploadDoc object with the tokens_id
                doc.tokens_id = str(doc_tokens_id)
                doc.tokenized = True

                # Update the user document with the modified UploadDoc object
                update_result = user_db.update_one(
                    {"username": user.username, "uploaded_files.name": filename},
                    {"$set": {"uploaded_files.$": doc.dict()}},
                )

                if update_result.modified_count == 0:
                    raise ValueError(
                        f"Failed to update user '{user.username}' with tokenized file '{filename}'"
                    )

                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"message": doc_tokens.dict()},
                )

        if not file_found:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "message": f"File '{filename}' not found in user uploaded files"
                },
            )
    except FileNotFoundError as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"message": str(e)}
        )
    except ValueError as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"message": str(e)}
        )
    except Exception as e:
        # Log unexpected errors
        print(f"Unexpected error: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": str(e)},
        )


async def process_tscc(req: Request, user: UserBase, filename: str):
    db = req.app.database
    user_db = db[config["USER_DB"]]
    docs_db = db[config["DOCS_DB"]]
    tscc_db = db[config["TSCC_DB"]]

    # Generate the unique identifier for the file using the user's username and filename
    uid = gen_uid(user.username, filename)

    try:
        # Check if file exists in the uploaded file list of user
        for doc in user.uploaded_files:
            if doc.name == filename:
                # Check if the file is already tokenized and ready for tscc processing
                if not doc.tokenized:
                    return JSONResponse(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        content={
                            "message": f"File '{filename}' has not yet been tokenized. Please generate tokens for '{filename}' first"
                        },
                    )

                if not doc.processed:
                    # Retrieve the tokenized document from the docs collection
                    document = docs_db.find_one({"_id": ObjectId(doc.tokens_id)})
                    if not document:
                        return JSONResponse(
                            status_code=status.HTTP_404_NOT_FOUND,
                            content={
                                "message": f"Tokenized document with ID '{doc.tokens_id}' not found in docs_db"
                            },
                        )

                    tscc = generate_tscc(document)

                    # Insert the TSCC document into the tscc collection
                    tscc_insert_result = tscc_db.insert_one(tscc.dict())
                    if not tscc_insert_result.inserted_id:
                        raise ValueError("Failed to insert TSCC document into tscc_db")

                    # Update the UploadDoc object inside the user
                    doc.tscc_id = str(tscc_insert_result.inserted_id)
                    doc.processed = True

                    # Update the user document with the modified UploadDoc object
                    user_db.update_one(
                        {"username": user.username, "uploaded_files.name": filename},
                        {"$set": {"uploaded_files.$": doc.dict()}},
                    )

                    return JSONResponse(
                        status_code=status.HTTP_200_OK,
                        content={
                            "message": f"File '{filename}' has been successfully processed for TSCC",
                            "tscc_id": doc.tscc_id,
                        },
                    )
                else:
                    return JSONResponse(
                        status_code=status.HTTP_409_CONFLICT,
                        content={
                            "message": f"File '{filename}' has already been processed"
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
    except ValueError as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"message": str(e)}
        )
    except Exception as e:
        # Log unexpected errors
        print(f"Unexpected error: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": str(e)},
        )


async def delete_tokens(req: Request, user: UserBase, filename: str):
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
                print(f"Deleting document with tokens_id: {doc.tokens_id}")

                # Check if the document exists in the docs collection
                doc_in_db = docs_db.find_one({"_id": ObjectId(doc.tokens_id)})
                if not doc_in_db:
                    raise ValueError(
                        f"Document with tokens_id '{doc.tokens_id}' does not exist in docs_db"
                    )

                # Delete the document in the docs collection
                delete_result = docs_db.delete_one({"_id": ObjectId(doc.tokens_id)})
                if delete_result.deleted_count == 0:
                    raise ValueError(
                        f"Failed to delete document with tokens_id '{doc.tokens_id}'"
                    )

                # Modify the UploadedDoc object inside the user
                doc.tokens_id = None
                doc.tokenized = False

                # Update the user document with the modified UploadDoc object
                user_db.update_one(
                    {"username": user.username, "uploaded_files.name": filename},
                    {"$set": {"uploaded_files.$": doc.dict()}},
                )

                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "message": f"Updated User {user.username}'s files and deleted {doc.name}'s tokens from the database"
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
    except ValueError as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"message": str(e)}
        )
    except Exception as e:
        # Log unexpected errors
        print(f"Unexpected error: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": str(e)},
        )


async def delete_tscc(req: Request, user: UserBase, filename: str):
    db = req.app.database
    user_db = db[config["USER_DB"]]
    tscc_db = db[config["TSCC_DB"]]

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
                print(f"Deleting document with tscc_id: {doc.tscc_id}")

                # Check if the document exists in the docs collection
                tscc_in_db = tscc_db.find_one({"_id": ObjectId(doc.tscc_id)})
                if not tscc_in_db:
                    raise ValueError(
                        f"Document with tscc_id '{doc.tscc_id}' does not exist in tscc_db"
                    )

                # Delete the document in the docs collection
                delete_result = tscc_db.delete_one({"_id": ObjectId(doc.tscc_id)})
                if delete_result.deleted_count == 0:
                    raise ValueError(
                        f"Failed to delete document with tscc_id '{doc.tscc_id}'"
                    )

                # Modify the UploadedDoc object inside the user
                doc.tscc_id = None
                doc.processed = False

                # Update the user document with the modified UploadDoc object
                user_db.update_one(
                    {"username": user.username, "uploaded_files.name": filename},
                    {"$set": {"uploaded_files.$": doc.dict()}},
                )

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
    except ValueError as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"message": str(e)}
        )
    except Exception as e:
        # Log unexpected errors
        print(f"Unexpected error: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": str(e)},
        )
