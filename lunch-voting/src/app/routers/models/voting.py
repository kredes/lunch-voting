import datetime

from pydantic import BaseModel


class GetWinnerQueryParams(BaseModel):
    date: datetime.date | None = None
