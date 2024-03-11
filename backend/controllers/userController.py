from fastapi import Request, status
from fastapi.responses import JSONResponse

from middleware.apiMsg import APIMessages
from models.user import UserBase


async def get_all_users(req: Request):
    user_list = list(req.app.database["users"].find({}, {'_id': 0, 'hashed_password': 0}))

    if not list:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": APIMessages.USERS_NOT_FOUND}
            )

    return user_list


async def get_user(req: Request, user: UserBase) -> UserBase:
    user_data = req.app.database["users"].find_one({"username": user.username})

    if user_data:
        # If user is found, create a UserBase object using the retrieved data
        return UserBase(**user_data)
    else:
        # If user is not found, return None or handle as needed
        return None


# async def edit_user(req: Request):

