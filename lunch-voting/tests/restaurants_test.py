import pytest

from fastapi.testclient import TestClient
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.session import Session

from app.db.models.restaurants import RestaurantModel
from .conftest import ModelFactory, one_or_none


def test_create_restaurant(client: TestClient, session: Session) -> None:
    """ """
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
    """ """
    restaurant = model_factory(RestaurantModel, name="The Scrapyard")

    response = client.put(f"/restaurants/{restaurant.id}", json={"name": "Can Andres"})
    assert response.status_code == 200

    # The name change is reflected in the database
    session.refresh(restaurant)
    assert restaurant.name == "Can Andres"


def test_get_all_restaurants(client: TestClient, model_factory: ModelFactory) -> None:
    """ """
    model_factory(RestaurantModel, name="The Scrapyard")
    model_factory(RestaurantModel, name="Can Andres")
    model_factory(RestaurantModel, name="Burger King")

    response = client.get("/restaurants")

    assert response.status_code == 200
    assert len(response.json()) == 3


def test_delete_restaurant(
    client: TestClient, model_factory: ModelFactory, session: Session
) -> None:
    """ """
    restaurant = model_factory(RestaurantModel, name="The Scrapyard")

    response = client.delete(f"/restaurants/{restaurant.id}")

    assert response.status_code == 200

    with pytest.raises(InvalidRequestError):
        session.refresh(restaurant)
