from fastapi import APIRouter, Depends, Body, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse


from controllers.userController import login_user, register_user
from middleware.apiMsg import APIMessages
from models.user import UserReg, UserUpdate

router = APIRouter()


@router.get(
    "/hello",
    response_description="To test if the route is alive and working well",
    status_code=status.HTTP_200_OK,
)
def hello():
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": APIMessages.AUTH_ROUTE_SUCCESS},
    )


@router.post(
    "/login", response_description="Login a user", status_code=status.HTTP_202_ACCEPTED
)
async def login_route(
    req: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    remember_me=Body(...),
):
    return await login_user(req, form_data, remember_me)


@router.post(
    "/register",
    response_description="Register a user",
    status_code=status.HTTP_201_CREATED,
)
async def register_route(req: Request, user: UserReg = Body(...)):
    return await register_user(req, user)


@router.post(
    "/logout",
    response_description="Logout user",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout_user():
    return JSONResponse(
        status_code=status.HTTP_204_NO_CONTENT,
        content={"message": APIMessages.NOT_FOUND},
    )
