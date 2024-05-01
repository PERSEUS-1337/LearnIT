from pymongo.collection import Collection
from models.user import UserBase


def get_user_data(db, username: str) -> UserBase:
    user = db.find_one({"username": username})

    if user:
        return UserBase(**user)
    else:
        return None
