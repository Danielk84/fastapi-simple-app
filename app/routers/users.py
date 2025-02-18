from fastapi import APIRouter, Request, HTTPException, status
from sqlmodel import select

from app.config import limiter
from app.database import (
    SessionDep, 
    AuthDep,
    UserBase,
    BasePassword,
    UserLogin,
    UserInfo,
    UserPermissionInfo,
    UserPermission,
    create_token,
    TokenValidateDep,
    create_user,
    password_hasher,
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


@router.put("/change-password", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("10/hour")
async def change_password(
    request: Request,
    session: SessionDep,
    user: TokenValidateDep,
    new_passwd: BasePassword,
) -> None:
    try:
        passwd_hash = password_hasher(new_passwd.password)
        user.password_hash = passwd_hash

        session.add(user)
        session.commit()
    except:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)


@router.get("/permission")
async def users_permission(
    session: SessionDep, user: TokenValidateDep,
) -> list[UserPermissionInfo]:
    if user.permission != UserPermission.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    users = session.exec(
        select(UserBase.id, UserBase.username, UserBase.permission)
    ).all()
    return users


@router.put("/permission", status_code=status.HTTP_202_ACCEPTED)
async def change_permission(
    session: SessionDep,
    admin: TokenValidateDep,
    user_perm: UserPermissionInfo,
) -> UserPermissionInfo:
    if admin.permission != UserPermission.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    try:
        user = session.exec(
            select(UserBase).where(UserBase.id == user_perm.id)
        ).one()

        user.permission = user_perm.permission
        session.add(user)
        session.commit()

        return user_perm
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.get("/info")
@limiter.limit("20/hour")
async def user_info(
    request: Request, session: SessionDep, user: TokenValidateDep,
) -> UserInfo:
    return UserInfo(**user.model_dump()) 


@router.put("/info", status_code=status.HTTP_202_ACCEPTED)
@limiter.limit("10/hour")
async def update_user_info(
    request: Request,
    session: SessionDep,
    user: TokenValidateDep,
    info: UserInfo,
) -> UserInfo:
    if user.id != info.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    try:
        for key, value in info.model_dump().items():
            setattr(user, key, value)

        session.add(user)
        session.commit()

        return info
    except:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)


@router.delete("/info", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(session: SessionDep, user: TokenValidateDep) -> None:
    session.delete(user)
    session.commit()