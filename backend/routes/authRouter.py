from fastapi import APIRouter, Body, Request, Response, status
from fastapi.responses import JSONResponse
from typing import List

router = APIRouter()

from models.user import User
from middleware.api_msg import APIMessages

import controllers.userController as user_api


@router.get("/all", response_description="Get all users", response_class=List[User], tags=["users"])
async def get_all_users(req: Request):
    # Your get all users logic here
    # pass
    return user_api.get_all_users(req)

@router.post("/register", response_description="Register a user", response_class=List[User], tags=["authentication"])
async def register_user():
    # Your registration logic here
    pass

@router.post("/login", response_description="Login user", response_class=List[User], tags=["authentication"])
async def login_user():
    # Your login logic here
    pass

@router.post("/logout", response_description="Logout user", response_class=List[User], tags=["authentication"])
async def logout_user():
    # Your logout logic here
    pass

