"""
Tests for GET /users/lookup?email=...
"""


class TestLookupByEmail:
    """Endpoint: GET /users/lookup"""

    def test_returns_user_id_for_known_email(self, client):
        resp = client.get("/users/lookup", params={"email": "jane.doe@example.com"})
        assert resp.status_code == 200
        assert resp.json()["user_id"] == 1

    def test_returns_correct_id_for_another_user(self, client):
        resp = client.get(
            "/users/lookup", params={"email": "alice.wong@example.com"}
        )
        assert resp.status_code == 200
        assert resp.json()["user_id"] == 3

    def test_returns_null_for_unknown_email(self, client):
        resp = client.get(
            "/users/lookup", params={"email": "nobody@example.com"}
        )
        assert resp.status_code == 200
        assert resp.json()["user_id"] is None

    def test_missing_email_param_returns_422(self, client):
        resp = client.get("/users/lookup")
        assert resp.status_code == 422  # FastAPI validation error
