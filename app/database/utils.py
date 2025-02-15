from typing import Annotated
from datetime import datetime, timezone,timedelta

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select

from app.config import (
    SECRET_KEY,
    TOKEN_ALGORITHM,
    TOKEN_EXPIRED_TIME,
)
from app.database import engine, UserBase, UserLogin, UserPermission


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def password_hasher(passwd: str) -> bytes:
    salt = bcrypt.gensalt()
    pw_hash = bcrypt.hashpw(passwd.encode(), salt)

    return pw_hash


def auth_password(login: UserLogin) -> UserBase:
    with Session(engine) as session:
        try:
            user = session.exec(
                select(UserBase).where(UserBase.username==login.username,)
            ).one()

            assert bcrypt.checkpw(login.password.encode(), user.password_hash)

            return user
        except:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid Username or Password.",
            )


AuthDep = Annotated[UserBase, Depends(auth_password)]


def create_token(user: UserBase) -> str:
    try:
        token = jwt.encode(
            payload={
                "user_id": str(user.id),
                "username": user.username,
                "exp": 
                    datetime.now(timezone.utc) + 
                    timedelta(minutes=TOKEN_EXPIRED_TIME), 
            },
            key=SECRET_KEY,
            algorithm=TOKEN_ALGORITHM,
        )
        return token
    except jwt.PyJWKError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,)


def auth_token(token: str) -> UserBase:
    try:
        payload = jwt.decode(
            token, SECRET_KEY, algorithms=[TOKEN_ALGORITHM],
        )
    except (
        jwt.InvalidTokenError,
        jwt.ExpiredSignatureError,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWKError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    with Session(engine) as session:
        user = session.exec(
            select(UserBase).
                where(UserBase.id == payload["user_id"]).
                where(UserBase.username == payload["username"])
        ).one()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user


def create_user(
    user_login: UserLogin,
    permission: UserPermission = UserPermission.guest,
    f_name: str | None = None,
    l_name: str | None = None,
) -> None:
    try:
        password_hash = password_hasher(user_login.password)
        user = UserBase(
            username=user_login.username,
            password_hash=password_hash,
            permission=permission,
            f_name=f_name,
            l_name=l_name,
        )
        with Session(engine) as session:
            session.add(user)
            session.commit()
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)