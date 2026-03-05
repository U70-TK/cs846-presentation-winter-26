"""
Tests for GET /users/{user_id}/display
"""


class TestGetUserDisplay:
    """Endpoint: GET /users/{user_id}/display"""

    def test_requires_bearer_token(self, unauthenticated_client):
        resp = unauthenticated_client.get("/users/1/display")
        assert resp.status_code == 401

    def test_returns_name_and_email_for_valid_user(self, client):
        resp = client.get("/users/1/display")
        assert resp.status_code == 200
        body = resp.json()
        assert body["name"] == "Jane Doe"
        assert body["email"] == "jane.doe@example.com"

    def test_returns_second_user(self, client):
        resp = client.get("/users/2/display")
        assert resp.status_code == 200
        body = resp.json()
        assert body["name"] == "John Smith"
        assert body["email"] == "john.smith@example.com"

    def test_404_for_nonexistent_user(self, client):
        resp = client.get("/users/9999/display")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "User not found"

    def test_response_has_no_id_field(self, client):
        """Ensure internal IDs are not leaked via this endpoint."""
        resp = client.get("/users/1/display")
        body = resp.json()
        assert "id" not in body

    def test_response_has_no_role_field(self, client):
        resp = client.get("/users/1/display")
        body = resp.json()
        assert "role" not in body
