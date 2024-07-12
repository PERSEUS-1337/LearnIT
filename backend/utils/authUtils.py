from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Collection, Optional

from dotenv import dotenv_values
from jose import jwt
from passlib.context import CryptContext

from models.user import UserBase, UserCreds

config = dotenv_values(".env")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config["SECRET_KEY"], algorithm=config["ALGO"])
    return encoded_jwt


async def get_user_creds(db: AsyncIOMotorClient, username: str) -> Optional[UserCreds]:
    user_doc = await db.find_one({"username": username})
    if user_doc:
        return UserCreds(**user_doc)
    return None


async def get_user_data(db: AsyncIOMotorClient, username: str) -> Optional[UserBase]:
    user_doc = await db.find_one({"username": username})

    if user_doc:
        return UserBase(**user_doc)
    else:
        return None
