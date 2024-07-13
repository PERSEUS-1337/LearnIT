from datetime import datetime
import os
from typing import List, Optional
import aiofiles
from bson import ObjectId
from dotenv import dotenv_values

from fastapi import BackgroundTasks, HTTPException, status, Request, UploadFile, status
from fastapi.responses import JSONResponse

from services.nlp_chain import (
    document_tokenizer_async,
    generate_tscc,
    qa_chain_async,
    setup_db,
)
from utils.fileUtils import find_file_by_uid, gen_uid, update_doc_status
from middleware.apiMsg import APIMessages as apiMsg
from models.user import UserBase
from models.document import TSCC, DocTokens, ProcessStatus, UploadDoc


config = dotenv_values(".env")

async def get_file_details(req: Request, user: UserBase, filename: str) -> Optional[UploadDoc]:
    db = req.app.database
    user_db = db[config["USER_DB"]]
    files_db = db[config["FILES_DB"]]

    log_prefix = f"> [LOG]\t{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - GET_UPLOADED_FILE - {user.username} - {filename}"

    try:
        # Retrieve the user's _id from the user_db
        user_data = await user_db.find_one({"username": user.username})
        if not user_data:
            print(f"{log_prefix} - ERROR - USER_NOT_FOUND")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=apiMsg.USER_NOT_FOUND.format(username=user.username),
            )

        user_id = str(user_data["_id"])

        # Query the files_db to get the uploaded file by user_id and filename
        file_data = await files_db.find_one({"user_id": user_id, "name": filename})
        if not file_data:
            print(f"{log_prefix} - ERROR - FILE_NOT_FOUND - {filename}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=apiMsg.FILE_NOT_FOUND.format(file=filename),
            )

        # Convert the file document to an UploadDoc instance
        upload_doc = UploadDoc(**file_data)

        print(f"{log_prefix} - INFO - FILE_RETRIEVED")
        return upload_doc.details()

    except HTTPException as e:
        raise e  # Re-raise the HTTP exceptions
    except Exception as e:
        print(f"{log_prefix} - ERROR - UNEXPECTED_ERROR - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


async def list_user_files(req: Request, user: UserBase) -> List[UploadDoc]:
    db = req.app.database
    user_db = db[config["USER_DB"]]
    files_db = db[config["FILES_DB"]]

    log_prefix = f"> [LOG]\t{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - GET_UPLOADED_FILES - {user.username}"

    try:
        # Retrieve the user's _id from the user_db
        user_data = await user_db.find_one({"username": user.username})
        if not user_data:
            print(f"{log_prefix} - ERROR - USER_NOT_FOUND")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=apiMsg.USER_NOT_FOUND.format(username=user.username),
            )

        user_id = str(user_data["_id"])

        # Query the files_db to get the uploaded files by user_id
        uploaded_files_cursor = files_db.find({"user_id": user_id})
        uploaded_files = await uploaded_files_cursor.to_list(length=None)

        # Convert each file document to an UploadDoc instance
        uploaded_files_list = [UploadDoc(**file) for file in uploaded_files]
        # Convert each UploadDoc instance to its .dict() format
        uploaded_files_list = [doc.details() for doc in uploaded_files_list]

        print(f"{log_prefix} - INFO - FILES_RETRIEVED")
        return uploaded_files_list

    except HTTPException as e:
        raise e  # Re-raise the HTTP exceptions
    except Exception as e:
        print(f"{log_prefix} - ERROR - UNEXPECTED_ERROR - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


async def upload_file(req: Request, file: UploadFile, user: UserBase):
    db = req.app.database
    user_db = db[config["USER_DB"]]
    files_db = db[config["FILES_DB"]]

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
            
        # Fetch user document from MongoDB to get user ID
        user_doc = await user_db.find_one({"username": user.username})

        if not user_doc:
            print(f"{log_prefix} - ERROR - USER_NOT_FOUND - {user.username}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=apiMsg.USER_NOT_FOUND.format(username=user.username),
            )

        user_id = str(user_doc["_id"])  # Assuming MongoDB ObjectId as user_id

        # Create an instance of UploadDoc for the uploaded file
        uploaded_file_info = UploadDoc(
            user_id=user_id,
            name=file.filename,
            file_uid=uid,
            uploaded_at=datetime.now(),
        )

        # Insert the uploaded file information into MongoDB
        insert_result = await files_db.insert_one(uploaded_file_info.dict())

        if not insert_result.inserted_id:
            print(f"{log_prefix} - ERROR - UPLOAD_DOC_INSERT_FAIL - {file.filename}")
            raise ValueError(
                apiMsg.UPLOAD_DOC_INSERT_FAIL.format(file=file.filename)
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


async def delete_file(req: Request, user: UserBase, filename):
    db = req.app.database
    user_db = db[config["USER_DB"]]
    files_db = db[config["FILES_DB"]]

    # Generate the unique identifier for the file using the user's username and filename
    uid = gen_uid(user.username, filename)
    log_prefix = (
        f"> [LOG]\t{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - DELETE_FILE - {uid}"
    )

    try:
        # Retrieve the user's ID from the database
        user_data = await user_db.find_one({"username": user.username}, {"_id": 1})
        if not user_data:
            print(f"{log_prefix} - ERROR - USER_NOT_FOUND_DB - {user.username}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=apiMsg.USER_NOT_FOUND_DB.format(user=user.username),
            )
        
        user_id = str(user_data["_id"])  # Convert ObjectId to str if needed
        
        # Retrieve the file document from files_db based on user_id and file_uid
        file_doc = await files_db.find_one({"user_id": user_id, "file_uid": uid})
        if not file_doc:
            print(f"{log_prefix} - ERROR - FILE_NOT_FOUND_DB - {filename}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=apiMsg.FILE_NOT_FOUND_DB.format(file=filename),
            )
        
        # Remove the file from files_db
        delete_result = await files_db.delete_one({"user_id": user_id, "file_uid": uid})
        if delete_result.deleted_count == 0:
            print(f"{log_prefix} - ERROR - FILE_DELETE_FAIL_DB - {filename}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=apiMsg.FILE_DELETE_FAIL_DB.format(file=filename),
            )
            
    
        # Construct the file path
        file_path = find_file_by_uid(config["UPLOAD_PATH"], uid)

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


async def get_tokens(req: Request, user: UserBase, filename):
    user_db = req.app.database[config["USER_DB"]]
    files_db = req.app.database[config["FILES_DB"]]
    
    uid = gen_uid(user.username, filename)
    log_prefix = (
        f"> [LOG]\t{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - GET_TOKENS - {uid}"
    )


    try:
        # Retrieve the user's _id from the user_db
        user_data = await user_db.find_one({"username": user.username})
        if not user_data:
            print(f"{log_prefix} - ERROR - USER_NOT_FOUND")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=apiMsg.USER_NOT_FOUND.format(username=user.username),
            )

        user_id = str(user_data["_id"])

        # Query the files_db to find the document by user_id and filename
        doc_data = await files_db.find_one({"user_id": user_id, "name": filename})
        if not doc_data:
            print(f"{log_prefix} - ERROR - FILE_NOT_FOUND_DB - {filename}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=apiMsg.FILE_NOT_FOUND_DB.format(file=filename),
            )
            
        doc_data["oid"] = str(doc_data["_id"])
        doc_data = UploadDoc(**doc_data)

        # Check if the document is tokenized
        if not doc_data.tokens:
            print(f"{log_prefix} - ERROR - NOT_TOKENIZED - {filename}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=apiMsg.NOT_TOKENIZED.format(file=filename),
            )

        # doc_tokens = DocTokens(**doc_data.tokens)
        
        print(f"{log_prefix} - INFO - TOKEN_GET_SUCCESS")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": apiMsg.TOKEN_GET_SUCCESS.format(tokens_id=filename),
                "data": doc_data.tokens.dict(),
            },
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
        
        
async def get_tscc(req: Request, user: UserBase, filename):
    user_db = req.app.database[config["USER_DB"]]
    files_db = req.app.database[config["FILES_DB"]]
    
    uid = gen_uid(user.username, filename)
    log_prefix = (
        f"> [LOG]\t{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - GET_TOKENS - {uid}"
    )


    try:
        # Retrieve the user's _id from the user_db
        user_data = await user_db.find_one({"username": user.username})
        if not user_data:
            print(f"{log_prefix} - ERROR - USER_NOT_FOUND")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=apiMsg.USER_NOT_FOUND.format(username=user.username),
            )

        user_id = str(user_data["_id"])

        # Query the files_db to find the document by user_id and filename
        doc_data = await files_db.find_one({"user_id": user_id, "name": filename})
        if not doc_data:
            print(f"{log_prefix} - ERROR - FILE_NOT_FOUND_DB - {filename}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=apiMsg.FILE_NOT_FOUND_DB.format(file=filename),
            )
            
        doc_data["oid"] = str(doc_data["_id"])
        doc_data = UploadDoc(**doc_data)

        # Check if the document is tokenized
        if not doc_data.tokens:
            print(f"{log_prefix} - ERROR - NOT_TOKENIZED - {filename}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=apiMsg.NOT_TOKENIZED.format(file=filename),
            )
        
        if not doc_data.tscc:
            print(f"{log_prefix} - ERROR - NOT_TSCC_PROCESSED - {filename}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=apiMsg.NOT_TSCC_PROCESSED.format(file=filename),
            )

        # tscc = TSCC(**doc_data.tscc)
        
        print(f"{log_prefix} - INFO - TOKEN_GET_SUCCESS")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": apiMsg.TOKEN_GET_SUCCESS.format(tokens_id=filename),
                "data": doc_data.tscc.dict(),
            },
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
    req: Request, user: UserBase, filename, pdf_loader, overwrite: bool
):
    db = req.app.database
    user_db = db[config["USER_DB"]]
    files_db = db[config["FILES_DB"]]

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
            
            
         # Retrieve the user's ID from the database
        user_data = await user_db.find_one({"username": user.username}, {"_id": 1})
        if not user_data:
            print(f"{log_prefix} - ERROR - USER_NOT_FOUND_DB - {user.username}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=apiMsg.USER_NOT_FOUND_DB.format(user=user.username),
            )
        
        user_id = str(user_data["_id"])  # Convert ObjectId to str if needed

        # Retrieve the file document from files_db based on user_id and file_uid
        doc_data = await files_db.find_one({"user_id": user_id, "file_uid": uid})
        if not doc_data:
            print(f"{log_prefix} - ERROR - FILE_NOT_FOUND_DB - {filename}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=apiMsg.FILE_NOT_FOUND_DB.format(file=filename),
            )
            
        doc_data["oid"] = str(doc_data["_id"])
        doc_data = UploadDoc(**doc_data)

        # Check if the document is already tokenized and not set to overwrite
        if doc_data.tokenized and not overwrite:
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
        doc_data.tokens = doc_tokens
        doc_data.tokenized = True
        
        vec_db_path = setup_db(uid, pre_text_chunks)
        doc_data.vec_db_path = str(vec_db_path)
        doc_data.embedded = True
        
        update_result = await files_db.update_one(
            {"_id": ObjectId(doc_data.oid)},
            {"$set": doc_data.dict()}
        )
        if update_result.modified_count == 0:
            print(f"{log_prefix} - ERROR - TOKENS_UPDATE_FAIL")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=apiMsg.TOKENS_UPDATE_FAIL.format(file=filename),
            )
        
        print(f"{log_prefix} - INFO - TOKENIZATION_SUCCESS")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": apiMsg.TOKENIZE_SUCCESS.format(file=filename),
                "data": doc_tokens.details(),
            },
        )

    except HTTPException as e:
        raise e  # Re-raise the HTTP exceptions
    except Exception as e:
        print(f"{log_prefix} - ERROR - UNEXPECTED_ERROR - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
       

async def query_rag(req: Request, user: UserBase, filename, query):
    files_db = req.app.database[config["FILES_DB"]]
    log_prefix = f"> [LOG]\t{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - QUERY_RAG - {filename}"

    try:
        # Retrieve the user's _id from the user_db
        user_data = await req.app.database[config["USER_DB"]].find_one({"username": user.username})
        if not user_data:
            print(f"{log_prefix} - ERROR - USER_NOT_FOUND")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=apiMsg.USER_NOT_FOUND.format(username=user.username),
            )

        user_id = str(user_data["_id"])

        # Query the files_db to find the document by user_id and filename
        doc_data = await files_db.find_one({"user_id": user_id, "name": filename})
        if not doc_data:
            print(f"{log_prefix} - ERROR - FILE_NOT_FOUND - {filename}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=apiMsg.FILE_NOT_FOUND.format(file=filename),
            )
        doc_data["oid"] = str(doc_data["_id"])
        doc_data = UploadDoc(**doc_data)

        # Check if the document is tokenized
        if not doc_data.tokenized:
            print(f"{log_prefix} - ERROR - FILE_NOT_YET_TOKENIZED")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=apiMsg.FILE_NOT_YET_TOKENIZED.format(file=filename),
            )

        # Check if the document is embedded
        if not doc_data.embedded:
            print(f"{log_prefix} - ERROR - FILE_NOT_YET_EMBEDDED")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=apiMsg.FILE_NOT_YET_EMBEDDED.format(file=filename),
            )

        # Check if the vector database path exists
        if not os.path.exists(doc_data.vec_db_path):
            print(f"{log_prefix} - ERROR - FILE_NOT_FOUND_LOCAL")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=apiMsg.FILE_NOT_FOUND_LOCAL.format(file=doc_data.vec_db_path),
            )

        # Set up the QA chain using the vector database path
        response = await qa_chain_async(str(query), doc_data.vec_db_path)

        # Return the query response
        print(f"{log_prefix} - INFO - QUERY_SUCCESS")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": apiMsg.RAG_QUERY_SUCCESS,
                "data": {"query": str(query), "response": response["result"]},
            },
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


async def process_tscc(
    background_tasks: BackgroundTasks, req: Request, user: UserBase, filename, llm
):
    log_prefix = f"> [LOG]\t{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - PROCESS_TSCC - {filename}"

    db = req.app.database
    user_db = db[config["USER_DB"]]
    files_db = db[config["FILES_DB"]]

    try:
        # Retrieve the user's _id from the user_db
        user_data = await user_db.find_one({"username": user.username})
        if not user_data:
            print(f"{log_prefix} - ERROR - USER_NOT_FOUND")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=apiMsg.USER_NOT_FOUND.format(username=user.username),
            )

        user_id = str(user_data["_id"])
        
        # Query the files_db to find the document by user_id and filename
        doc_data = await files_db.find_one({"user_id": user_id, "name": filename})
        if not doc_data:
            print(f"{log_prefix} - ERROR - FILE_NOT_FOUND - {filename}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=apiMsg.FILE_NOT_FOUND.format(file=filename),
            )
    
        doc_data["oid"] = str(doc_data["_id"])
        doc_data = UploadDoc(**doc_data)

        # Check if the document is tokenized
        if not doc_data.tokenized:
            print(f"{log_prefix} - ERROR - FILE_NOT_YET_TOKENIZED")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=apiMsg.NOT_TOKENIZED.format(file=doc_data.name),
            )
            
        # Check if the document is already processed
        if doc_data.processed:
            print(f"{log_prefix} - ERROR - TSCC_ALREADY_PROCESSED")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=apiMsg.TSCC_ALREADY_PROCESSED.format(file=doc_data.name),
            )


        # Add the long-running process to background tasks
        doc_data.process_status = ProcessStatus(
            code=status.HTTP_202_ACCEPTED,
            message=apiMsg.TSCC_PROCESSING_BACKGROUND.format(file=doc_data.name),
        )
        
        await update_doc_status(files_db, doc_data)
        
        background_tasks.add_task(
            process_tscc_background,
            files_db,
            doc_data,
            llm,
            log_prefix,
        )

        # Return immediate response indicating background processing
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content={
                "message": apiMsg.TSCC_PROCESSING_BACKGROUND.format(
                    file=doc_data.name
                ),
            },
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


async def process_tscc_background(
    files_db, doc_data: UploadDoc, llm, log_prefix
):
    try:
        try:
            # Generate TSCC for the doc_tokens
            print(f"{log_prefix} - INFO - START_TSCC")
            tscc = await generate_tscc(files_db, doc_data, llm)
        except Exception as e:
            print(f"{log_prefix} - ERROR - TSCC_PROCESS_FAIL - {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=apiMsg.TSCC_PROCESS_FAIL.format(
                    file=doc_data.name, error=str(e)
                ),
            )
        
        doc_data.tscc = tscc
        doc_data.processed = True
        
        update_result = await files_db.update_one(
            {"_id": ObjectId(doc_data.oid)},
            {"$set": doc_data.dict()}
        )
        if update_result.modified_count == 0:
            print(f"{log_prefix} - ERROR - TSCC_DB_INSERT_FAIL")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=apiMsg.TSCC_DB_INSERT_FAIL.format(file=doc_data.name),
            )
        # Add the long-running process to background tasks
        doc_data.process_status = ProcessStatus(
            code=status.HTTP_202_ACCEPTED,
            message=apiMsg.TSCC_PROCESS_SUCCESS.format(file=doc_data.name),
        )
        await update_doc_status(files_db, doc_data)
        # Log success message
        print(f"{log_prefix} - INFO - TSCC_PROCESS_SUCCESS")
    except HTTPException as e:
        doc_data.process_status = ProcessStatus(code=e.status_code, message=str(e.detail))
        await update_doc_status(files_db, doc_data)
        raise e  # Re-raise the HTTP exceptions
    except Exception as e:
        doc_data.process_status = ProcessStatus(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR, message=str(e)
        )
        await update_doc_status(files_db, doc_data)
        print(f"{log_prefix} - ERROR - UNEXPECTED_ERROR - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    finally:
        if doc_data.process_status.code != status.HTTP_200_OK:
            await update_doc_status(files_db, doc_data)


async def delete_tokens(req: Request, user: UserBase, filename):
    log_prefix = f"> [LOG]\t{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - DELETE_TOKENS - {filename}"

    db = req.app.database
    user_db = db[config["USER_DB"]]
    files_db = db[config["FILES_DB"]]

    try:
        # Retrieve the user's _id from the user_db
        user_data = await user_db.find_one({"username": user.username})
        if not user_data:
            print(f"{log_prefix} - ERROR - USER_NOT_FOUND")
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"message": apiMsg.USER_NOT_FOUND.format(username=user.username)},
            )

        user_id = str(user_data["_id"])

        # Query the files_db to find the document by user_id and filename
        doc_data = await files_db.find_one({"user_id": user_id, "name": filename})
        if not doc_data:
            print(f"{log_prefix} - ERROR - FILE_NOT_FOUND - {filename}")
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"message": apiMsg.FILE_NOT_FOUND.format(file=filename)},
            )
        doc_data["oid"] = str(doc_data["_id"])
        doc_data = UploadDoc(**doc_data)

        # Check if the document is tokenized
        if not doc_data.tokenized:
            print(f"{log_prefix} - ERROR - NOT_TOKENIZED")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": apiMsg.NOT_TOKENIZED.format(file=filename)},
            )

        # Delete the tokens from the document in the database
        delete_result = await files_db.update_one(
            {"user_id": user_id, "name": filename},
            {"$unset": {"tokens": "", "vec_db_path": ""}, "$set": {"embedded": False}}
        )
        if delete_result.modified_count == 0:
            raise ValueError(
                apiMsg.TOKENS_DELETE_FAIL.format(tokens_id=doc_data.oid)
            )
        
        # Return success response
        print(f"{log_prefix} - INFO - TOKENS_DELETE_SUCCESS")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": apiMsg.TOKENS_DELETE_SUCCESS.format(file=filename)
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
        print(f"{log_prefix} - ERROR - UNEXPECTED_ERROR - {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": str(e)},
        )
        
async def delete_tscc(req: Request, user: UserBase, filename):
    log_prefix = f"> [LOG]\t{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - DELETE_TOKENS - {filename}"

    db = req.app.database
    user_db = db[config["USER_DB"]]
    files_db = db[config["FILES_DB"]]

    try:
        # Retrieve the user's _id from the user_db
        user_data = await user_db.find_one({"username": user.username})
        if not user_data:
            print(f"{log_prefix} - ERROR - USER_NOT_FOUND")
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"message": apiMsg.USER_NOT_FOUND.format(username=user.username)},
            )

        user_id = str(user_data["_id"])

        # Query the files_db to find the document by user_id and filename
        doc_data = await files_db.find_one({"user_id": user_id, "name": filename})
        if not doc_data:
            print(f"{log_prefix} - ERROR - FILE_NOT_FOUND - {filename}")
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"message": apiMsg.FILE_NOT_FOUND.format(file=filename)},
            )
        doc_data["oid"] = str(doc_data["_id"])
        doc_data = UploadDoc(**doc_data)
        
        # Check if the document is tokenized
        if not doc_data.processed:
            print(f"{log_prefix} - ERROR - NOT_TSCC_TOKENIZED")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": apiMsg.NOT_TSCC_PROCESSED.format(file=filename)},
            )

        # Delete the tokens from the document in the database
        delete_result = await files_db.update_one(
            {"user_id": user_id, "name": filename},
            {"$unset": {"tscc": ""}, "$set": {"processed": False}}
        )
        if delete_result.modified_count == 0:
            raise ValueError(
                apiMsg.TOKENS_DELETE_FAIL.format(tokens_id=doc_data.oid)
            )
        
        # Return success response
        print(f"{log_prefix} - INFO - TOKENS_DELETE_SUCCESS")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": apiMsg.TOKENS_DELETE_SUCCESS.format(file=filename)
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
        print(f"{log_prefix} - ERROR - UNEXPECTED_ERROR - {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": str(e)},
        )


async def delete_tscc_old(req: Request, user: UserBase, filename):
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
