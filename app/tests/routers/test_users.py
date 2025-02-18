from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from ..utils import session_fixture, client_fixture, logger_fixture
from app.database import (
    UserLogin,
    UserPermission,
    create_user,
    auth_token,
)

base_url = "/users"


def temp_create_user(session: Session):
    user = create_user(
        UserLogin(username="testuser", password="testpasswd"),
        permission=UserPermission.admin,
    )
    session.add(user)
    session.commit
    session.refresh(user)

    return user


def test_login_user(session: Session, client: TestClient, logger):
    pass