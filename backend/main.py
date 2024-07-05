import time
from dotenv import dotenv_values
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from starlette.responses import Response

from routes.authRouter import router as auth_router
from routes.userRouter import router as user_router
from routes.documentRouter import router as docu_router

config = dotenv_values(".env")

app = FastAPI()

@app.middleware("http")
async def measure_request_time(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time} s"
    return response


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to match your SvelteKit application's origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "This is the API route of LearnIT!"}

@app.get("/hello")
async def root():
    return {"message": "Hello World!"}


@app.on_event("startup")
def startup_db_client():
    try:
        app.mongodb_client = MongoClient(config["MONGO_URI"])
        app.database = app.mongodb_client[config["DB_NAME"]]
        print(f"Connected to the {config['DB_NAME']} database!")
    except Exception as e:
        print(f"Failed to connect to the database: {e}")


@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()


app.include_router(auth_router, tags=["auth"], prefix="/auth")
app.include_router(user_router, tags=["user"], prefix="/user")
app.include_router(docu_router, tags=["docu"], prefix="/docu")
