from fastapi import Request, status
from fastapi.responses import JSONResponse

from middleware.api_msg import APIMessages


def get_all_users(req: Request):
    users = list(req.app.database["users"].find(limit=100))

    if not users:
        return JSONResponse(content={"message": APIMessages.PROFILE_NOT_FOUND}, status_code=status.HTTP_404_NOT_FOUND)

    return users
