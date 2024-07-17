from typing import Annotated, Optional
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Form,
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
    generate_and_process_tscc,
    query_rag,
    process_tscc,
    upload_file,
    delete_file,
    generate_tokens,
    delete_tscc,
    get_tokens,
    get_tscc,
)

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
    "/get-tokens",
    response_description="Get tokens of a document",
    responses=responses.get_tokens_responses,
)
async def get_tokens_route(
    req: Request, filename: str, user: UserBase = Depends(auth_curr_user)
):
    return await get_tokens(req, user, filename)


@router.get(
    "/get-tscc",
    response_description="Get TSCC data of a document",
    responses=responses.get_tscc_responses,
)
async def get_tscc_route(
    req: Request, filename: str, user: UserBase = Depends(auth_curr_user)
):
    return await get_tscc(req, user, filename)

@router.get(
    "/query-rag",
    response_description="Query using RAG model",
    responses=responses.query_rag_responses,
)
async def query_rag_route(
    req: Request,
    filename: str,
    query: str,
    user: UserBase = Depends(auth_curr_user),
):
    return await query_rag(req, user, filename, query)


@router.post(
    "/upload",
    response_description="Upload a file",
    responses=responses.upload_file_responses,
)
async def upload_file_route(
    req: Request, file: UploadFile, user: UserBase = Depends(auth_curr_user)
):
    return await upload_file(req, file, user)


@router.post(
    "/gen-tokens",
    response_description="Generate tokens for a file",
    responses=responses.generate_tokens_responses,
)
async def generate_tokens_route(
    req: Request,
    filename: str = Form(...),
    pdf_loader: Optional[str] = Form(None),
    overwrite: Optional[bool] = Form(None),
    user: UserBase = Depends(auth_curr_user),
):
    return await generate_tokens(req, user, filename, pdf_loader, overwrite)


@router.post(
    "/process-tscc",
    response_description="Process TSCC for a file",
    responses=responses.process_tscc_responses,
)
async def process_tscc_route(
    background_tasks: BackgroundTasks,
    req: Request,
    filename: str = Form(...),
    llm: Optional[str] = Form(None),
    user: UserBase = Depends(auth_curr_user),
):

    return await process_tscc(background_tasks, req, user, filename, llm)

@router.post(
    "/gen-proc-tscc",
    response_description="Generate tokens and process TSCC for a file",
    responses=responses.process_tscc_responses,
)
async def generate_and_process_tscc_route(
    background_tasks: BackgroundTasks,
    req: Request,
    filename: str = Form(...),
    pdf_loader: Optional[str] = Form(None),
    llm: Optional[str] = Form(None),
    overwrite: Optional[bool] = Form(None),
    user: UserBase = Depends(auth_curr_user),
):
    return await generate_and_process_tscc(background_tasks, req, user, filename, pdf_loader, llm, overwrite)


@router.delete(
    "/", response_description="Delete a file", responses=responses.delete_file_responses
)
async def delete_file_route(
    req: Request, filename: str, user: UserBase = Depends(auth_curr_user)
):
    return await delete_file(req, user, filename)


@router.delete(
    "/delete-tokens",
    response_description="Delete tokens from a document",
    responses=responses.delete_tokens_responses,
)
async def delete_tokens_route(
    req: Request, filename: str, user: UserBase = Depends(auth_curr_user)
):
    return await delete_tokens(req, user, filename)


@router.delete(
    "/delete-tscc",
    response_description="Delete TSCC from a document",
    responses=responses.delete_tscc_responses,
)
async def delete_tscc_route(
    req: Request, filename: str, user: UserBase = Depends(auth_curr_user)
):
    return await delete_tscc(req, user, filename)
