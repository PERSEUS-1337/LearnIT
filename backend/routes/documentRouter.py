from typing import Annotated

from fastapi import APIRouter, Body, Request, Depends, FastAPI, UploadFile, File, status
from fastapi.responses import JSONResponse
from middleware.apiMsg import APIMessages
from controllers.documentController import upload_file

router = APIRouter()

@router.get("/hello", response_description="To test if the route is alive and working well",
            status_code=status.HTTP_200_OK)
def hello():
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": APIMessages.DOCU_ROUTE_SUCCESS}
    )

@router.post("/upload")
async def upload_file_route(req: Request, file: UploadFile):
    return await upload_file(req, file)