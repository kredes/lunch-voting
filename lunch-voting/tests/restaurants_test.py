import pytest

from fastapi.testclient import TestClient
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.session import Session

from app.db.models.restaurants import RestaurantModel
from .conftest import ModelFactory, one_or_none


def test_create_restaurant(client: TestClient, session: Session) -> None:
    response = client.post("/restaurants", json={"name": "The Scrapyard"})
    assert response.status_code == 201

    restaurant = one_or_none(RestaurantModel, session, name="The Scrapyard")

    try:
        assert restaurant is not None
    finally:
        session.delete(restaurant)
        session.commit()


def test_update_restaurant(
    client: TestClient, model_factory: ModelFactory, session: Session
) -> None:
    restaurant = model_factory(RestaurantModel, name="The Scrapyard")

    response = client.put(f"/restaurants/{restaurant.id}", json={"name": "Can Andres"})
    assert response.status_code == 200

    # The name change is reflected in the database
    session.refresh(restaurant)
    assert restaurant.name == "Can Andres"


def test_get_all_restaurants_paginated(client: TestClient, model_factory: ModelFactory) -> None:
    """
    Tests that pagination for the /restaurants endpoint works.
    """
    for i in range(50):
        model_factory(RestaurantModel, name=f"Restaurant {i}")

    def request_page_and_assert(
        offset: int, limit: int, expected_length: int, expected_first_restaurant: str
    ) -> None:
        response = client.get("/restaurants", params={"offset": offset, "limit": limit})
        response_data = response.json()
        assert response.status_code == 200
        assert len(response_data["data"]) == expected_length
        assert response_data["data"][0]["name"] == expected_first_restaurant
        assert response_data["pagination"] == {"offset": offset, "limit": limit, "total": 50}

    # First and page, should 20 restaurants each time
    request_page_and_assert(0, 20, 20, "Restaurant 0")
    request_page_and_assert(20, 20, 20, "Restaurant 20")

    # The last page should only have 10 restaurants
    request_page_and_assert(40, 20, 10, "Restaurant 40")


def test_delete_restaurant(
    client: TestClient, model_factory: ModelFactory, session: Session
) -> None:
    restaurant = model_factory(RestaurantModel, name="The Scrapyard")

    response = client.delete(f"/restaurants/{restaurant.id}")

    assert response.status_code == 200

    with pytest.raises(InvalidRequestError):
        session.refresh(restaurant)
