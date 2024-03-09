from typing import Annotated
from fastapi import APIRouter, Request, Depends
from fastapi.security import OAuth2PasswordRequestForm

from controllers.authController import login_for_access_token
from controllers.userController import get_all_users
from middleware.requireAuth import auth_curr_user
from models.user import User
from middleware.apiMsg import APIMessages



router = APIRouter()


# @router.get("/all", response_description="Get all users")
# async def get_all_users_route(req: Request, ):
#     # Your get all users logic here
#     # pass
#     return get_all_users(req)


@router.post("/token")
async def login_route(form_data: OAuth2PasswordRequestForm = Depends()):
    return await login_for_access_token(form_data)


@router.get("/me/", response_model=User)
async def read_users_me(
        current_user: Annotated[User, Depends(auth_curr_user)]
):
    return current_user


@router.get("/me/items/")
async def read_own_items(
        current_user: Annotated[User, Depends(auth_curr_user)]
):
    return [{"item_id": "Foo", "owner": current_user.username}]

# @router.post("/register", response_description="Register a user", response_class=List[User], tags=["authentication"])
# async def register_user():
#     # Your registration logic here
#     pass
#
#
# @router.post("/login", response_description="Login user", response_class=List[User], tags=["authentication"])
# async def login_user():
#     # Your login logic here
#     pass
#
#
# @router.post("/logout", response_description="Logout user", response_class=List[User], tags=["authentication"])
# async def logout_user():
#     # Your logout logic here
#     pass
