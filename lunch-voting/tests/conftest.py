from __future__ import annotations

from typing import Iterator, TypeVar, Any, Protocol

import pytest

from fastapi.testclient import TestClient
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.expression import select

from app.app import app
from app.db import DatabaseModel, UserModel, RestaurantModel
from app.db.connections import get_session, init_db
from app.routers.dependencies.users import get_authenticated_user
from app.routers.users import hash_password

DatabaseModelType = TypeVar("DatabaseModelType", bound=DatabaseModel)


@pytest.fixture(scope="session", autouse=True)
def setup_environment() -> None:
    """
    Initializes the test database. Because this basic implementation uses a SQLite database on the
    working directory, this will create a database in `/tests` when called here.
    """
    init_db()


@pytest.fixture(scope="function")
def client(user: UserModel) -> Iterator[TestClient]:
    """
    Authentication is tested separately (`users/users_test.py` and `users/auth_test.py`),
    so we're always logged in for this client so we don't have to do this all the time.
    """
    app.dependency_overrides[get_authenticated_user] = lambda: user

    yield TestClient(app)

    del app.dependency_overrides[get_authenticated_user]


@pytest.fixture(scope="function")
def session() -> Iterator[Session]:
    yield from get_session()


def one_or_none[DatabaseModelType](
    model_class: type[DatabaseModelType], session: Session, **fields: Any
) -> DatabaseModelType | None:
    """
    Util function that fetches at most one row from the given table.

    Equivalent to `SELECT * FROM model_table WHERE field_1 = value_1 AND field_2 = value_2 ...`
    """
    query = select(model_class)

    for field, value in fields.items():
        query = query.where(getattr(model_class, field) == value)

    return session.execute(query).scalars().one_or_none()


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


@pytest.fixture
def user(model_factory: ModelFactory) -> Iterator[UserModel]:
    yield model_factory(UserModel, username="someone", password_hash=hash_password("bad_password"))


@pytest.fixture
def restaurant(model_factory: ModelFactory) -> Iterator[RestaurantModel]:
    yield model_factory(RestaurantModel, name="FEBO")
