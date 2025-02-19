import contextlib

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from sqlmodel import SQLModel
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded


from app.config import DEBUG, ORIGINS, limiter, engine
from app.routers import articles, users


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


app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


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
    )