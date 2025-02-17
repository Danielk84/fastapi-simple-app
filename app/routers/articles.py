import uuid
from typing import Annotated
from datetime import datetime

from fastapi import (
    APIRouter,
    Depends,
    Body,
    Path,
    HTTPException,
    status,
)
from sqlmodel import select

from app.config import PAGINATION
from app.database import (
    SessionDep,
    Article,
    ArticleList,
    ArticleBase,
    UserPermission,
    TokenValidateDep,
)

router = APIRouter(
    tags=["Articles"],
    prefix="/articles",
)


async def pagination(page: int) -> int:
    return page * PAGINATION


@router.get("/")
async def articles_list(
    session: SessionDep, page: Annotated[int, Depends(pagination)] = 0,
) -> list[ArticleList]:
    return session.exec(
        select(Article.author, Article.id, Article.title, Article.last_mod).
            where(Article.pub_date <= datetime.now()).
            offset(page).limit(PAGINATION)
    ).all()


@router.post("/")
async def create_article(
    session: SessionDep,
    user: TokenValidateDep,
    content: ArticleBase,
) -> ArticleBase:
    if user.permission == UserPermission.guest:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    article = Article(**content.model_dump())
    try:
        session.add(article)
        session.commit()

        return content
    except:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)


@router.get("/{article_title}/{article_id}")
async def get_article(
    session: SessionDep, article_title: str, article_id: uuid.UUID,
) -> Article:
    try:
        return session.exec(
            select(Article).
                where(Article.title == article_title).
                where(Article.id == article_id)
        ).one()
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.put("/{article_title}/{article_id}")
async def update_article(
    session: SessionDep,
    user: TokenValidateDep,
    article_title: Annotated[str, Path()],
    article_id: Annotated[uuid.UUID, Path()],
    mod_article: Annotated[ArticleBase, Body()],
) -> ArticleBase:
    if user.permission == UserPermission.guest:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    try:
        article = session.exec(
            select(Article).
                where(Article.id == article_id).
                where(Article.title == article_title)
        ).one()
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    for key, value in mod_article.model_dump().items():
        setattr(article, key, value)

    session.add(article)
    session.commit()

    return mod_article


@router.delete(
    "/{article_title}/{article_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_article(
    session: SessionDep,
    article_title: Annotated[str, Path()],
    article_id: Annotated[uuid.UUID, Path()],
    user: TokenValidateDep,
) -> None:
    if user.permission == UserPermission.guest:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    try:
        article = session.exec(
            select(Article).
                where(Article.id == article_id).
                where(Article.title == article_title)
        ).one()
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    session.delete(article)
    session.commit()