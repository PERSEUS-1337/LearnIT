from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
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

# Model used for accepting passwords
class UserReg(UserBase):
    password: str

    class Config(UserBase.Config):
        pass

# Model used for registering a UserBase to the DB with a hashed password
class UserInDB(UserBase):
    hashed_password: str

    class Config(UserBase.Config):
        pass

# Model used for retrieving username and hash_pwd for verification purposes
class UserCreds(BaseModel):
    username: str
    hashed_password: str

    class Config(UserBase.Config):
        pass

# Model used for updating user details
class UserUpdate(BaseModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None

    class Config:
        json_schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "johndoe@example.com",
                "full_name": "John Doe"
            }
        }

# Model used for generating JWT during login
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

# Model used for retrieving username embedded in token for user detail retrieval
class TokenData(BaseModel):
    username: str | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "username": "johndoe"
            }
        }
