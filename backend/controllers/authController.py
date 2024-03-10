from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status, Request, Body
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from jose import jwt
from passlib.context import CryptContext

from models.user import Token, UserInDB, UserReg
from middleware.apiMsg import APIMessages

# config = dotenv_values(".env")

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
# SECRET_KEY = config["SECRET_KEY"]


fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

app = FastAPI()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str) -> UserInDB:
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(db, username: str, password: str):
    user = db.find_one({"username": username})
    print(user)
    if not user:
        return False
    if not verify_password(password, user['hashed_password']):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def login_for_access_token(req: Request, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = authenticate_user(req.app.database["users"], form_data.username, form_data.password)
    print(user)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


def create_user(req: Request, user: UserReg = Body(...)):
    try:
        user_exists = req.app.database["users"].find_one({"email": user.username})

        if user_exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A user with the username '{user.username}' already exists."
            )

        hashed_pass = get_password_hash(user.password)
        time_now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        new_user_data = UserInDB(username=user.username, email=user.email,
                                 full_name=user.full_name, hashed_password=hashed_pass,
                                 date_created=time_now)

        new_user_data = new_user_data.dict()
        insert_result = req.app.database["users"].insert_one(new_user_data)

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": APIMessages.USER_CREATED})
    except HTTPException as he:
        # Re-raise if it already has a status code
        raise he

    except Exception as e:
        # Print the error
        print(f"An unexpected error occurred: {str(e)}")
        # Handle exceptions here and return a proper status code and detail message
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
