from fastapi import FastAPI
from dotenv import dotenv_values
from pymongo import MongoClient
from routes.bookRouter import router as book_router
from routes.authRouter import router as auth_router

config = dotenv_values(".env")

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = MongoClient(config["MONGO_URI"])
    app.database = app.mongodb_client[config["DB_NAME"]]
    print(f"Connected to the {config['DB_NAME']} database!")


@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()


app.include_router(book_router, tags=["books"], prefix="/book")
app.include_router(auth_router, tags=["auth"], prefix="/auth")
