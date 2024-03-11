from typing import Optional

from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "johndoe@example.com",
                "full_name": "John Doe"
            }
        }


class UserReg(UserBase):
    password: str

    class Config(UserBase.Config):
        pass


class UserInDB(UserBase):
    hashed_password: str

    # date_created: datetime

    class Config(UserBase.Config):
        pass


class UserCreds(BaseModel):
    username: str
    hashed_password: str

    class Config(UserBase.Config):
        pass


class UserUpdate(BaseModel):
    username: Optional[str]
    full_name: Optional[str]
    email: Optional[EmailStr]

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Don Quixote",
                "author": "Miguel de Cervantes",
                "synopsis": "Don Quixote is a Spanish novel by Miguel de Cervantes..."
            }
        }


class Token(BaseModel):
    access_token: str
    token_type: str

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
                "token_type": "bearer"
            }
        }


class TokenData(BaseModel):
    username: str | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "username": "johndoe"
            }
        }
