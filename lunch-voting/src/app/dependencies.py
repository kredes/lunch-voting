from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm.session import Session

from app.db.connections import get_session

SessionDep = Annotated[Session, Depends(get_session)]
