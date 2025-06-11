from datetime import timedelta, date
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.sql.expression import select, text

from app.config import VOTES_PER_USER
from app.db import UserModel, RestaurantModel, VoteModel
from app.routers.dependencies.database import SessionDep
from app.routers.dependencies.users import get_authenticated_user
from app.routers.models.restaurants import Restaurant
from app.routers.models.voting import GetWinnerQueryParams

router = APIRouter(tags=["voting"])


@router.post("/vote", status_code=200)
def cast_vote(
    restaurant_id: int,
    current_user: Annotated[UserModel, Depends(get_authenticated_user)],
    session: SessionDep,
) -> None:
    """
    Cast a vote from the currently logged-in user to the given restaurant.
    """
    restaurant = session.get(RestaurantModel, restaurant_id)

    if restaurant is None:
        raise HTTPException(status_code=404, detail=f"Restaurant {restaurant_id} not found")

    today = date.today()
    tomorrow = today + timedelta(days=1)

    # Votes cast by the user today
    user_votes_query = select(VoteModel).where(
        (VoteModel.user_id == current_user.id)
        & (VoteModel.created >= today)
        & (VoteModel.created < tomorrow)
    )
    user_votes = session.scalars(user_votes_query).fetchall()

    # Has the user already voted for this restaurant today?
    if any(vote.restaurant_id == restaurant.id for vote in user_votes):
        raise HTTPException(
            status_code=400, detail="Cannot vote for the same restaurant multiple times"
        )

    # Has the user reached their daily vote limit?
    if len(user_votes) >= VOTES_PER_USER:
        raise HTTPException(status_code=400, detail="User reached vote limit")

    match len(user_votes):
        case 0:
            weight = Decimal(1)
        case 1:
            weight = Decimal(0.5)
        case _:
            weight = Decimal(0.25)

    vote = VoteModel(user_id=current_user.id, restaurant_id=restaurant.id, weight=weight)
    session.add(vote)
    session.commit()


@router.get("/winner", dependencies=[Depends(get_authenticated_user)])
def get_chosen_restaurant(
    params: Annotated[GetWinnerQueryParams, Query()], session: SessionDep
) -> Restaurant:
    """
    Returns the winner restaurant at the given date. If date is omitted, returns the winner at
    the current time. If there is no winner for the given date, returns a 404 error.
    """
    start_date = params.date or date.today()
    end_date = start_date + timedelta(days=1)

    chosen_restaurant_id_query = text(
        """
        SELECT restaurant_id
        FROM votes
        WHERE created >= :start_date AND created < :end_date
        GROUP BY restaurant_id
        ORDER BY sum(weight) DESC, count(DISTINCT user_id) DESC
        LIMIT 1
        """
    )

    chosen_restaurant_query = select(RestaurantModel).where(
        RestaurantModel.id.in_(chosen_restaurant_id_query)
    )

    chosen_restaurant = (
        session.execute(chosen_restaurant_query, {"start_date": start_date, "end_date": end_date})
        .scalars()
        .one_or_none()
    )

    # No votes have been cast on the given date
    if chosen_restaurant is None:
        raise HTTPException(status_code=404, detail="No winner found")

    return Restaurant.model_validate(chosen_restaurant)
