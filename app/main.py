import contextlib
import secrets
import ssl

import uvicorn
from fastapi import FastAPI
from fastapi.middleware import Middleware as Mid
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from sqlmodel import SQLModel, create_engine

from app.database import models
from app.routers import articles, users

DEBUG = True

SECRET_KEY = secrets.token_urlsafe(64)
TOKEN_ALGORITHM = "HS256"

# Time by minutes
TOKEN_EXPIRED_TIME = 20

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain(certfile='cert.pem', keyfile='key.pem')

ORIGINS = [
    "https://localhost:8000",
]

# the count of object in each page
PAGINATION = 10

SQLITE_FILE_NAME = "database.db"
SQLITE_URL = f"sqlite:///{SQLITE_FILE_NAME}"

engine = create_engine(SQLITE_URL, echo=DEBUG)


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(
    title="FastAPI-Simple-App",
    version="0.1.0",
    redoc_url=None,
    debug=DEBUG,
    lifespan=lifespan,
)


app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=800, compresslevel=5)


app.include_router(articles.router)
app.include_router(users.router)


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="localhost",
        port=8000,
        ssl_certfile="cert.pem",
        ssl_keyfile="key.pem",
    )