from fastapi import APIRouter, Body, Request, Response, status
from fastapi.responses import JSONResponse
from typing import List

router = APIRouter()

from models.user import User
from middleware.api_msg import APIMessages as api


@router.get("/users", response_description="Get all users", response_class=List[User])
def get_all_users_route(request: Request):
    users = list(request.app.database["users"].find(limit=100))

    if not users:
        return JSONResponse(content={"message": api.PROFILE_NOT_FOUND}, status_code=status.HTTP_404_NOT_FOUND)

    return users
