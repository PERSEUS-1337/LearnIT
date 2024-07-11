from typing import Annotated

from fastapi import (
    APIRouter,
    Request,
    Depends,
    UploadFile,
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
    get_tokens,
    get_tscc,
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
def get_uploaded_files_route(req: Request):
    return get_uploaded_files()


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


@router.get("/get-tokens")
async def get_tokens_route(
    req: Request, filename: str, user: UserBase = Depends(auth_curr_user)
):
    return await get_tokens(req, user, filename)


@router.get("/get-tscc")
async def get_tscc_route(
    req: Request, filename: str, user: UserBase = Depends(auth_curr_user)
):
    return await get_tscc(req, user, filename)


@router.post("/gen-tokens")
async def generate_tokens_route(
    req: Request,
    filename: str,
    pdf_loader: str,
    overwrite: bool,
    user: UserBase = Depends(auth_curr_user),
):
    # background_tasks = req.app.state.background_tasks
    # background_tasks.add_task(
    #     generate_tokens, req, user, filename, pdf_loader, overwrite
    # )
    # return JSONResponse(
    #     status_code=202,
    #     content={"message": "Processing started in the background."},
    # )
    return await generate_tokens(req, user, filename, pdf_loader, overwrite)


@router.post("/process-tscc")
async def process_tscc_route(
    req: Request,
    filename: str,
    user: UserBase = Depends(auth_curr_user),
):
    # Now you can use background_tasks to add tasks
    # background_tasks.add_task(process_tscc, req, user, filename)
    # return JSONResponse(
    #     status_code=202,
    #     content={"message": "Processing started in the background."},
    # )
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
