from datetime import datetime

from pydantic import BaseModel

from app.routers.models.shared import DataModel


class AuthToken(BaseModel):
    access_token: str
    token_type: str


class CreateUserData(BaseModel):
    username: str
    password: str


class UserData(DataModel):
    username: str
    created: datetime
