from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.expression import select
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.sqltypes import DateTime

from app.db.models.base import DatabaseModel


class UserModel(DatabaseModel):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[bytes]
    created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.current_timestamp(), nullable=False
    )

    @staticmethod
    def get_by_username(username: str, session: Session) -> UserModel | None:
        """
        Returns the user identified by username, if it exists.
        """
        query = select(UserModel).where(UserModel.username == username)
        return session.execute(query).scalars().one_or_none()
