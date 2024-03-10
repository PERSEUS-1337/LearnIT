from fastapi import APIRouter, Depends, Body, status, Request
from fastapi.security import OAuth2PasswordRequestForm

from controllers.authController import login_for_access_token, create_user
from models.user import UserReg

router = APIRouter()


@router.post("/token", response_description="For logging in a user and obtaining a token")
async def login_route(req: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    return await login_for_access_token(req, form_data)


@router.post("/register", response_description="Register a user", status_code=status.HTTP_201_CREATED)
def register_route(req: Request, user: UserReg = Body(...)):
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
