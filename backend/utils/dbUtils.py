from models.user import UserBase


def get_user(db, username: str) -> UserBase:
    user_data = db.find_one({"username": username})

    if user_data:
        # If user is found, create a UserBase object using the retrieved data
        return UserBase(**user_data)
    else:
        # If user is not found, return None or handle as needed
        return None
