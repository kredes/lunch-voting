from typing import Iterator

from sqlalchemy.engine.base import Engine
from sqlalchemy.engine.create import create_engine
from sqlalchemy.orm.session import Session

from app.db.models.base import DatabaseModel


def get_engine() -> Engine:
    """
    Returns an engine connected to the default database.
    """

    return create_engine("sqlite:///database.db", echo=True)


def get_session() -> Iterator[Session]:
    """
    Returns a `Session` to interact with the database.
    """
    with Session(get_engine()) as session:
        yield session


def init_db() -> None:
    """
    Initializes the database and creates all tables.
    """

    DatabaseModel.metadata.create_all(get_engine())
