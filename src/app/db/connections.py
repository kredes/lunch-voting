from pathlib import Path
from typing import Iterator

from sqlalchemy.engine.base import Engine
from sqlalchemy.engine.create import create_engine
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.expression import text

from app.config import Config


def get_engine() -> Engine:
    """
    Returns an engine connected to the default database.
    """
    database_path = Path(Config.database_dir).expanduser()

    if not database_path.exists():
        database_path.mkdir(parents=True, exist_ok=True)

    return create_engine(f"sqlite:///{str(database_path)}/database.db", echo=True)


def get_session() -> Iterator[Session]:
    """
    Returns a `Session` to interact with the database.
    """
    with Session(get_engine()) as session:
        # For god knows what reason, foreign keys are disabled by default in SQLite AND they have
        # to be enabled on each connection.
        session.execute(text("PRAGMA foreign_keys = ON"))
        session.commit()

        yield session
