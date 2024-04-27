from dotenv import dotenv_values
from fastapi import FastAPI
from pymongo import MongoClient

from routes.authRouter import router as auth_router
from routes.bookRouter import router as book_router
from routes.userRouter import router as user_router

config = dotenv_values(".env")

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.on_event("startup")
def startup_db_client():
    try:
        app.mongodb_client = MongoClient(config["MONGO_URI"])
        app.database = app.mongodb_client[config["DB_NAME"]]
        print(f"Connected to the {config['DB_NAME']} database!")
    except Exception as e:
        print(f"Failed to connect to the database: {e}")
        # Optionally, you can raise an exception or handle the error in another way
        # raise e


@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()


app.include_router(auth_router, tags=["auth"], prefix="/auth")
app.include_router(user_router, tags=["user"], prefix="/user")
app.include_router(book_router, tags=["book"], prefix="/book")
