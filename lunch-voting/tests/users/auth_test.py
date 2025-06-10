def test_all_endpoints_are_only_accessible_by_logged_in_users() -> None:
    """
    Tests that all endpoints besides creating a new user are only accessible by users with a
    valid access token.
    """
