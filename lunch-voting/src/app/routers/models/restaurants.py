from datetime import datetime

from pydantic import BaseModel

from app.routers.models.shared import DataModel, PaginationInfo


class Restaurant(DataModel):
    """
    A restaurant, as returned by the API.
    """

    id: int
    name: str
    created: datetime


class PaginatedRestaurantResponse(DataModel):
    """
    A paginated response containing restaurant objects.
    """

    data: list[Restaurant]
    pagination: PaginationInfo


class RestaurantCreate(BaseModel):
    """
    The data necessary to create a restaurant via the API.
    """

    name: str


class RestaurantUpdate(BaseModel):
    """
    The data necessary to update a restaurant via the API.
    """

    name: str
