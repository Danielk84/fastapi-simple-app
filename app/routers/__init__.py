from fastapi.security import APIKeyHeader as _APIKeyH

from . import articles
from . import users

auth_header_scheme = _APIKeyH(name="Authorization")