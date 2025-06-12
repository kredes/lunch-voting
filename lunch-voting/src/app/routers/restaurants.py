from typing import Annotated

from sqlalchemy.sql.functions import func

from app.routers.dependencies.database import SessionDep
from app.db.models.restaurants import RestaurantModel

from pydantic import TypeAdapter
from sqlalchemy import select, update, delete
from fastapi import Response, APIRouter, Depends, Query

from app.routers.dependencies.users import get_authenticated_user
from app.routers.models.restaurants import (
    RestaurantCreate,
    RestaurantUpdate,
    Restaurant,
    PaginatedRestaurantResponse,
)
from app.routers.models.shared import PaginationInfo

router = APIRouter(tags=["restaurants"])


@router.get("/restaurants", dependencies=[Depends(get_authenticated_user)], status_code=200)
def get_restaurants(
    session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 10
) -> PaginatedRestaurantResponse:
    """
    Returns all existing restaurants.
    """
    total_restaurant_count_query = select(func.count()).select_from(RestaurantModel)
    total_restaurant_count = int(session.scalar(total_restaurant_count_query))

    query = select(RestaurantModel).order_by(RestaurantModel.id).offset(offset).limit(limit)
    restaurants = session.scalars(query).all()

    return PaginatedRestaurantResponse(
        data=TypeAdapter(list[Restaurant]).validate_python(restaurants),
        pagination=PaginationInfo(
            offset=offset,
            limit=limit,
            total=total_restaurant_count,
        ),
    )


@router.post("/restaurants", dependencies=[Depends(get_authenticated_user)], status_code=201)
def create_restaurant(data: RestaurantCreate, session: SessionDep) -> Restaurant:
    """
    Creates a new restaurant.
    """
    restaurant = RestaurantModel(**data.model_dump())
    session.add(restaurant)
    session.commit()

    return Restaurant.model_validate(restaurant)


@router.put(
    "/restaurants/{restaurant_id}", dependencies=[Depends(get_authenticated_user)], status_code=200
)
def update_restaurant(
    restaurant_id: int, data: RestaurantUpdate, response: Response, session: SessionDep
) -> Restaurant | None:
    """
    Updates a restaurant.
    """

    result = session.scalars(
        update(RestaurantModel)
        .values(name=data.name)
        .where(RestaurantModel.id == restaurant_id)
        .returning(RestaurantModel),
    )
    restaurant = result.one_or_none()

    session.commit()

    if restaurant is None:
        response.status_code = 404

    return Restaurant.model_validate(restaurant)


@router.delete(
    "/restaurants/{restaurant_id}", dependencies=[Depends(get_authenticated_user)], status_code=200
)
def delete_restaurant(restaurant_id: int, response: Response, session: SessionDep) -> None:
    """
    Deletes a restaurant.
    """

    result = session.execute(delete(RestaurantModel).where(RestaurantModel.id == restaurant_id))
    session.commit()

    if result.rowcount == 0:
        response.status_code = 404
