from datetime import datetime
import os
import aiofiles
from bson import ObjectId
from dotenv import dotenv_values

from fastapi import HTTPException, status, Request, UploadFile, status
from fastapi.responses import JSONResponse

from services.nlp_chain import (
    document_tokenizer_async,
    generate_tscc,
    qa_chain_async,
    setup_db,
)
from utils.fileUtils import find_file_by_uid, gen_uid
from middleware.apiMsg import APIMessages as apiMsg
from models.user import UserBase
from models.document import TSCC, DocTokens, UploadDoc


config = dotenv_values(".env")


def get_uploaded_files():
    # Define the directory where uploaded files are stored
    directory = config["UPLOAD_PATH"]
    log_prefix = (
        f"> [LOG]\t{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - GET_UPLOADED_FILES"
    )

    try:
        # Check if the directory exists
        if not os.path.exists(directory):
            # Log and raise a FileNotFoundError
            print(f"{log_prefix} - ERROR - FILES_NOT_FOUND")
            raise FileNotFoundError(apiMsg.FILES_NOT_FOUND)

        # Get a list of all files in the directory
        files = os.listdir(directory)
        # Filter out directories (if any)
        files = [
            file for file in files if os.path.isfile(os.path.join(directory, file))
        ]

        # Log and return the list of files or an empty list if no files found
        print(f"{log_prefix} - INFO - FILES_RETRIEVED - {len(files)} files found")
        return JSONResponse(
            status_code=status.HTTP_200_OK, content={"files": files if files else []}
        )
    except FileNotFoundError as e:
        # Handle file not found errors
        print(f"{log_prefix} - ERROR - FILE_NOT_FOUND - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        # Handle any other unexpected errors
        print(f"{log_prefix} - ERROR - UNEXPECTED_ERROR - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


async def upload_file(req: Request, file: UploadFile, user: UserBase):
    db = req.app.database[config["USER_DB"]]

    # Generate a unique file name using user's username
    uid = gen_uid(user.username, file.filename)

    # Construct the file path
    file_path = os.path.join(config["UPLOAD_PATH"], f"{uid}.pdf")
    log_prefix = (
        f"> [LOG]\t{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - UPLOAD_FILE - {uid}"
    )

    try:
        # Check if the directory exists, if not, create it
        if not os.path.exists(config["UPLOAD_PATH"]):
            os.makedirs(config["UPLOAD_PATH"])
            print(f"{log_prefix} - INFO - DIRECTORY_CREATED - {config['UPLOAD_PATH']}")

        # Check if the file already exists
        if os.path.exists(file_path):
            print(f"{log_prefix} - ERROR - FILE_EXISTS - {file.filename}")
            raise FileExistsError(apiMsg.FILE_ALREADY_EXISTS.format(file=file.filename))

        # Open the file in write-binary mode and save the content
        async with aiofiles.open(file_path, "wb") as out_file:
            content = await file.read()  # async read
            await out_file.write(content)  # async write
            print(f"{log_prefix} - INFO - FILE_SAVED - {file.filename}")

        # Add the uploaded file information to the user's uploaded_files list
        uploaded_file_info = UploadDoc(
            name=file.filename, uid=uid, uploaded_at=datetime.now()
        )

        # Update the user in MongoDB with the new uploaded file information
        update_result = await db.update_one(
            {"username": user.username},
            {"$push": {"uploaded_files": uploaded_file_info.dict()}},
        )

        if update_result.modified_count == 0:
            print(f"{log_prefix} - ERROR - USER_UPDATE_FAIL - {user.username}")
            raise ValueError(
                apiMsg.USER_FILE_INSERT_FAIL.format(
                    file=file.filename, user=user.username
                )
            )

        print(f"{log_prefix} - INFO - FILE_UPLOADED - {file.filename}")
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": apiMsg.FILE_UPLOADED.format(file=file.filename)},
        )

    except FileExistsError as e:
        print(f"{log_prefix} - ERROR - FILE_EXISTS_ERROR - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except Exception as e:
        # If an error occurs during upload, delete the partially uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)
        print(f"{log_prefix} - ERROR - UNEXPECTED_ERROR - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


async def delete_file(req: Request, user: UserBase, filename: str):
    db = req.app.database[config["USER_DB"]]

    # Generate the unique identifier for the file using the user's username and filename
    uid = gen_uid(user.username, filename)
    log_prefix = (
        f"> [LOG]\t{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - DELETE_FILE - {uid}"
    )

    try:
        # Construct the file path
        file_path = find_file_by_uid(config["UPLOAD_PATH"], uid)

        # Retrieve the user's files from the database
        user_files = await db.find_one(
            {"username": user.username}, {"uploaded_files": 1}
        )
        if not user_files:
            print(f"{log_prefix} - ERROR - FILE_NOT_FOUND_DB - {filename}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=apiMsg.FILE_NOT_FOUND_DB.format(file=filename),
            )

        # Get the list of all files
        uploaded_files = user_files.get("uploaded_files", [])
        # Check if the file is registered in the user_db
        file_registered = any(file["uid"] == uid for file in uploaded_files)
        if not file_registered:
            print(f"{log_prefix} - ERROR - FILE_NOT_REGISTERED - {filename}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=apiMsg.FILE_NOT_FOUND_DB.format(file=filename),
            )

        # Remove the file to be deleted
        updated_files = [file for file in uploaded_files if file["uid"] != uid]

        # Update the database with the updated list without the deleted file
        update_result = await db.update_one(
            {"username": user.username},
            {"$set": {"uploaded_files": updated_files}},
        )
        if update_result.modified_count == 0:
            print(f"{log_prefix} - ERROR - USER_FILE_DELETE_FAIL - {filename}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=apiMsg.USER_FILE_DELETE_FAIL.format(
                    file=filename, user=user.username
                ),
            )

        # Check if the file exists on the filesystem
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"{log_prefix} - INFO - FILE_DELETED - {filename}")
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"message": apiMsg.FILE_DELETED.format(file=filename)},
                )
            except OSError as e:
                print(f"{log_prefix} - ERROR - FILE_DELETE_OS_ERROR - {e.strerror}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error removing file '{file_path}': {e.strerror}",
                )
        else:
            print(f"{log_prefix} - INFO - FILE_DELETED_DB_ONLY - {filename}")
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"message": apiMsg.FILE_DELETED_DB_ONLY.format(file=filename)},
            )
    except HTTPException as e:
        raise e  # Re-raise the HTTP exceptions
    except Exception as e:
        # Log unexpected errors
        print(f"{log_prefix} - ERROR - UNEXPECTED_ERROR - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


async def get_tokens(req: Request, user: UserBase, filename: str):
    docs_db = req.app.database[config["DOCS_DB"]]
    uid = gen_uid(user.username, filename)
    log_prefix = (
        f"> [LOG]\t{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - GET_TOKENS - {uid}"
    )

    try:
        # Loop through the user's uploaded files to find the requested filename
        for doc in user.uploaded_files:
            if doc.name == filename:
                # Check if the document is tokenized
                if not doc.tokenized:
                    print(f"{log_prefix} - ERROR - NOT_TOKENIZED - {filename}")
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=apiMsg.NOT_TOKENIZED.format(file=filename),
                    )

                # Retrieve tokenized document from the database
                doc_tokens = await docs_db.find_one({"_id": ObjectId(doc.tokens_id)})
                if not doc_tokens:
                    print(f"{log_prefix} - ERROR - TOKENS_NOT_FOUND - {doc.tokens_id}")
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=apiMsg.TOKENS_NOT_FOUND.format(tokens_id=doc.tokens_id),
                    )

                doc_tokens = DocTokens(**doc_tokens)
                print(f"{log_prefix} - INFO - TOKEN_GET_SUCCESS - {doc.tokens_id}")
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "message": apiMsg.TOKEN_GET_SUCCESS.format(
                            tokens_id=doc.tokens_id
                        ),
                        "data": doc_tokens.dict(),
                    },
                )

        # If the document is not found in the user's uploaded files
        print(f"{log_prefix} - ERROR - USER_UPLOAD_NOT_FOUND - {filename}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=apiMsg.USER_UPLOAD_NOT_FOUND.format(file=filename),
        )
    except HTTPException as e:
        raise e  # Re-raise the HTTP exceptions
    except Exception as e:
        # Log unexpected errors
        print(f"{log_prefix} - ERROR - UNEXPECTED_ERROR - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


async def get_tscc(req: Request, user: UserBase, filename: str):
    tscc_db = req.app.database[config["TSCC_DB"]]
    uid = gen_uid(user.username, filename)
    log_prefix = (
        f"> [LOG]\t{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - GET_TSCC - {uid}"
    )

    try:
        # Loop through the user's uploaded files to find the requested filename
        for doc in user.uploaded_files:
            if doc.name == filename:
                # Check if the document is tokenized
                if not doc.tokenized:
                    print(f"{log_prefix} - ERROR - NOT_TOKENIZED - {filename}")
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=apiMsg.NOT_TOKENIZED.format(file=filename),
                    )

                # Check if the document is processed for TSCC
                if not doc.processed:
                    print(f"{log_prefix} - ERROR - NOT_TSCC_PROCESSED - {filename}")
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=apiMsg.NOT_TSCC_PROCESSED.format(file=filename),
                    )

                # Retrieve TSCC data from the database
                tscc_tokens = await tscc_db.find_one({"_id": ObjectId(doc.tscc_id)})
                if not tscc_tokens:
                    print(f"{log_prefix} - ERROR - TSCC_NOT_FOUND - {doc.tscc_id}")
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=apiMsg.TSCC_NOT_FOUND.format(tscc_id=doc.tscc_id),
                    )

                tscc_tokens = TSCC(**tscc_tokens)
                print(f"{log_prefix} - INFO - TSCC_GET_SUCCESS - {doc.tscc_id}")
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "message": apiMsg.TSCC_GET_SUCCESS.format(tscc_id=doc.tscc_id),
                        "data": tscc_tokens.dict(),
                    },
                )

        # If the document is not found in the user's uploaded files
        print(f"{log_prefix} - ERROR - USER_UPLOAD_NOT_FOUND - {filename}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=apiMsg.USER_UPLOAD_NOT_FOUND.format(file=filename),
        )
    except HTTPException as e:
        raise e  # Re-raise the HTTP exceptions
    except Exception as e:
        # Log unexpected errors
        print(f"{log_prefix} - ERROR - UNEXPECTED_ERROR - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


async def generate_tokens(
    req: Request, user: UserBase, filename: str, pdf_loader: str, overwrite: bool
):
    db = req.app.database
    user_db = db[config["USER_DB"]]
    docs_db = db[config["DOCS_DB"]]

    uid = gen_uid(user.username, filename)
    log_prefix = f"> [LOG]\t{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - GENERATE_TOKENS - {uid}"

    try:
        # Find the file path by uid
        file_path = find_file_by_uid(config["UPLOAD_PATH"], uid)

        # Check if the file exists locally
        if not os.path.exists(file_path):
            print(f"{log_prefix} - ERROR - FILE_NOT_FOUND_LOCAL")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=apiMsg.FILE_NOT_FOUND_LOCAL.format(file=filename),
            )

        # Iterate through user's uploaded files to find the target file
        for doc in user.uploaded_files:
            if doc.name == filename:
                # Check if the document is already tokenized and not set to overwrite
                if doc.tokenized and not overwrite:
                    print(f"{log_prefix} - ERROR - TOKENS_EXISTS")
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=apiMsg.TOKENS_EXISTS.format(file=filename),
                    )

                try:
                    # Start tokenization process
                    print(f"{log_prefix} - INFO - START_TOKENIZATION")
                    doc_tokens, pre_text_chunks = await document_tokenizer_async(
                        file_path, uid, pdf_loader
                    )
                except Exception as e:
                    print(f"{log_prefix} - ERROR - TOKENIZATION_FAIL - {str(e)}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=apiMsg.TOKENIZATION_FAIL.format(
                            file=filename, error=str(e)
                        ),
                    )

                # Set up vector database path
                vec_db_path = setup_db(uid, pre_text_chunks)
                doc.vec_db_path = str(vec_db_path)
                doc.embedded = True

                # If overwrite is enabled and document is already tokenized, update the tokens
                if doc.tokenized and overwrite:
                    try:
                        update_result = await docs_db.update_one(
                            {"_id": ObjectId(doc.tokens_id)},
                            {"$set": doc_tokens.dict()},
                        )
                        if update_result.modified_count == 0:
                            print(f"{log_prefix} - ERROR - TOKENS_UPDATE_FAIL")
                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail=apiMsg.TOKENS_UPDATE_FAIL.format(file=filename),
                            )
                    except Exception as e:
                        print(f"{log_prefix} - ERROR - TOKENS_UPDATE_FAIL - {str(e)}")
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=apiMsg.TOKENS_UPDATE_FAIL.format(
                                file=filename, error=str(e)
                            ),
                        )
                else:
                    # Insert new token data into the database
                    doc_insert_result = await docs_db.insert_one(doc_tokens.dict())
                    if not doc_insert_result.inserted_id:
                        print(f"{log_prefix} - ERROR - TOKENS_INSERT_FAIL - {str(e)}")
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=apiMsg.TOKENS_INSERT_FAIL.format(
                                file=filename, error=str(e)
                            ),
                        )

                    # Update document with new token ID
                    doc.tokens_id = str(doc_insert_result.inserted_id)
                    doc.tokenized = True

                    update_result = await user_db.update_one(
                        {"username": user.username, "uploaded_files.name": filename},
                        {"$set": {"uploaded_files.$": doc.dict()}},
                    )

                    if update_result.modified_count == 0:
                        print(f"{log_prefix} - ERROR - USER_TOKENS_INSERT_FAIL")
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=apiMsg.USER_TOKENS_INSERT_FAIL.format(
                                tokens_id=doc.tokens_id, user=user.username
                            ),
                        )

                print(f"{log_prefix} - INFO - TOKENIZATION_SUCCESS")
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "message": apiMsg.TOKENIZE_SUCCESS.format(file=filename),
                        "data": doc_tokens.dict(),
                    },
                )

        print(f"{log_prefix} - ERROR - USER_UPLOAD_NOT_FOUND")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=apiMsg.USER_UPLOAD_NOT_FOUND.format(file=filename),
        )
    except HTTPException as e:
        raise e  # Re-raise the HTTP exceptions
    except Exception as e:
        print(f"{log_prefix} - ERROR - UNEXPECTED_ERROR - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


async def query_rag(req: Request, user: UserBase, filename: str, query: str):
    log_prefix = f"> [LOG]\t{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - QUERY_RAG - {filename}"

    try:
        # Iterate through user's uploaded files to find the target file
        for doc in user.uploaded_files:
            if doc.name == filename:
                # Check if the document is tokenized
                if not doc.tokenized:
                    print(f"{log_prefix} - ERROR - FILE_NOT_YET_TOKENIZED")
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=apiMsg.FILE_NOT_YET_TOKENIZED.format(file=filename),
                    )

                # Check if the document is embedded
                if not doc.embedded:
                    print(f"{log_prefix} - ERROR - FILE_NOT_YET_EMBEDDED")
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=apiMsg.FILE_NOT_YET_EMBEDDED.format(file=filename),
                    )

                # Check if the vector database path exists
                if not os.path.exists(doc.vec_db_path):
                    print(f"{log_prefix} - ERROR - FILE_NOT_FOUND_LOCAL")
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=apiMsg.FILE_NOT_FOUND_LOCAL.format(file=doc.vec_db_path),
                    )

                # Set up the QA chain using the vector database path
                # qa_chain = setup_chain(doc.vec_db_path)
                response = await qa_chain_async(str(query), doc.vec_db_path)

                # Return the query response
                print(f"{log_prefix} - INFO - QUERY_SUCCESS")
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "message": apiMsg.RAG_QUERY_SUCCESS,
                        "data": {"query": str(query), "response": response["result"]},
                    },
                )

        # Raise an error if the file is not found in user's uploaded files
        print(f"{log_prefix} - ERROR - USER_UPLOAD_NOT_FOUND")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=apiMsg.USER_UPLOAD_NOT_FOUND.format(file=filename),
        )
    except HTTPException as e:
        raise e  # Re-raise the HTTP exceptions
    except Exception as e:
        # Log unexpected errors
        print(f"{log_prefix} - ERROR - UNEXPECTED_ERROR - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


async def process_tscc(req: Request, user: UserBase, filename: str, llm: str):
    log_prefix = f"> [LOG]\t{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - PROCESS_TSCC - {filename}"

    db = req.app.database
    user_db = db[config["USER_DB"]]
    docs_db = db[config["DOCS_DB"]]
    tscc_db = db[config["TSCC_DB"]]

    try:
        # Iterate through user's uploaded files to find the target file
        for doc in user.uploaded_files:
            if doc.name == filename:
                # Check if the document is tokenized
                if not doc.tokenized:
                    print(f"{log_prefix} - ERROR - NOT_TOKENIZED")
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=apiMsg.NOT_TOKENIZED.format(file=filename),
                    )

                # Check if the document has already been processed for TSCC
                if doc.processed:
                    print(f"{log_prefix} - ERROR - TSCC_ALREADY_PROCESSED")
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=apiMsg.TSCC_ALREADY_PROCESSED.format(file=filename),
                    )

                # Retrieve the document tokens from the database
                document = await docs_db.find_one({"_id": ObjectId(doc.tokens_id)})
                if not document:
                    print(f"{log_prefix} - ERROR - TOKENS_NOT_FOUND")
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=apiMsg.TOKENS_NOT_FOUND.format(tokens_id=doc.tokens_id),
                    )

                # Generate TSCC for the document
                tscc = await generate_tscc(document, llm)

                # Insert TSCC into the database
                tscc_insert_result = await tscc_db.insert_one(tscc.dict())
                if not tscc_insert_result.inserted_id:
                    print(f"{log_prefix} - ERROR - TSCC_DB_INSERT_FAIL")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=apiMsg.TSCC_DB_INSERT_FAIL.format(file=filename),
                    )

                # Update document with TSCC information
                doc.tscc_id = str(tscc_insert_result.inserted_id)
                doc.processed = True

                # Update user's uploaded files with the new document information
                update_result = await user_db.update_one(
                    {"username": user.username, "uploaded_files.name": filename},
                    {"$set": {"uploaded_files.$": doc.dict()}},
                )

                # Check if the update was successful
                if update_result.modified_count == 0:
                    print(f"{log_prefix} - ERROR - USER_TSCC_INSERT_FAIL")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=apiMsg.USER_TSCC_INSERT_FAIL.format(
                            user=user.username, file=filename
                        ),
                    )

                # Return success message with TSCC ID
                print(f"{log_prefix} - INFO - TSCC_PROCESS_SUCCESS")
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "message": apiMsg.TSCC_PROCESS_SUCCESS.format(file=filename),
                        "tscc_id": doc.tscc_id,
                    },
                )

        # Raise an error if the file is not found in user's uploaded files
        print(f"{log_prefix} - ERROR - USER_UPLOAD_NOT_FOUND")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=apiMsg.USER_UPLOAD_NOT_FOUND.format(file=filename),
        )
    except HTTPException as e:
        raise e  # Re-raise the HTTP exceptions
    except Exception as e:
        # Log unexpected errors
        print(f"{log_prefix} - ERROR - UNEXPECTED_ERROR - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


async def delete_tokens(req: Request, user: UserBase, filename: str):
    log_prefix = f"> [LOG]\t{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - DELETE_TOKENS - {filename}"

    db = req.app.database
    user_db = db[config["USER_DB"]]
    docs_db = db[config["DOCS_DB"]]

    try:
        # Iterate through user's uploaded files to find the target file
        for doc in user.uploaded_files:
            if doc.name == filename:
                # Check if the document is tokenized
                if not doc.tokenized:
                    print(f"{log_prefix} - ERROR - NOT_TOKENIZED")
                    return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content={"message": apiMsg.NOT_TOKENIZED.format(file=filename)},
                    )

                # Retrieve the document from the database
                doc_in_db = await docs_db.find_one({"_id": ObjectId(doc.tokens_id)})
                if not doc_in_db:
                    raise ValueError(
                        apiMsg.TOKENS_NOT_FOUND.format(tokens_id=doc.tokens_id)
                    )

                # Delete the document from the database
                delete_result = await docs_db.delete_one(
                    {"_id": ObjectId(doc.tokens_id)}
                )
                if delete_result.deleted_count == 0:
                    raise ValueError(
                        apiMsg.TOKENS_DELETE_FAIL.format(tokens_id=doc.tokens_id)
                    )

                # Update the document attributes in the UploadedDoc object
                doc.tokens_id = None
                doc.tokenized = False
                doc.embedded = False
                doc.vec_db_path = None

                # Update the user's uploaded_files with the modified UploadedDoc object
                update_result = await user_db.update_one(
                    {"username": user.username, "uploaded_files.name": filename},
                    {"$set": {"uploaded_files.$": doc.dict()}},
                )

                if update_result.modified_count == 0:
                    raise ValueError(
                        apiMsg.USER_TOKENS_DELETE_FAIL.format(
                            tokens_id=doc.tokens_id, user=user.username
                        )
                    )

                # Return success response
                print(f"{log_prefix} - INFO - TOKENS_DELETE_SUCCESS")
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "message": apiMsg.TOKENS_DELETE_SUCCESS.format(file=filename),
                        "data": doc.dict(),
                    },
                )

        # Raise an error if the file is not found in user's uploaded files
        print(f"{log_prefix} - ERROR - USER_UPLOAD_NOT_FOUND")
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
        print(f"{log_prefix} - ERROR - UNEXPECTED_ERROR - {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": str(e)},
        )


async def delete_tscc(req: Request, user: UserBase, filename: str):
    log_prefix = f"> [LOG]\t{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - DELETE_TSCC - {filename}"

    db = req.app.database
    user_db = db[config["USER_DB"]]
    tscc_db = db[config["TSCC_DB"]]

    try:
        # Iterate through user's uploaded files to find the target file
        for doc in user.uploaded_files:
            if doc.name == filename:
                # Check if the document exists in the TSCC collection
                tscc_in_db = await tscc_db.find_one({"_id": ObjectId(doc.tscc_id)})
                if not tscc_in_db:
                    raise ValueError(apiMsg.TSCC_NOT_FOUND.format(tscc_id=doc.tscc_id))

                # Delete the document from the TSCC collection
                delete_result = await tscc_db.delete_one({"_id": ObjectId(doc.tscc_id)})
                if delete_result.deleted_count == 0:
                    raise ValueError(apiMsg.TSCC_DB_DELETE_FAIL.format(file=filename))

                # Update the UploadedDoc object attributes
                doc.tscc_id = None
                doc.processed = False

                # Update the user's uploaded_files with the modified UploadedDoc object
                update_result = await user_db.update_one(
                    {"username": user.username, "uploaded_files.name": filename},
                    {"$set": {"uploaded_files.$": doc.dict()}},
                )

                if update_result.modified_count == 0:
                    raise ValueError(
                        apiMsg.USER_TSCC_DELETE_FAIL.format(
                            tscc_id=doc.tscc_id, user=user.username
                        )
                    )

                # Return success response
                print(f"{log_prefix} - INFO - TSCC_DELETE_SUCCESS")
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "message": apiMsg.TSCC_DB_DELETE_SUCCESS.format(file=filename),
                        "data": doc.dict(),
                    },
                )

        # Raise an error if the file is not found in user's uploaded files
        print(f"{log_prefix} - ERROR - USER_UPLOAD_NOT_FOUND")
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
        print(f"{log_prefix} - ERROR - UNEXPECTED_ERROR - {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": str(e)},
        )
