from typing import Annotated

from fastapi import APIRouter, Security
from fastapi.security import APIKeyHeader

router = APIRouter(
    tags=["Users"],
    prefix="/users",
)

auth_header_scheme = APIKeyHeader(name="Authorization")


@router.get("/")
async def token(key: Annotated[str, Security(auth_header_scheme)]):
    return {"token": key}