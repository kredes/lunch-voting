from fastapi.testclient import TestClient
from sqlalchemy.orm.session import Session

from app.db import UserModel
from app.routers.users import hash_password
from ..conftest import ModelFactory


def test_create_user_with_valid_data(client: TestClient, session: Session) -> None:
    """
    Test creating a new user.
    """
    response = client.post(
        "/users",
        json={"username": "andres", "password": "not_very_secure"},
    )

    assert response.status_code == 201

    user = UserModel.get_by_username("andres", session)

    try:
        assert user is not None
        assert user.password_hash != "not_very_secure"
    finally:
        session.delete(user)
        session.commit()


def test_create_user_with_invalid_data_fails(client: TestClient, session: Session) -> None:
    """
    Test creating a new user with invalid data.
    """
    response = client.post(
        "/users",
        json={"username": "andres"},
    )

    assert response.status_code == 422


def test_login_with_valid_user(client: TestClient, model_factory: ModelFactory) -> None:
    """
    Tests login in with an existing user.
    """
    model_factory(UserModel, username="andres", password_hash=hash_password("not_very_secure"))

    response = client.post(
        "/login",
        data={"username": "andres", "password": "not_very_secure"},
    )
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["access_token"] is not None
    assert response_data["token_type"] == "bearer"


def test_login_with_fake_user_fails(client: TestClient, session: Session) -> None:
    """
    Tests login in with a user that does not exist.
    """
    response = client.post(
        "/login",
        data={"username": "i_dont_exist", "password": "not_very_secure"},
    )

    assert response.status_code == 401


def test_login_with_invalid_password_fails(client: TestClient, model_factory: ModelFactory) -> None:
    """
    Tests login in with an existing user and an invalid password.
    """
    model_factory(UserModel, username="andres", password_hash=hash_password("not_very_secure"))

    response = client.post(
        "/login",
        data={"username": "andres", "password": "wrong_password"},
    )

    assert response.status_code == 401
