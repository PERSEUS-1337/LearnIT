from datetime import datetime
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
import time
from dotenv import dotenv_values

from models.document import UploadDoc
from middleware.apiMsg import APIMessages
from controllers.documentController import list_user_files
from middleware.requireAuth import auth_curr_user
from models.user import UserBase
from routes.authRouter import router as auth_router
from routes.userRouter import router as user_router
from routes.documentRouter import router as docu_router

config = dotenv_values(".env")

app = FastAPI()


@app.middleware("http")
async def measure_request_time(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time} s"
    return response


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "This is the API route of LearnIT!"}


@app.get("/hello")
async def root():
    return {"message": "Hello World!"}


@app.get("/app", response_description="Get general app dashboard details", responses="")
async def get_app_details_route(req: Request, user: UserBase = Depends(auth_curr_user)):
    # Once user is authorized, retrieve other details such as:
    # User Details
    # User Uploaded Files Stat
    # Tokens Proccessed
    # Tokens Generated
    # Estimated time reading
    log_prefix = f"> [LOG]\t{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - GET_APP_DETAILS - {user.username}"

    db = req.app.database
    user_db = db[config["USER_DB"]]
    files_db = db[config["FILES_DB"]]

    try:
        # Retrieve the user's details from the user_db
        user_data = await user_db.find_one({"username": user.username})
        if not user_data:
            print(f"{log_prefix} - ERROR - USER_NOT_FOUND")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=APIMessages.USER_NOT_FOUND.format(username=user.username),
            )

         # Retrieve the user's uploads from the files_db
        upload_docs = await files_db.find({"user_id": str(user_data["_id"])}).to_list(length=None)
        uploads = [UploadDoc(**upload_doc) for upload_doc in upload_docs]
        total_uploads = len(uploads)

        # Calculate total tokens in doc_tokens and tscc_tokens
        total_doc_tokens = sum(upload.tokens.token_count for upload in uploads if upload.tokens)
        total_tscc_tokens = sum(upload.tscc.token_count for upload in uploads if upload.tscc)

        # Calculate the total number of files processed
        total_files_processed = sum(1 for upload in uploads if upload.tscc)
        
        # Calculate the average token reduction percentage
        reduction_percentages = []
        for upload in uploads:
            if upload.tokens and upload.tscc:
                doc_tokens = upload.tokens.token_count
                tscc_tokens = upload.tscc.token_count
                if doc_tokens > 0:
                    reduction_percentage = ((doc_tokens - tscc_tokens) / doc_tokens) * 100
                    reduction_percentages.append(reduction_percentage)
        
        average_token_reduction_percentage = sum(reduction_percentages) / len(reduction_percentages) if reduction_percentages else 0

        # Calculate the total approximated reading time
        words_per_minute = 250
        total_reading_time_minutes = total_tscc_tokens / words_per_minute


        # Create the response object
        response_data = {
            "user": {
                "username": user_data["username"],
                "email": user_data["email"],
                "full_name": user_data["full_name"],
            },
            "uploads": total_uploads,
            "total_doc_tokens": total_doc_tokens,
            "total_tscc_tokens": total_tscc_tokens,
            "total_files_processed": total_files_processed,
            "average_token_reduction_percentage": average_token_reduction_percentage,
            "total_approximated_reading_time_minutes": total_reading_time_minutes,
        }

        # Return the response
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": APIMessages.APP_DETAILS_SUCCESS, "data": response_data},
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


@app.on_event("startup")
async def startup_db_client():
    try:
        app.mongodb_client = AsyncIOMotorClient(config["MONGO_URI"])
        app.database = app.mongodb_client[config["DB_NAME"]]
        print(f"Connected to the {config['DB_NAME']} database!")
    except Exception as e:
        print(f"Failed to connect to the database: {e}")


@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()
    print("Connection to MongoDB closed.")


app.include_router(auth_router, tags=["auth"], prefix="/auth")
app.include_router(user_router, tags=["user"], prefix="/user")
app.include_router(docu_router, tags=["docu"], prefix="/docu")
