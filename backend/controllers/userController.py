from dotenv import dotenv_values
from fastapi import Depends, HTTPException, status, Request, Body
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from middleware.apiMsg import APIMessages
from models.user import UserBase, Token, UserInDB, UserReg, UserUpdate
from utils.authUtils import verify_password, get_password_hash, get_user_creds, create_access_token

from datetime import timedelta
from typing import Annotated, Optional


config = dotenv_values(".env")


async def login_user(req: Request, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    try:
        user = get_user_creds(req.app.database["users"], form_data.username)
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
                detail=f"Password is incorrect",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=int(config['ACCESS_TOKEN_EXPIRE_MINUTES']))
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
            detail=f"An unexpected error occurred: {str(e)}"
        )


async def register_user(req: Request, user: UserReg = Body(...)):
    try:
        user_exists = get_user_creds(req.app.database["users"], user.username)
        if user_exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=APIMessages.USER_ALREADY_EXISTS,
                headers={"WWW-Authenticate": "Bearer"},
            )

        hashed_pass = get_password_hash(user.password)
        # time_now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        new_user_data = UserInDB(username=user.username, email=user.email,
                                 full_name=user.full_name, hashed_password=hashed_pass)

        new_user_data = new_user_data.dict()
        insert_result = req.app.database["users"].insert_one(new_user_data)

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": APIMessages.USER_CREATED}
        )

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
            detail=f"An unexpected error occurred: {str(e)}"
        )


async def get_all_users(req: Request):
    user_list = list(req.app.database["users"].find({}, {'_id': 0, 'hashed_password': 0}))

    if not list:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": APIMessages.USERS_NOT_FOUND}
            )

    return user_list


async def get_user(req: Request, user: UserBase) -> UserBase:
    user_data = req.app.database["users"].find_one({"username": user.username})

    if user_data:
        # If user is found, create a UserBase object using the retrieved data
        return UserBase(**user_data)
    else:
        # If user is not found, return None or handle as needed
        return None

async def update_user(req: Request, user: UserBase, user_update: UserUpdate) -> Optional[UserBase]:
    # Find the user in the database by username
    user_exists = req.app.database["users"].find_one({"username": user.username})

    if user_exists:
        # If user is found, update the user's information
        updated_data = user_exists
        if user_update.email:
            updated_data["email"] = user_update.email
        if user_update.full_name:
            updated_data["full_name"] = user_update.full_name
            
        # Update the user's information in the database
        req.app.database["users"].update_one({"username": user.username}, {"$set": updated_data})
        
        # Fetch the updated user data from the database
        updated_user_data = req.app.database["users"].find_one({"username": user.username})

        # Create a UserBase object using the updated data and return it
        # return UserBase(**updated_user_data)
        return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"message": APIMessages.USER_UPDATED, "data": UserBase(**updated_user_data)}
            )
    else:
        # If user is not found, return None or handle as needed
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": APIMessages.USER_NOT_FOUND}
        )
    
async def delete_user(req: Request, user: UserBase):
    # Find the user in the database by username
    user_data = req.app.database["users"].find_one({"username": user.username})

    if user_data:
        # If user is found, delete the user from the database
        req.app.database["users"].delete_one({"username": user.username})
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": APIMessages.USER_DELETED}
        )
    else:
        # If user is not found, return None or handle as needed
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": APIMessages.USER_NOT_FOUND}
        )