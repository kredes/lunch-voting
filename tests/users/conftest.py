from typing import Iterator

import pytest

from fastapi.testclient import TestClient

from app.app import app  # type: ignore


@pytest.fixture(scope="function")
def unauthenticated_client() -> Iterator[TestClient]:
    """
    A client without authentication headers.
    """
    yield TestClient(app)
