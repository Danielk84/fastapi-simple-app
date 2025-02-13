from typing import Annotated
from datetime import datetime, timezone,timedelta

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select


from app import main
from app.database import UserBase, UserLogin


def get_session():
    with Session(main.engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def password_hasher(passwd: str) -> bytes:
    salt = bcrypt.gensalt()
    pw_hash = bcrypt.hashpw(passwd.encode(), salt)

    return pw_hash


def auth_password(login: UserLogin) -> bool:
    with Session(main.engine) as session:
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


def create_token(user: UserBase) -> str:
    try:
        token = jwt.encode(
            payload={
                "user_id": user.id,
                "username": user.username,
                "exp": 
                    datetime.now(timezone.utc) + 
                    timedelta(minutes=main.TOKEN_EXPIRED_TIME), 
            },
            key=main.SECRET_KEY,
            algorithm=main.TOKEN_ALGORITHM,
        )
        return token
    except jwt.PyJWKError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,)


def check_token(token: str) -> UserBase:
    try:
        payload = jwt.decode(
            token=token,
            key=main.SECRET_KEY,
            algorithms=main.TOKEN_ALGORITHM,
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

    with Session(main.engine) as session:
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