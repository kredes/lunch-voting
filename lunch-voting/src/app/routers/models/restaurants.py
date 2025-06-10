from datetime import datetime

from pydantic import BaseModel

from app.routers.models.shared import DataModel


class Restaurant(DataModel):
    id: int
    name: str
    created: datetime


class RestaurantCreate(BaseModel):
    name: str


class RestaurantUpdate(BaseModel):
    name: str
