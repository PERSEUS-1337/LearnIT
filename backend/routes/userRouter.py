from fastapi import APIRouter, Body, Request, Depends, status
from fastapi.responses import JSONResponse

from middleware.apiMsg import APIMessages
from controllers.documentController import get_file_details, list_user_files
from controllers.userController import (
    delete_user,
)
from middleware.requireAuth import auth_curr_user
from models.user import UserBase

import utils.responses as responses

router = APIRouter()


@router.get(
    "/hello",
    response_description="To test if the route is alive and working well",
    status_code=status.HTTP_200_OK,
)
def hello():
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": APIMessages.DOC_ROUTE_SUCCESS},
    )


@router.get(
    "/me",
    response_description="Get current logged in user details",
    responses=responses.get_curr_user_responses,
)
async def get_curr_user_route(
    req: Request, current_user: UserBase = Depends(auth_curr_user)
):
    return current_user


@router.delete("/me", response_description="Delete user")
async def delete_user_route(
    req: Request,
    current_user: UserBase = Depends(auth_curr_user),
):
    return await delete_user(req, current_user)


@router.get(
    "/file",
    response_description="Get file details",
    responses=responses.get_file_responses,
)
async def get_file_details_route(
    req: Request, filename: str, user: UserBase = Depends(auth_curr_user)
):
    return await get_file_details(req, user, filename)


@router.get(
    "/file/list",
    response_description="List user files",
    responses=responses.list_user_files_responses,
)
async def list_user_files_route(req: Request, user: UserBase = Depends(auth_curr_user)):
    return await list_user_files(req, user)
