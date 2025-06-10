from typing import Iterator

import pytest

from fastapi.testclient import TestClient

from app.app import app  # type: ignore


@pytest.fixture(scope="function")
def client() -> Iterator[TestClient]:
    """
    An unauthenticated client.
    """
    yield TestClient(app)
