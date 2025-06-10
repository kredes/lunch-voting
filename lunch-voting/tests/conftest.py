from __future__ import annotations

from typing import Iterator, TypeVar, Any, Protocol

import pytest

from fastapi.testclient import TestClient
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.session import Session

from app.app import app
from app.db import DatabaseModel, UserModel
from app.db.connections import get_session, init_db
from app.routers.users import hash_password

DatabaseModelType = TypeVar("DatabaseModelType", bound=DatabaseModel)


@pytest.fixture(scope="session", autouse=True)
def setup_environment() -> None:
    """ """
    # TODO: Split into test and production DB
    init_db()


@pytest.fixture(scope="function")
def client(model_factory: ModelFactory) -> Iterator[TestClient]:
    """
    Authentication is tested separately (`users/users_test.py` and `users/auth_test.py`),
    so we're always logged in for this client so we don't have to do this all the time.
    """
    username = "cool_guy"
    password = "8n$039AD9wa564@"

    model_factory(UserModel, username=username, password_hash=hash_password(password))

    client = TestClient(app)

    response = client.post("/login", data={"username": username, "password": password})
    assert response.status_code == 200

    client.headers["Authorization"] = f"Bearer {response.json()['access_token']}"

    yield client


@pytest.fixture(scope="function")
def session() -> Iterator[Session]:
    yield from get_session()


class ModelFactory(Protocol):
    def __call__(
        self, model_class: type[DatabaseModelType], **fields: Any
    ) -> DatabaseModelType: ...


@pytest.fixture(scope="function")
def model_factory(session: Session) -> Iterator[ModelFactory]:
    """
    Creates instances of the given database model and cleans them up after tests are done.
    """
    models: list[DatabaseModel] = []

    def _model_factory(model_class: type[DatabaseModelType], **fields: Any) -> DatabaseModelType:
        model = model_class(**fields)
        session.add(model)
        session.commit()

        models.append(model)

        return model

    yield _model_factory

    for model in models:
        try:
            # Sometimes rows are deleted without the model reflecting it.
            # If we can refresh the model, we know it's still around and can be deleted.
            session.refresh(model)
            session.delete(model)
            session.commit()
        except InvalidRequestError:
            pass
