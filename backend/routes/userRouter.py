from typing import Annotated

from fastapi import APIRouter, Request, Depends

from controllers.userController import get_all_users
from middleware.requireAuth import auth_curr_user
from models.user import User

router = APIRouter()


@router.get("/all", response_description="Get all users")
async def get_all_users_route(req: Request, current_user: Annotated[User, Depends(auth_curr_user)]):
    # Your get all users logic here
    return get_all_users(req)


@router.get("/me", response_description="Get current logged in user details")
async def get_curr_user_route(req: Request, current_user: Annotated[User, Depends(auth_curr_user)]):
    # Your logic to get current user details here
    return current_user
