from typing import List, Annotated
from fastapi import APIRouter, Body, Request, Response, status, Depends, Form
from fastapi.security import OAuth2PasswordRequestForm

from controllers.authController import get_current_active_user, login_for_access_token
from models.user import User
from middleware.api_msg import APIMessages

import controllers.userController as user_api

router = APIRouter()


@router.get("/all", response_description="Get all users")
async def get_all_users(req: Request):
    # Your get all users logic here
    # pass
    return user_api.get_all_users(req)


@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    return await login_for_access_token(form_data)


@router.get("/me/", response_model=User)
async def read_users_me(
        current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user


@router.get("/me/items/")
async def read_own_items(
        current_user: Annotated[User, Depends(get_current_active_user)]
):
    return [{"item_id": "Foo", "owner": current_user.username}]

# @router.post("/register", response_description="Register a user", response_class=List[User], tags=["authentication"])
# async def register_user():
#     # Your registration logic here
#     pass
#
#
# @router.post("/login", response_description="Login user", response_class=List[User], tags=["authentication"])
# async def login_user():
#     # Your login logic here
#     pass
#
#
# @router.post("/logout", response_description="Logout user", response_class=List[User], tags=["authentication"])
# async def logout_user():
#     # Your logout logic here
#     pass
