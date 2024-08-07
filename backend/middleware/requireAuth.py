from typing import Annotated

from dotenv import dotenv_values
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from middleware.apiMsg import APIMessages
from models.user import TokenData, UserBase
from utils.authUtils import get_user_data

config = dotenv_values(".env")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


async def auth_curr_user(
    req: Request, token: Annotated[str, Depends(oauth2_scheme)]
) -> UserBase:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=APIMessages.VALIDATION_ERROR,
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config["SECRET_KEY"], algorithms=[config["ALGO"]])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = await get_user_data(
        req.app.database[config["USER_DB"]], username=token_data.username
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=APIMessages.USER_NOT_FOUND
        )
    return user
