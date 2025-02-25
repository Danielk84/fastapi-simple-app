import uuid
from enum import Enum
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


class ArticleList(BaseModel):
    id: uuid.UUID
    title: str
    author: str
    last_mod: datetime


class ArticleBase(BaseModel):
    title: str = PField(max_length=64)
    last_mod: datetime = PField(default_factory=datetime.now)
    author: str
    content: str
    summary: str


class UserPermission(Enum):
    guest = "guest"
    staff = "staff"
    admin = "admin"


class UserBase(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    f_name: str | None = Field(default=None, max_length=32)
    l_name: str | None = Field(default=None, max_length=32)
    username: str = Field(max_length=32, primary_key=True)
    password_hash: bytes = Field(max_length=64)
    permission: UserPermission = Field(default=UserPermission.guest)



class BasePassword(BaseModel):
    password: str = PField(min_length=8, max_length=32)


class UserLogin(BasePassword):
    username: str = PField(max_length=32)



class UserInfo(BaseModel):
    id: uuid.UUID
    username: str
    f_name: str | None = PField(default=None)
    l_name: str | None = PField(default=None)


class UserPermissionInfo(BaseModel):
    id: uuid.UUID
    username: str
    permission: UserPermission