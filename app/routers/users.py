from typing import Annotated

from fastapi import APIRouter, Security, Request, HTTPException, status
from sqlmodel import select

from app.config import limiter
from app.routers import auth_header_scheme
from app.database import (
    SessionDep, 
    AuthDep,
    UserBase,
    UserLogin,
    UserInfo,
    UserPermissionInfo,
    UserPermission,
    create_token,
    auth_token,
    create_user,
)

router = APIRouter(
    tags=["Users"],
    prefix="/users",
)




@router.post("/login")
@limiter.limit("3/hour")
async def login_user(request: Request, user: AuthDep):
    return {"token": create_token(user)}


@router.post("/register", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("10/hour")
async def register_user(
    request: Request, session: SessionDep, user: UserLogin,
) -> None:
    existing_user = session.exec(
        select(UserBase).where(UserBase.username == user.username)
    ).one_or_none()
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Username already exists.",
        )
    create_user(user)


@router.get("/permission")
async def users_permission(
    session: SessionDep,
    token: Annotated[str, Security(auth_header_scheme)],
) -> list[UserPermissionInfo]:
    user = auth_token(token)
    if user.permission != UserPermission.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    print("this sisssssssssssssssssssssssssssssssssssssssssss")
    users = session(
        select(UserBase.username, UserBase.permission)
    ).all()
    return users


@router.get("/info")
async def user_info(session: SessionDep) -> list[UserInfo]:
    users = session.exec(
        select(UserBase.username, UserBase.f_name, UserBase.l_name)
    ).all()
    return users