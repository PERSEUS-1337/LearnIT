from typing import Annotated

from fastapi import (
    APIRouter,
    Body,
    Form,
    Request,
    Depends,
    FastAPI,
    UploadFile,
    File,
    status,
)
from fastapi.responses import JSONResponse
from middleware.requireAuth import auth_curr_user
from models.user import UserBase
from middleware.apiMsg import APIMessages
from controllers.documentController import (
    delete_tokens,
    get_uploaded_files,
    query_rag,
    process_tscc,
    upload_file,
    delete_file,
    generate_tokens,
    delete_tscc,
)

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


@router.get("/list", response_description="Get a list of uploaded files")
async def get_uploaded_files_route(req: Request):
    return await get_uploaded_files()


@router.post("/upload")
async def upload_file_route(
    req: Request, file: UploadFile, user: UserBase = Depends(auth_curr_user)
):
    return await upload_file(req, file, user)


@router.delete("/")
async def delete_file_route(
    req: Request, filename: str, user: UserBase = Depends(auth_curr_user)
):
    return await delete_file(req, user, filename)


@router.post("/gen-tokens")
async def generate_tokens_route(
    req: Request, filename: str, user: UserBase = Depends(auth_curr_user)
):
    return await generate_tokens(req, user, filename)


@router.post("/process-tscc")
async def process_tscc_route(
    req: Request, filename: str, user: UserBase = Depends(auth_curr_user)
):
    return await process_tscc(req, user, filename)


@router.post("/query-rag")
async def query_rag_route(
    req: Request, filename: str, query: str, user: UserBase = Depends(auth_curr_user)
):
    return await query_rag(req, user, filename, query)


@router.delete("/delete-tokens")
async def delete_tokens_route(
    req: Request, filename: str, user: UserBase = Depends(auth_curr_user)
):
    return await delete_tokens(req, user, filename)


@router.delete("/delete-tscc")
async def delete_tscc_route(
    req: Request, filename: str, user: UserBase = Depends(auth_curr_user)
):
    return await delete_tscc(req, user, filename)
