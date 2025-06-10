from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from starlette import status

from app.config import JWT_SIGNING_KEY
from app.db import UserModel
from app.routers.dependencies.database import SessionDep


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_authenticated_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: SessionDep,
) -> UserModel:
    """
    Returns the user authenticated by the given token, if valid.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, JWT_SIGNING_KEY, algorithms=["HS256"])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception

    except InvalidTokenError:
        raise credentials_exception

    user = UserModel.get_by_username(username, session)
    if user is None:
        raise credentials_exception

    return user
