from datetime import timedelta, date, datetime, time
from decimal import Decimal
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy.orm.session import Session

from app.db import UserModel, RestaurantModel, VoteModel
from .conftest import ModelFactory, one_or_none


def test_vote_for_valid_restaurant(
    user: UserModel, restaurant: RestaurantModel, client: TestClient, session: Session
) -> None:
    """
    Tests casting a valid vote.
    """
    response = client.post("/vote", params={"restaurant_id": restaurant.id})

    assert response.status_code == 200

    vote = one_or_none(VoteModel, session, user_id=user.id, restaurant_id=restaurant.id)

    assert vote is not None
    assert vote.weight == Decimal(1)


def test_voting_for_invalid_restaurant(
    user: UserModel, restaurant: RestaurantModel, client: TestClient
) -> None:
    """
    Tests casting an invalid vote.
    """
    response = client.post("/vote", params={"restaurant_id": -1})

    assert response.status_code == 404


def test_cannot_vote_multiple_times_for_same_restaurant(
    user: UserModel, restaurant: RestaurantModel, client: TestClient
) -> None:
    """
    Tests that a user cannot vote for the same restaurant twice.
    """
    response = client.post("/vote", params={"restaurant_id": restaurant.id})
    assert response.status_code == 200

    response = client.post("/vote", params={"restaurant_id": restaurant.id})
    assert response.status_code == 400
    assert response.json() == {"detail": "Cannot vote for the same restaurant multiple times"}


def test_cannot_vote_more_times_than_the_daily_vote_limit(
    user: UserModel, restaurant: RestaurantModel, model_factory: ModelFactory, client: TestClient
) -> None:
    """
    Tests that a user cannot exceed its daily vote limit.
    """
    r1 = restaurant
    r2 = model_factory(RestaurantModel, name="McDonald's")
    r3 = model_factory(RestaurantModel, name="The Scrapyard")
    r4 = model_factory(RestaurantModel, name="GG Doner")

    response = client.post("/vote", params={"restaurant_id": r1.id})
    assert response.status_code == 200

    response = client.post("/vote", params={"restaurant_id": r2.id})
    assert response.status_code == 200

    response = client.post("/vote", params={"restaurant_id": r3.id})
    assert response.status_code == 200

    # We reached the vote limit for the day
    response = client.post("/vote", params={"restaurant_id": r4.id})
    assert response.status_code == 400
    assert response.json() == {"detail": "User reached vote limit"}

    # However, voting on a different day is just fine
    with patch("app.routers.voting.date") as date_mock:
        date_mock.today.return_value = date.today() + timedelta(days=7)
        # with freeze_time(date.today() + timedelta(days=7)):
        response = client.post("/vote", params={"restaurant_id": r4.id})
        assert response.status_code == 200


def test_vote_weights(
    user: UserModel,
    restaurant: RestaurantModel,
    model_factory: ModelFactory,
    client: TestClient,
    session: Session,
) -> None:
    """ """
    r1 = restaurant
    r2 = model_factory(RestaurantModel, name="McDonald's")
    r3 = model_factory(RestaurantModel, name="The Scrapyard")

    def vote_and_assert_weight(restaurant: RestaurantModel, expected_weight: Decimal) -> None:
        response = client.post("/vote", params={"restaurant_id": restaurant.id})
        assert response.status_code == 200

        vote = one_or_none(VoteModel, session, user_id=user.id, restaurant_id=restaurant.id)
        assert vote
        assert vote.weight == expected_weight

    # First vote has a weight of 1
    vote_and_assert_weight(r1, Decimal(1))

    # Second vote has a weight of 0.5
    vote_and_assert_weight(r2, Decimal(0.5))

    # Subsequent votes have a weight of 0.25
    vote_and_assert_weight(r3, Decimal(0.25))


def test_get_winner_on_current_date(
    user: UserModel, restaurant: RestaurantModel, model_factory: ModelFactory, client: TestClient
) -> None:
    """ """
    user_2 = model_factory(UserModel, username="anne", password_hash=b"z9g7w6h58isw")
    restaurant_2 = model_factory(RestaurantModel, name="McDonald's")

    model_factory(VoteModel, user_id=user.id, restaurant_id=restaurant.id, weight=Decimal(1))
    model_factory(VoteModel, user_id=user_2.id, restaurant_id=restaurant.id, weight=Decimal(1))
    model_factory(VoteModel, user_id=user_2.id, restaurant_id=restaurant_2.id, weight=Decimal(0.5))

    response = client.get("/winner")
    assert response.status_code == 200
    assert response.json()["id"] == restaurant.id


def test_get_weight_tie_winner(
    user: UserModel, restaurant: RestaurantModel, model_factory: ModelFactory, client: TestClient
) -> None:
    """ """
    user_2 = model_factory(UserModel, username="anne", password_hash=b"z9g7w6h58isw")
    restaurant_2 = model_factory(RestaurantModel, name="McDonald's")

    model_factory(VoteModel, user_id=user.id, restaurant_id=restaurant.id, weight=Decimal(1))
    model_factory(VoteModel, user_id=user.id, restaurant_id=restaurant_2.id, weight=Decimal(0.5))
    model_factory(VoteModel, user_id=user_2.id, restaurant_id=restaurant_2.id, weight=Decimal(0.5))

    response = client.get("/winner")
    assert response.status_code == 200
    assert response.json()["id"] == restaurant_2.id


def test_get_winner_on_past_date(
    user: UserModel, restaurant: RestaurantModel, model_factory: ModelFactory, client: TestClient
) -> None:
    """ """
    last_week = date.today() - timedelta(days=7)
    vote_moment = datetime.combine(last_week, time(12, 25))

    user_2 = model_factory(UserModel, username="anne", password_hash=b"z9g7w6h58isw")
    restaurant_2 = model_factory(RestaurantModel, name="McDonald's")

    # Three votes cast on the same day, one week ago
    model_factory(
        VoteModel,
        user_id=user.id,
        restaurant_id=restaurant.id,
        weight=Decimal(1),
        created=vote_moment,
    )
    model_factory(
        VoteModel,
        user_id=user_2.id,
        restaurant_id=restaurant.id,
        weight=Decimal(1),
        created=vote_moment,
    )
    model_factory(
        VoteModel,
        user_id=user_2.id,
        restaurant_id=restaurant_2.id,
        weight=Decimal(0.5),
        created=vote_moment,
    )

    response = client.get("/winner", params={"date": last_week.isoformat()})
    assert response.status_code == 200
    assert response.json()["id"] == restaurant.id


def get_winner_on_invalid_date(client: TestClient) -> None:
    """ """
    invalid_date = date.today() + timedelta(days=7)

    response = client.get("/winner", params={"date": invalid_date.isoformat()})
    assert response.status_code == 404
    assert response.json()["detail"] == "No winner found"
