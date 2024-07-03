from typing import Optional, List
from pydantic import BaseModel, EmailStr
from models.document import UploadDoc


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    uploaded_files: List[UploadDoc] = []

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "johndoe@example.com",
                "full_name": "John Doe",
                "uploaded_files": [],
            }
        }

    def dict(self):
        return {
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "uploaded_files": [file.dict() for file in self.uploaded_files],
        }


class UserReg(UserBase):
    password: str

    class Config(UserBase.Config):
        pass

    def dict(self):
        base_dict = super().dict()
        base_dict.update({"password": self.password})
        return base_dict


class UserInDB(UserBase):
    hashed_password: str

    class Config(UserBase.Config):
        pass

    def dict(self):
        base_dict = super().dict()
        base_dict.update({"hashed_password": self.hashed_password})
        return base_dict


class UserCreds(BaseModel):
    username: str
    hashed_password: str

    class Config(UserBase.Config):
        pass

    def dict(self):
        return {"username": self.username, "hashed_password": self.hashed_password}


class UserUpdate(BaseModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    uploaded_files: Optional[List[UploadDoc]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "johndoe@example.com",
                "full_name": "John Doe",
            }
        }

    def dict(self):
        return {
            "username": self.username,
            "full_name": self.full_name,
            "email": self.email,
            "uploaded_files": (
                [file.dict() for file in self.uploaded_files]
                if self.uploaded_files
                else None
            ),
        }


class Token(BaseModel):
    access_token: str
    token_type: str

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
                "token_type": "bearer",
            }
        }

    def dict(self):
        return {"access_token": self.access_token, "token_type": self.token_type}


class TokenData(BaseModel):
    username: Optional[str] = None

    class Config:
        json_schema_extra = {"example": {"username": "johndoe"}}

    def dict(self):
        return {"username": self.username}
