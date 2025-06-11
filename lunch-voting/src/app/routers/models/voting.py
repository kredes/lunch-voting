import datetime

from pydantic import BaseModel


class GetWinnerQueryParams(BaseModel):
    """
    Query parameters for the `/winner` endpoint.

    Even though it's only one field, it's defined here to avoid typing conflicts with `date`.
    """

    date: datetime.date | None = None
