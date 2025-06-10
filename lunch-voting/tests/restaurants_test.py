from typing import Iterator, Protocol

import pytest

from fastapi.testclient import TestClient
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import select, delete
from sqlalchemy.orm.session import Session

from app.db.models.restaurants import RestaurantModel


pytestmark = pytest.mark.asyncio


class RestaurantFactory(Protocol):
    def __call__(self, name: str) -> RestaurantModel: ...


@pytest.fixture(scope="function")
def create_restaurant(session: Session) -> RestaurantFactory:
    def _create_restaurant(name: str) -> RestaurantModel:
        restaurant = RestaurantModel(name=name)
        session.add(restaurant)
        session.commit()

        return restaurant

    return _create_restaurant


@pytest.fixture(scope="function", autouse=True)
def delete_all_restaurants(session: Session) -> Iterator[None]:
    """ """
    yield

    session.execute(delete(RestaurantModel))
    session.commit()


def fetch_restaurant(name: str, session: Session) -> RestaurantModel | None:
    """ """
    query = select(RestaurantModel).where(RestaurantModel.name == name)
    return session.execute(query).scalars().one_or_none()


async def test_create_restaurant(client: TestClient, session: Session) -> None:
    """ """
    # async with client:
    #     response = await client.post("/restaurants", json={"name": "The Scrapyard"})
    #     assert response.status_code == 201

    response = client.post("/restaurants", json={"name": "The Scrapyard"})

    assert response.status_code == 201

    restaurant = fetch_restaurant("The Scrapyard", session)

    assert restaurant is not None


def test_update_restaurant(
    client: TestClient, create_restaurant: RestaurantFactory, session: Session
) -> None:
    """ """
    restaurant = create_restaurant("The Scrapyard")

    response = client.put(f"/restaurants/{restaurant.id}", json={"name": "Can Andres"})

    assert response.status_code == 200

    session.refresh(restaurant)

    assert restaurant.name == "Can Andres"


def test_get_all_restaurants(client: TestClient, create_restaurant: RestaurantFactory) -> None:
    """ """
    create_restaurant("The Scrapyard")
    create_restaurant("Can Andres")
    create_restaurant("Burger King")

    response = client.get("/restaurants")

    assert response.status_code == 200
    assert len(response.json()) == 3


def test_delete_restaurant(
    client: TestClient, create_restaurant: RestaurantFactory, session: Session
) -> None:
    """ """
    restaurant = create_restaurant("The Scrapyard")

    response = client.delete(f"/restaurants/{restaurant.id}")

    assert response.status_code == 200

    with pytest.raises(InvalidRequestError):
        session.refresh(restaurant)
