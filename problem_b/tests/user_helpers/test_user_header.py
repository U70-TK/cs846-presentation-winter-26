"""
Tests for GET /users/{user_id}/header
"""


class TestFormatUserForHeader:
    """Endpoint: GET /users/{user_id}/header"""

    def test_admin_shows_role_in_parentheses(self, client):
        resp = client.get("/users/1/header")
        assert resp.status_code == 200
        assert resp.json()["display"] == "Jane Doe (admin)"

    def test_support_shows_role_in_parentheses(self, client):
        resp = client.get("/users/3/header")
        assert resp.status_code == 200
        assert resp.json()["display"] == "Alice Wong (support)"

    def test_regular_user_shows_name_only(self, client):
        resp = client.get("/users/2/header")
        assert resp.status_code == 200
        assert resp.json()["display"] == "John Smith"

    def test_another_regular_user(self, client):
        resp = client.get("/users/4/header")
        assert resp.status_code == 200
        assert resp.json()["display"] == "Bob Martin"

    def test_404_for_nonexistent_user(self, client):
        resp = client.get("/users/9999/header")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "User not found"

    def test_response_shape(self, client):
        resp = client.get("/users/1/header")
        body = resp.json()
        assert "display" in body
        assert isinstance(body["display"], str)
