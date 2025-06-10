from typing import Iterator

import pytest

from fastapi.testclient import TestClient
from sqlalchemy.orm.session import Session

from app.app import app
from app.db.connections import get_session, init_db


@pytest.fixture(scope="session", autouse=True)
def setup_environment() -> None:
    """ """
    # TODO: Split into test and production DB
    init_db()


@pytest.fixture(scope="session")
def client() -> Iterator[TestClient]:
    yield TestClient(app)


@pytest.fixture(scope="function")
def session() -> Iterator[Session]:
    yield from get_session()
