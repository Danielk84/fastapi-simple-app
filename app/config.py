import secrets

from sqlmodel import create_engine
from slowapi import Limiter
from slowapi.util import get_remote_address


DEBUG = False


SECRET_KEY = secrets.token_urlsafe(64)
TOKEN_ALGORITHM = "HS256"

# Time by minutes
TOKEN_EXPIRED_TIME = 20

ORIGINS = [
    "https://localhost:8000",
]

# the count of object in each page
PAGINATION = 10

if DEBUG:
    SQLITE_FILE_NAME = "test.db"
else:
    SQLITE_FILE_NAME = "database.db"

SQLITE_URL = f"sqlite:///{SQLITE_FILE_NAME}"

engine = create_engine(SQLITE_URL)

limiter = Limiter(key_func=get_remote_address)