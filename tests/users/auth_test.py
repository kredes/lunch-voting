from dataclasses import dataclass

from fastapi.testclient import TestClient


@dataclass
class RouteTest:
    route: str
    method: str
    body: str | None = None


ROUTES_TESTS = [
    RouteTest("/users/me", "GET"),
    RouteTest("/restaurants", "GET"),
    RouteTest("/restaurants", "POST"),
    RouteTest("/restaurants/1", "PUT"),
    RouteTest("/restaurants/1", "DELETE"),
    RouteTest("/vote", "POST"),
    RouteTest("/winner", "GET"),
]


def test_endpoints_are_not_accessible_by_not_logged_in_users(
    unauthenticated_client: TestClient,
) -> None:
    """
    Tests that all endpoints besides creating a new user and login are not accessible by users
    without a
    valid access token.

    This is a very simple test that checks whether we get a 401 (unauthorized) response.
    """
    for route in ROUTES_TESTS:
        response = unauthenticated_client.request(route.method, route.route)
        assert response.status_code == 401


def test_endpoints_are_accessible_by_logged_in_users(client: TestClient) -> None:
    """
    Tests that all endpoints besides creating a new user and login are accessible by users with a
    valid access token.

    This is a very simple test that checks whether we get anything besides a 401 (unauthorized)
    response.
    """
    for route in ROUTES_TESTS:
        response = client.request(route.method, route.route)
        assert response.status_code != 401
