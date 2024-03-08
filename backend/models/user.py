from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    fname: str
    lname: str
    usertype: str  # You might want to use an Enum for limited choices (admin or user)
    email: EmailStr
    password: str

    class Config:
        # Using the Pydantic Config class to set additional configurations
        schema_extra = {
            "example": {
                "fname": "John",
                "lname": "Doe",
                "usertype": "user",
                "email": "john.doe@example.com",
                "password": "secretpassword",
            }
        }
