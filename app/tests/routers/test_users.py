from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from ..utils import session_fixture, client_fixture, logger_fixture
from app.database import (
    UserBase,
    BasePassword,
    UserLogin,
    UserPermission,
    UserInfo,
    create_user,
    create_token,
    auth_token,
)

base_url = "/users"


def temp_create_user() -> tuple[UserBase, UserLogin]:
    user_login = UserLogin(username="testuser", password="testpasswd")
    user = create_user(
        user_login=user_login,
        permission=UserPermission.admin,
    )
    return (user, user_login)


def test_login_user(session: Session, client: TestClient, logger):
    user, user_login = temp_create_user()

    response = client.post(
        base_url + "/login",
        content=user_login.model_dump_json(),
    )
    assert response.status_code == status.HTTP_200_OK
    assert auth_token(**response.json()) == user
    logger.info("Test login user, 200 status.")

    user_login = UserLogin(username="invalid", password="invalidpasswd")
    response = client.post(
        base_url + "/login",
        content=user_login.model_dump_json(),
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    logger.info("Test login user, 404 status.")


def test_register_user(session: Session, client: TestClient, logger):
    user_login = UserLogin(username="testuser", password="testpasswd")

    response = client.post(
        base_url + "/register",
        content=user_login.model_dump_json(),
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    user = session.exec(
        select(UserBase).where(UserBase.username == user_login.username)
    ).one_or_none()
    assert user is not None
    logger.info("Test register_user.")


def test_change_password(session: Session, client: TestClient, logger):
    user, user_login = temp_create_user()
    token = create_token(user)

    old_passwd_hash = user.password_hash
    passwd = BasePassword(password="newpasswd")

    response = client.put(
        base_url + "/change-password",
        headers={"Authorization": token},
        content=passwd.model_dump_json(),
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    user = session.exec(
        select(UserBase).where(UserBase.username == user_login.username)
    ).one()
    assert user.password_hash != old_passwd_hash
    logger.info("Test Change_Password.")


def test_user_info(session: Session, client: TestClient, logger):
    user, user_login = temp_create_user()
    token = create_token(user)

    response = client.get(
        base_url + "/info",
        headers={"Authorization": token},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == UserInfo(**user.model_dump()).username
    logger.info("Test user_info.")


def test_update_user_info(session: Session, client: TestClient, logger):
    user, user_login = temp_create_user()
    token = create_token(user)
    user_info = UserInfo(id=user.id, username="newuser")

    response = client.put(
        base_url + "/info",
        headers={"Authorization": token},
        content=user_info.model_dump_json(),
    )
    assert response.status_code == status.HTTP_202_ACCEPTED
    user = session.exec(
        select(UserBase).where(UserBase.username == user_info.username)
    ).one()
    assert response.json()["username"] == user_info.username
    logger.info("Test update_user_info.")


def test_delete_user(session: Session, client: TestClient, logger):
    user, user_login = temp_create_user()
    token = create_token(user)

    response = client.delete(
        base_url + "/info",
        headers={"Authorization": token},
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    user = session.exec(
        select(UserBase).where(UserBase.username == user_login.username)
    ).one_or_none()
    assert user is None
    logger.info("Test delete_user.")