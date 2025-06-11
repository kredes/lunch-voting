from datetime import datetime, timedelta, timezone
from typing import Annotated

import bcrypt
import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm.session import Session

from app.config import Config
from app.db import UserModel
from app.routers.dependencies.database import SessionDep
from app.routers.models.users import AuthToken, CreateUserData, User
from app.routers.dependencies.users import get_authenticated_user

router = APIRouter(tags=["users"])


def is_password_valid(password: str, password_hash: bytes) -> bool:
    """
    Verifies that the provided password matches the known hash.
    """
    return bcrypt.checkpw(
        bytes(password, encoding="utf-8"),
        password_hash,
    )


def authenticate_user(username: str, password: str, session: Session) -> UserModel | None:
    """
    Returns user identified by username and password, if valid.
    """

    user = UserModel.get_by_username(username, session)

    if not user or not is_password_valid(password, user.password_hash):
        return None

    return user


def generate_user_access_token(user: UserModel):
    """
    Generates a JWT with the given user.
    """
    jwt_data = {
        "sub": user.username,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=Config.jwt_expiration_minutes),
    }

    encoded_jwt = jwt.encode(jwt_data, Config.jwt_signing_key, algorithm="HS256")

    return encoded_jwt


def hash_password(password: str) -> bytes:
    """
    Hashes the given password.

    Note: OWASP recommends using Argon2id or scrypt rather than bcrypt
        * https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
    """
    return bcrypt.hashpw(
        bytes(password, encoding="utf-8"),
        bcrypt.gensalt(),
    )


@router.post("/login", status_code=200)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep
) -> AuthToken:
    """
    Authenticates a user via username and password.

    Notes:
      - The OAuth password flow implemented here is deprecated, but I believe it's a good balance
      between complexity and being practical for a test task.
      - In a more complete implementation, a token refresh endpoint would be implemented as well,
      but is left out here for simplicity's sake.
      - Also left out of this implementation are scopes, for the same reason.
    """
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = generate_user_access_token(user)

    return AuthToken(access_token=access_token, token_type="bearer")


@router.get("/users/me/", status_code=200)
def get_current_user(
    logged_in_user: Annotated[UserModel, Depends(get_authenticated_user)],
) -> User:
    """
    Returns the logged in user.
    """
    return User.model_validate(logged_in_user)


@router.post("/users", status_code=201)
def create_user(data: CreateUserData, session: SessionDep) -> User:
    """
    Creates a new user.
    """
    user = UserModel(username=data.username, password_hash=hash_password(data.password))
    session.add(user)
    session.commit()

    return User.model_validate(user)
