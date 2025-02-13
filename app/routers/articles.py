from typing import Annotated
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlmodel import select

from app import main
from app.database import Article
from app.database.utils import SessionDep

router = APIRouter(
    tags=["Articles"],
    prefix="/articles",
)


async def pagination(page: int) -> int:
    return page * main.PAGINATION


@router.get("/")
async def articles_list(
    session: SessionDep,
    page: Annotated[int, Depends(pagination)] = 0,
) -> list[Article]:
    return session.exec(
        select(Article).where(Article.pub_date <= datetime.now()).offset(page).limit(main.PAGINATION)
    ).all()