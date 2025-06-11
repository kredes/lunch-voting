from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.connections import get_session

# Dependency-injected session
SessionDep = Annotated[Session, Depends(get_session)]
