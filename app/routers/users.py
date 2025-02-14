from typing import Annotated

from fastapi import APIRouter, Security, Request
from fastapi.security import APIKeyHeader

from app.config import limiter
from app.database import AuthDep, create_token

router = APIRouter(
    tags=["Users"],
    prefix="/users",
)

auth_header_scheme = APIKeyHeader(name="Authorization")


@router.post("/login/")
@limiter.limit("1/minute")
async def login(request: Request, user: AuthDep):
    return {"token": create_token(user)}


@router.get("/info")
async def user_info(key: Annotated[str, Security(auth_header_scheme)]):
    return {"token": key}
