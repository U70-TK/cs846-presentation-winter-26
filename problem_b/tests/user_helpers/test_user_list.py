"""
Tests for GET /users  (user list, with optional role filter)
"""


class TestGetUserList:
    """Endpoint: GET /users"""

    def test_requires_bearer_token(self, unauthenticated_client):
        resp = unauthenticated_client.get("/users")
        assert resp.status_code == 401

    def test_returns_all_seeded_users(self, client):
        resp = client.get("/users")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 4  # 4 seed rows in conftest

    def test_each_user_has_required_fields(self, client):
        resp = client.get("/users")
        for u in resp.json():
            assert "id" in u
            assert "name" in u
            assert "email" in u
            assert "role" in u

    def test_filter_by_admin_role(self, client):
        resp = client.get("/users", params={"role": "admin"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["name"] == "Jane Doe"
        assert data[0]["role"] == "admin"

    def test_filter_by_support_role(self, client):
        resp = client.get("/users", params={"role": "support"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["name"] == "Alice Wong"

    def test_filter_by_user_role(self, client):
        resp = client.get("/users", params={"role": "user"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        names = {u["name"] for u in data}
        assert names == {"John Smith", "Bob Martin"}

    def test_filter_nonexistent_role_returns_empty(self, client):
        resp = client.get("/users", params={"role": "nonexistent"})
        assert resp.status_code == 200
        assert resp.json() == []

    def test_no_filter_returns_all(self, client):
        resp = client.get("/users")
        assert resp.status_code == 200
        assert len(resp.json()) == 4
