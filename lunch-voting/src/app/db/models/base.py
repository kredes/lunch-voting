from sqlalchemy.orm import DeclarativeBase


class DatabaseModel(DeclarativeBase):
    """
    Base class required by SQLAlchemy. All database models must inherit from this class.
    """
