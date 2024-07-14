from dotenv import dotenv_values
from datetime import timedelta
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
    remember_me,
) -> Token:
    try:
        db = req.app.database[config["USER_DB"]]
        user = await get_user_creds(db, form_data.username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=APIMessages.USER_NOT_FOUND,
                headers={"WWW-Authenticate": "Bearer"},
            )

        match_pass = verify_password(form_data.password, user.hashed_password)
        if not match_pass:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=APIMessages.INCORRECT_PASSWORD,
                headers={"WWW-Authenticate": "Bearer"},
            )

        if remember_me:
            access_token_expires = timedelta(days=3)  # Override to 3 days
        else:
            access_token_expires = timedelta(
                minutes=int(config["ACCESS_TOKEN_EXPIRE_MINUTES"])
            )

        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return Token(access_token=access_token, token_type="bearer")

    except HTTPException as he:
        # Re-raise if it already has a status code
        print(f"An unexpected error occurred: {str(he)}")
        raise he

    except Exception as e:
        # Print the error
        print(f"An unexpected error occurred: {str(e)}")
        # Handle exceptions here and return a proper status code and detail message
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        )


async def register_user(
    req: Request, username: str, full_name: str, email: str, password: str
):
    try:
        db = req.app.database[config["USER_DB"]]
        user_exists = await get_user_creds(db, username)
        if user_exists:
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

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "message": APIMessages.USER_CREATED,
                "data": user_base_data.dict(),
            },
        )

    except HTTPException as he:
        # Re-raise HTTPException with additional logging
        print(f"HTTP error occurred: {str(he.detail)} (status code: {he.status_code})")
        raise he

    except Exception as e:
        # Log the detailed error and re-raise with a generic message
        print(f"Unexpected error during user registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during user registration. Please try again later.",
        )


async def delete_user(req: Request, user: UserBase):
    try:
        # Find the user in the database by username
        db = req.app.database[config["USER_DB"]]

        # If user is found, delete the user from the database
        result = db.delete_one({"username": user.username})

        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": APIMessages.USER_DELETED,
                "data": user.model_dump(),
            },
        )
    except HTTPException as e:
        # Re-raise HTTPExceptions if necessary
        raise e

    except Exception as e:
        # Handle any unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal Server Error", "data": str(e)},
        )
