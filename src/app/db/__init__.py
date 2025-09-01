from app.db.models.base import DatabaseModel

__all__ = ["DatabaseModel", "RestaurantModel", "UserModel", "VoteModel"]

from app.db.models.restaurants import RestaurantModel
from app.db.models.users import UserModel
from app.db.models.votes import VoteModel
