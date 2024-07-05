from datetime import datetime
import os
import aiofiles
from bson import ObjectId
from dotenv import dotenv_values

from fastapi import status, Request, UploadFile, status
from fastapi.responses import JSONResponse

from services.nlp_chain import (
    document_tokenizer,
    generate_tscc,
    retrieve_db,
    setup_chain,
    setup_db,
)
from utils.fileUtils import find_file_by_uid, gen_uid
from middleware.apiMsg import APIMessages as apiMsg
from models.user import UserBase
from models.document import TSCC, DocTokens, UploadDoc


config = dotenv_values(".env")


async def get_uploaded_files():
    # Define the directory where uploaded files are stored
    directory = config["UPLOAD_PATH"]

    try:
        # Check if the directory exists
        if not os.path.exists(directory):
            # If directory does not exist, return an empty list
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"message": apiMsg.FILES_NOT_FOUND},
            )

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
            content={"message": "OS error", "data": str(e)},
        )
    except Exception as e:
        # Handle any other unexpected errors
        print(f"Unexpected error: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Internal server error", "data": str(e)},
        )


async def upload_file(req: Request, file: UploadFile, user: UserBase):
    db = req.app.database[config["USER_DB"]]

    # Generate a unique file name using user's username
    uid = gen_uid(user.username, file.filename)

    # Construct the file path
    file_path = os.path.join(config["UPLOAD_PATH"], f"{uid}.pdf")

    try:
        # Check if the directory exists, if not, create it
        if not os.path.exists(config["UPLOAD_PATH"]):
            os.makedirs(config["UPLOAD_PATH"])

        # Check if the file already exists
        if os.path.exists(file_path):
            raise FileExistsError(apiMsg.FILE_ALREADY_EXISTS.format(file=file.filename))

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
            raise ValueError(apiMsg.USER_FILE_INSERT_FAIL.format(file=file.filename, user=user.username))

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": apiMsg.FILE_UPLOADED.format(file=file.filename)},
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

    try:
        # Construct the file path
        file_path = find_file_by_uid(config["UPLOAD_PATH"], uid)

        # Retrieve the user's files from the database
        user_files = db.find_one({"username": user.username}, {"uploaded_files": 1})
        if not user_files:
            raise ValueError(apiMsg.FILE_NOT_FOUND_DB.format(file=filename))
        
        # Get the list of all files
        uploaded_files = user_files.get("uploaded_files", [])
        # Check if the file is registered in the user_db
        file_registered = any(file["uid"] == uid for file in uploaded_files)
        if not file_registered:
            raise ValueError(apiMsg.FILE_NOT_FOUND_DB.format(file=filename))

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
            raise ValueError(apiMsg.USER_FILE_DELETE_FAIL.format(file=filename, user=user.username))

         # Check if the file exists on the filesystem
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"message": apiMsg.FILE_DELETED.format(file=filename)},
                )
            except OSError as e:
                raise OSError(f"Error removing file '{file_path}': {e.strerror}")
        else:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"message": apiMsg.FILE_DELETED_DB_ONLY.format(file=filename)},
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

    try:
        # Construct the file path
        file_path = find_file_by_uid(config["UPLOAD_PATH"], uid)

        # Check if the file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(apiMsg.FILE_NOT_FOUND_LOCAL.format(file=filename))

        for doc in user.uploaded_files:
            if doc.name == filename:

                if doc.tokenized:
                    return JSONResponse(
                        status_code=status.HTTP_409_CONFLICT,
                        content={
                            "message": apiMsg.TOKENS_EXISTS.format(
                                file=filename
                            )
                        },
                    )

                # Extract tokens and create DocTokens object
                try:
                    doc_tokens, pre_text_chunks = document_tokenizer(
                        file_path, uid, "PyMuPDFLoader"
                    )
                except Exception as e:
                    raise ValueError(
                        apiMsg.TOKENIZATION_FAIL.format(file=filename, error=str(e))
                    )

                # This is where we inject the function of prepping the ChromaDb to be retrieved later when we start doing the QnA
                vec_db_path = setup_db(uid, pre_text_chunks)
                doc.vec_db_path = str(vec_db_path)
                doc.embedded = True

                # Store the DocTokens document in the docs collection
                try:
                    doc_tokens_id = docs_db.insert_one(doc_tokens.dict()).inserted_id
                except Exception as e:
                    raise ValueError(
                        apiMsg.TOKENS_INSERT_FAIL.format(file=filename, error=str(e))
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
                        apiMsg.USER_TOKENS_INSERT_FAIL.format(
                             tokens_id=doc.tokens_id, user=user.username
                        )
                    )

                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "message": apiMsg.TOKENIZE_SUCCESS.format(file=filename),
                        "data": doc_tokens.dict(),
                    },
                )

            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"message": apiMsg.USER_UPLOAD_NOT_FOUND.format(file=filename)},
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

async def get_tokens(req: Request, user: UserBase, filename: str):
    docs_db = req.app.database[config["DOCS_DB"]]
    
    try:
        for doc in user.uploaded_files:
            if doc.name == filename:
                if not doc.tokenized:
                    return JSONResponse(
                        status_code=status.HTTP_409_CONFLICT,
                        content={
                            "message": apiMsg.NOT_TOKENIZED.format(file=filename)
                        },
                    )

                doc_tokens = docs_db.find_one({"_id": ObjectId(doc.tokens_id)})
                if not doc_tokens:
                    return JSONResponse(
                        status_code=status.HTTP_404_NOT_FOUND,
                        content={
                            "message": apiMsg.TOKENS_NOT_FOUND.format(
                                tokens_id=doc.tokens_id
                            )
                        },
                    )
                    
                doc_tokens = DocTokens(**doc_tokens)
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "message": apiMsg.TOKEN_GET_SUCCESS.format(tokens_id=doc.tokens_id),
                        "data": doc_tokens.dict(),
                    },
                )

            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"message": apiMsg.USER_UPLOAD_NOT_FOUND.format(file=filename)},
            )
    except Exception as e:
        # Log unexpected errors
        print(f"Unexpected error: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": str(e)},
        )


async def get_tscc(req: Request, user: UserBase, filename: str):
    tscc_db = req.app.database[config["TSCC_DB"]]
    
    try:
        for doc in user.uploaded_files:
            if doc.name == filename:
                if not doc.tokenized:
                    return JSONResponse(
                        status_code=status.HTTP_409_CONFLICT,
                        content={
                            "message": apiMsg.NOT_TOKENIZED.format(file=filename)
                        },
                    )
                    
                if not doc.processed:
                    return JSONResponse(
                        status_code=status.HTTP_409_CONFLICT,
                        content={
                            "message": apiMsg.NOT_TSCC_PROCESSED.format(file=filename)
                        },
                    )

                tscc_tokens = tscc_db.find_one({"_id": ObjectId(doc.tscc_id)})
                if not tscc_tokens:
                    return JSONResponse(
                        status_code=status.HTTP_404_NOT_FOUND,
                        content={
                            "message": apiMsg.TSCC_NOT_FOUND.format(
                                tscc_id=doc.tscc_id
                            )
                        },
                    )
                    
                tscc_tokens = TSCC(**tscc_tokens)
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "message": apiMsg.TSCC_GET_SUCCESS.format(tscc_id=doc.tscc_id),
                        "data": tscc_tokens.dict(),
                    },
                )

            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"message": apiMsg.USER_UPLOAD_NOT_FOUND.format(file=filename)},
            )
    except Exception as e:
        # Log unexpected errors
        print(f"Unexpected error: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": str(e)},
        )
    

async def query_rag(req: Request, user: UserBase, filename: str, query: str):
    try:
        for doc in user.uploaded_files:
            if doc.name == filename:
                if not doc.tokenized:
                    return JSONResponse(
                        status_code=status.HTTP_409_CONFLICT,
                        content={
                            "message": apiMsg.FILE_NOT_YET_TOKENIZED.format(file=filename)
                        },
                    )

                if not doc.embedded:
                    return JSONResponse(
                        status_code=status.HTTP_409_CONFLICT,
                        content={
                            "message": apiMsg.FILE_NOT_YET_EMBEDDED.format(file=filename)
                        },
                    )

                if not os.path.exists(doc.vec_db_path):
                    raise OSError(apiMsg.FILE_NOT_FOUND_LOCAL.format(file=doc.vec_db_path))

                qa_chain = setup_chain(doc.vec_db_path)
                response = qa_chain(str(query))

                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "message": apiMsg.RAG_QUERY_SUCCESS,
                        "data": {"query": str(query), "response": response["result"]},
                    },
                )

        raise FileNotFoundError(apiMsg.USER_UPLOAD_NOT_FOUND.format(file=filename))
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
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": f"File system error: {str(e)}"},
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

    try:
        for doc in user.uploaded_files:
            if doc.name == filename:
                if not doc.tokenized:
                    return JSONResponse(
                        status_code=status.HTTP_409_CONFLICT,
                        content={
                            "message": apiMsg.NOT_TOKENIZED.format(
                                file=filename
                            )
                        },
                    )

                if doc.processed:
                    return JSONResponse(
                        status_code=status.HTTP_409_CONFLICT,
                        content={
                            "message": apiMsg.TSCC_ALREADY_PROCESSED.format(
                                file=filename
                            )
                        },
                    )
                
                document = docs_db.find_one({"_id": ObjectId(doc.tokens_id)})
                if not document:
                    return JSONResponse(
                        status_code=status.HTTP_404_NOT_FOUND,
                        content={
                            "message": apiMsg.TOKENS_NOT_FOUND.format(
                                tokens_id=doc.tokens_id
                            )
                        },
                    )

                tscc = generate_tscc(document)

                tscc_insert_result = tscc_db.insert_one(tscc.dict())
                if not tscc_insert_result.inserted_id:
                    raise ValueError(apiMsg.TSCC_DB_INSERT_FAIL.format(file=filename))

                doc.tscc_id = str(tscc_insert_result.inserted_id)
                doc.processed = True

                update_result = user_db.update_one(
                    {"username": user.username, "uploaded_files.name": filename},
                    {"$set": {"uploaded_files.$": doc.dict()}},
                )
                
                if update_result.modified_count == 0:
                    raise ValueError(
                        apiMsg.USER_TSCC_INSERT_FAIL.format(
                            user=user.username, file=filename
                        )
                    )

                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "message": apiMsg.TSCC_PROCESS_SUCCESS.format(file=filename),
                        "tscc_id": doc.tscc_id,
                    },
                )
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": apiMsg.USER_UPLOAD_NOT_FOUND},
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

    try:
        for doc in user.uploaded_files:
            if doc.name == filename:

                if not doc.tokenized:
                    return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content={"message": apiMsg.NOT_TOKENIZED.format(file=filename)},
                    )

                doc_in_db = docs_db.find_one({"_id": ObjectId(doc.tokens_id)})
                if not doc_in_db:
                    raise ValueError(
                        apiMsg.TOKENS_NOT_FOUND.format(tokens_id=doc.tokens_id)
                    )


                delete_result = docs_db.delete_one({"_id": ObjectId(doc.tokens_id)})
                if delete_result.deleted_count == 0:
                    raise ValueError(
                        apiMsg.TOKENS_DELETE_FAIL.format(tokens_id=doc.tokens_id)
                    )

                doc.tokens_id = None
                doc.tokenized = False
                doc.embedded = False
                doc.vec_db_path = None

                update_result = user_db.update_one(
                    {"username": user.username, "uploaded_files.name": filename},
                    {"$set": {"uploaded_files.$": doc.dict()}},
                )
                
                if update_result.modified_count == 0:
                    raise ValueError(
                        apiMsg.USER_TOKENS_DELETE_FAIL.format(
                            tokens_id=doc.tokens_id, user=user.username
                        )
                    )

                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "message": apiMsg.TOKENS_DELETE_SUCCESS.format(file=filename),
                        "data": doc.dict(),
                    },
                )

        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": apiMsg.USER_UPLOAD_NOT_FOUND.format(file=filename)},
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

    try:
        for doc in user.uploaded_files:
            if doc.name == filename:
                # Check if the document exists in the docs collection
                tscc_in_db = tscc_db.find_one({"_id": ObjectId(doc.tscc_id)})
                if not tscc_in_db:
                    raise ValueError(apiMsg.TSCC_NOT_FOUND.format(tscc_id=doc.tscc_id))

                # Delete the document in the docs collection
                delete_result = tscc_db.delete_one({"_id": ObjectId(doc.tscc_id)})
                if delete_result.deleted_count == 0:
                    raise ValueError(apiMsg.TSCC_DB_DELETE_FAIL.format(file=filename))

                # Modify the UploadedDoc object inside the user
                doc.tscc_id = None
                doc.processed = False

                # Update the user document with the modified UploadDoc object
                update_result = user_db.update_one(
                    {"username": user.username, "uploaded_files.name": filename},
                    {"$set": {"uploaded_files.$": doc.dict()}},
                )
                
                if update_result.modified_count == 0:
                    raise ValueError(
                        apiMsg.USER_TSCC_DELETE_FAIL.format(
                            tscc_id=doc.tscc_id, user=user.username
                        )
                    )

                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "message": apiMsg.TSCC_DB_DELETE_SUCCESS.format(file=filename),
                        "data": doc.dict(),
                    },
                )

        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": apiMsg.USER_UPLOAD_NOT_FOUND.format(file=filename)},
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
