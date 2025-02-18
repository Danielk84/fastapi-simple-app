import uuid

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from ..utils import session_fixture, client_fixture, logger_fixture
from app.config import PAGINATION
from app.database import (
    Article,
    ArticleList,
    ArticleBase,
    UserLogin,
    UserPermission,
    create_user,
    create_token,
)

base_url = "/articles"


def test_articles_list(session: Session, client: TestClient, logger):
    response = client.get(base_url + "/", params={"page": 0})
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    logger.info("Test 404 error for empty article_list.")

    for i in range(20):
        session.add(
            Article(
                title=f"title{i}", author=f"author{i}", content=f"content{i}", summary=f"summ{i}"
            )
        )
    session.commit()
    for i in range(2):
        response = client.get(base_url + "/", params={"page": i})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == PAGINATION
    logger.info("Test pagination and articles count.")

    article = ArticleList(**response.json()[0])
    assert list(article.model_dump().keys()) == ["id", "title", "author", "last_mod"]
    logger.info("Test ArticleList model.")


def temp_article_base_user():
    user = create_user(
        UserLogin(username="tempuser", password="temppasswd"),
        UserPermission.staff
    )
    token = create_token(user)
    article = ArticleBase(
        title="titlebase",
        content="contentbase",
        summary="summbase",
        author="authorbase",
    )
    headers = {"Authorization": token}
    return {
        "user": user,
        "token": token,
        "article": article,
        "headers": headers,
    }


def test_create_article(session: Session, client: TestClient, logger):
    temp = temp_article_base_user()

    response = client.post(
        base_url + "/",
        headers=temp["headers"],
        content=temp["article"].model_dump_json()
    )
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json()["title"] == temp["article"].model_dump()["title"]
    logger.info("Test create_article.")


def test_get_article(session: Session, client: TestClient, logger):
    article = Article(
        title="title",
        author="auth",
        content="content",
        summary="sum",
    )
    session.add(article)
    session.commit()
    session.refresh(article)

    response = client.get(base_url + f"/{article.title}/{article.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == article.model_dump()["title"]
    logger.info("Test get_article, status 200.")

    response = client.get(base_url + f"/{'not-cureect-title'}/{uuid.uuid4()}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    logger.info("Test get_article, 404 status error.")


def temp_create_article(session: Session):
    article = Article(
        title="titletest",
        author="auth",
        content="content",
        summary="sum",
    )
    session.add(article)
    session.commit()
    session.refresh(article)

    return article


def test_update_article(session: Session, client: TestClient, logger):
    article = temp_create_article(session)
    temp = temp_article_base_user()

    response = client.put(
        base_url + f"/{article.title}/{article.id}",
        content=temp["article"].model_dump_json(),
        headers=temp["headers"],
    )
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json()["title"] == temp["article"].model_dump()["title"]
    logger.info("Test update_article.")


def test_delete_article(session: Session, client: TestClient, logger):
    article = temp_create_article(session)
    temp = temp_article_base_user()

    response = client.delete(
        base_url + f"/{article.title}/{article.id}",
        headers=temp["headers"],
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    logger.info("Test delete_article.")