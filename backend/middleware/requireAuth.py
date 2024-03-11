from typing import Annotated

from dotenv import dotenv_values
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from models.user import TokenData
from utils.authUtils import get_user_creds

config = dotenv_values(".env")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


async def auth_curr_user(req: Request, token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
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

    user = get_user_creds(req.app.database["users"], username=token_data.username)

    if user is None:
        raise credentials_exception
    return user

