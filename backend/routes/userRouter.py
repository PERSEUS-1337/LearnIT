from fastapi import APIRouter, Body, Request, Depends

from controllers.documentController import get_user_files
from controllers.userController import (
    delete_user,
)
from middleware.requireAuth import auth_curr_user
from models.user import UserBase

router = APIRouter()


@router.get("/", response_description="Get current logged in user details")
async def get_curr_user_route(
    req: Request, current_user: UserBase = Depends(auth_curr_user)
):
    return current_user


@router.delete("/", response_description="Delete user")
async def edit_user_route(
    req: Request,
    current_user: UserBase = Depends(auth_curr_user),
):
    return await delete_user(req, current_user)


@router.get("/files")
async def get_user_files_route(
    req: Request, user: UserBase = Depends(auth_curr_user)
):
    return await get_user_files(req, user)
