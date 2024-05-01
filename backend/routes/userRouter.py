from typing import Annotated

from fastapi import APIRouter, Body, Request, Depends

from controllers.userController import (
    delete_user,
    get_all_users,
    update_user,
)
from middleware.requireAuth import auth_curr_user
from models.user import UserBase, UserUpdate

router = APIRouter()


@router.get("/list", response_description="Get all users")
async def get_all_users_route(
    req: Request, current_user: UserBase = Depends(auth_curr_user)
):
    return await get_all_users(req)


@router.get("/", response_description="Get current logged in user details")
async def get_curr_user_route(
    req: Request, current_user: UserBase = Depends(auth_curr_user)
):
    return current_user


@router.patch("/", response_description="Edit user details")
async def edit_user_route(
    req: Request,
    updated_details: UserUpdate = Body(...),
    current_user: UserBase = Depends(auth_curr_user),
):
    return await update_user(req, current_user, updated_details)


@router.delete("/", response_description="Delete user")
async def edit_user_route(
    req: Request,
    current_user: UserBase = Depends(auth_curr_user),
):
    return await delete_user(req, current_user)
