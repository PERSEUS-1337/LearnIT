from typing import Annotated

from dotenv import dotenv_values
from fastapi import Depends, HTTPException, status, Request
from jose import JWTError, jwt

from controllers.authController import check_user_details, oauth2_scheme
from models.user import TokenData

config = dotenv_values(".env")


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

    user = check_user_details(req.app.database["users"], username=token_data.username)

    if user is None:
        raise credentials_exception
    return user
