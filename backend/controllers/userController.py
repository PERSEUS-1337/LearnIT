from dotenv import dotenv_values
from datetime import datetime, timedelta
from typing import Annotated
from fastapi import Depends, HTTPException, status, Request, Body
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from middleware.apiMsg import APIMessages
from utils.authUtils import (
    verify_password,
    get_password_hash,
    get_user_creds,
    create_access_token,
)
from models.user import UserBase, Token, UserInDB, UserReg


config = dotenv_values(".env")


async def login_user(
    req: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    remember_me=None,
) -> Token:
    log_prefix = f"> [LOG]\t{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - LOGIN_USER - {form_data.username}"

    try:
        db = req.app.database[config["USER_DB"]]
        user = await get_user_creds(db, form_data.username)
        if not user:
            print(f"{log_prefix} - ERROR - USER_NOT_FOUND")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=APIMessages.USER_NOT_FOUND,
                headers={"WWW-Authenticate": "Bearer"},
            )

        match_pass = verify_password(form_data.password, user.hashed_password)
        if not match_pass:
            print(f"{log_prefix} - ERROR - INCORRECT_PASSWORD")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=APIMessages.INCORRECT_PASSWORD,
                headers={"WWW-Authenticate": "Bearer"},
            )

        if remember_me:
            access_token_expires = timedelta(days=10)  # Override to 3 days
        else:
            access_token_expires = timedelta(
                minutes=int(config["ACCESS_TOKEN_EXPIRE_MINUTES"])
            )

        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        print(f"{log_prefix} - INFO - LOGIN_SUCCESS")
        return Token(access_token=access_token, token_type="bearer")

    except HTTPException as he:
        # Re-raise if it already has a status code
        print(f"{log_prefix} - ERROR - HTTP_EXCEPTION - {str(he)}")
        raise he

    except Exception as e:
        # Print the error
        print(f"{log_prefix} - ERROR - UNEXPECTED_ERROR - {str(e)}")
        # Handle exceptions here and return a proper status code and detail message
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        )


async def register_user(
    req: Request, username: str, full_name: str, email: str, password: str
):
    log_prefix = f"> [LOG]\t{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - REGISTER_USER - {username}"

    try:
        db = req.app.database[config["USER_DB"]]
        user_exists = await get_user_creds(db, username)
        if user_exists:
            print(f"{log_prefix} - ERROR - USER_ALREADY_EXISTS")
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                headers={"WWW-Authenticate": "Bearer"},
                content={"message": APIMessages.USER_ALREADY_EXISTS},
            )

        hashed_pass = get_password_hash(password)

        new_user_data = UserInDB(
            username=username,
            email=email,
            full_name=full_name,
            hashed_password=hashed_pass,
        )

        insert_result = await db.insert_one(new_user_data.dict())

        if not insert_result.inserted_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to insert user into the database.",
            )

        # Convert UserInDB to UserBase
        user_base_data = UserBase(
            username=new_user_data.username,
            email=new_user_data.email,
            full_name=new_user_data.full_name,
        )
        print(f"{log_prefix} - INFO - USER_REGISTERED")
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "message": APIMessages.USER_CREATED,
                "data": user_base_data.dict(),
            },
        )

    except HTTPException as he:
        # Re-raise HTTPException with additional logging
        print(
            f"{log_prefix} - ERROR - HTTP_EXCEPTION - {str(he.detail)} (status code: {he.status_code})"
        )
        raise he

    except Exception as e:
        # Log the detailed error and re-raise with a generic message
        print(f"{log_prefix} - ERROR - UNEXPECTED_ERROR - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during user registration. Please try again later.",
        )


async def delete_user(req: Request, user: UserBase):
    log_prefix = f"> [LOG]\t{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - DELETE_USER - {user.username}"

    try:
        # Find the user in the database by username
        db = req.app.database[config["USER_DB"]]

        # If user is found, delete the user from the database
        delete_result = await db.delete_one({"username": user.username})

        if delete_result.deleted_count == 0:
            print(f"{log_prefix} - ERROR - USER_NOT_FOUND")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        print(f"{log_prefix} - INFO - USER_DELETED")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": APIMessages.USER_DELETED,
                "data": user.model_dump(),
            },
        )
    except HTTPException as e:
        # Re-raise HTTPExceptions if necessary
        print(f"{log_prefix} - ERROR - HTTP_EXCEPTION - {str(e)}")
        raise e

    except Exception as e:
        # Handle any unexpected errors
        print(f"{log_prefix} - ERROR - UNEXPECTED_ERROR - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal Server Error", "data": str(e)},
        )
