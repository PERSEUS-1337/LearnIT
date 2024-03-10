from fastapi import APIRouter, Depends, Body, status, Request
from fastapi.security import OAuth2PasswordRequestForm

from controllers.authController import login_user, register_user
from models.user import UserReg

router = APIRouter()


@router.post("/login", response_description="Login a user", status_code=status.HTTP_202_ACCEPTED)
async def login_route(req: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    return await login_user(req, form_data)


@router.post("/register", response_description="Register a user", status_code=status.HTTP_201_CREATED)
async def register_route(req: Request, user: UserReg = Body(...)):
    return await register_user(req, user)


# @router.post("/logout", response_description="Logout user", response_class=List[User], tags=["authentication"])
# async def logout_user():
#     # Your logout logic here
#     pass
