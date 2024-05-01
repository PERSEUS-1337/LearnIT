from typing import Annotated

from fastapi import APIRouter, Body, Request, Depends, FastAPI, UploadFile, File, status
from fastapi.responses import JSONResponse
from middleware.requireAuth import auth_curr_user
from models.user import UserBase
from middleware.apiMsg import APIMessages
from controllers.documentController import get_uploaded_files, upload_file

router = APIRouter()


@router.get(
    "/hello",
    response_description="To test if the route is alive and working well",
    status_code=status.HTTP_200_OK,
)
def hello():
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": APIMessages.DOCU_ROUTE_SUCCESS},
    )


@router.get("/list", response_description="Get a list of uploaded files")
async def get_uploaded_files_route(req: Request):
    return await get_uploaded_files(req)


@router.post("/upload")
async def upload_file_route(
    req: Request,
    file: UploadFile,
    current_user: Annotated[UserBase, Depends(auth_curr_user)],
):
    return await upload_file(req, file, current_user)


# @router.get('')
