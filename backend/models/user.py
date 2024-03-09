from pydantic import BaseModel, EmailStr


class RegisterForm(BaseModel):
    full_name: str
    username: str
    email: str
    password: str


class User(BaseModel):
    username: str
    email: str
    full_name: str
    disabled: bool


class UserInDB(User):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
