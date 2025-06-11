from datetime import datetime

from pydantic import BaseModel

from app.routers.models.shared import DataModel


class AuthToken(BaseModel):
    """
    An authentication token, as returned by the API.
    """

    access_token: str
    token_type: str


class CreateUserData(BaseModel):
    """
    The data necessary to create a new user via the API.
    """

    username: str
    password: str


class User(DataModel):
    """
    A user, as returned by the API.
    """

    username: str
    created: datetime
