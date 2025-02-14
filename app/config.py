import secrets
import ssl

from slowapi import Limiter
from slowapi.util import get_remote_address


DEBUG = True

SECRET_KEY = secrets.token_urlsafe(64)
TOKEN_ALGORITHM = "HS256"

# Time by minutes
TOKEN_EXPIRED_TIME = 20

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain(certfile='cert.pem', keyfile='key.pem')

ORIGINS = [
    "https://localhost:8000",
]

# the count of object in each page
PAGINATION = 10

SQLITE_FILE_NAME = "database.db"
SQLITE_URL = f"sqlite:///{SQLITE_FILE_NAME}"

limiter = Limiter(key_func=get_remote_address)