from fastapi import APIRouter, Body, Request, Response, status
from fastapi.responses import JSONResponse
from typing import List

router = APIRouter()

from models.user import User
from middleware.api_msg import APIMessages

@router.get("/all", response_description="Get all users", response_class=List[User], tags=["users"])
async def get_all_users():
    # Your get all users logic here
    pass

@router.get("/me", response_description="Get current logged in user details", response_class=List[User], tags=["user"])
async def get_current_user():
    # Your logic to get current user details here
    pass


