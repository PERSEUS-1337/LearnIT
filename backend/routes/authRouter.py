from typing import Annotated

from fastapi import APIRouter, Depends, Response, Body, status, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm

from controllers.authController import login_for_access_token, create_user
from middleware.requireAuth import auth_curr_user
from models.user import User, RegisterForm, UserInDB

router = APIRouter()


@router.post("/token", response_description="For logging in a user and obtaining a token")
async def login_route(form_data: OAuth2PasswordRequestForm = Depends()):
    return await login_for_access_token(form_data)


# @router.get("/me", response_model=User)
# async def read_users_me(
#         current_user: Annotated[User, Depends(auth_curr_user)]
# ):
#     return current_user
#
#
# @router.get("/me/items")
# async def read_own_items(
#         current_user: Annotated[User, Depends(auth_curr_user)]
# ):
#     return [{"item_id": "Foo", "owner": current_user.username}]

@router.post("/register", response_description="Register a user", status_code=status.HTTP_201_CREATED, response_model=UserInDB)
def register_route(req: Request, user: RegisterForm = Body(...)):
    # Your registration logic here
    return create_user(req, user)

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
