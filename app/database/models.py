import uuid
from datetime import datetime

from sqlmodel import SQLModel, Field, Column, Text
from pydantic import BaseModel, Field as PField


class Article(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=64)
    pub_date: datetime = Field(default_factory=datetime.now, const=True)
    last_mod: datetime = Field(default_factory=datetime.now)
    author: str
    content: str = Field(sa_column=Column(Text))
    summary: str


class UserBase(SQLModel, Table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    f_name: str | None = Field(default=None, max_length=32)
    l_name: str | None = Field(default=None, max_length=32)
    username: str = Field(min_length=8, max_length=32, primary_key=True)
    password_hash: bytes = Field(max_length=64)


class UserLogin(BaseModel):
    username: str = PField(min_length=8, max_length=32)
    password: str = PField(max_length=32)