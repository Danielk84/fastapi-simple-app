import logging
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session

from app import app
from app.config import engine


@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture():
    return TestClient(app)


@pytest.fixture(name="logger")
def logger_fixture():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('\n%(asctime)s [%(levelname)s] %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger