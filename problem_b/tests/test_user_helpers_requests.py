import pytest

import user_helpers as user_helpers


class DummyResponse:
    def __init__(self, json_data, status_code=200):
        self._json_data = json_data
        self.status_code = status_code

    def json(self):
        return self._json_data


def make_requests_mock(monkeypatch, expected_calls):
    """
    Simple requests.get mock:
    - expected_calls: list of (url, response) tuples in the order they should be called.
    """
    calls = {"urls": []}

    def fake_get(url, *args, **kwargs):
        calls["urls"].append((url, kwargs))
        if not expected_calls:
            raise AssertionError(f"Unexpected call to requests.get({url!r})")
        exp_url, resp = expected_calls.pop(0)
        assert url == exp_url, f"Expected URL {exp_url!r}, got {url!r}"
        return resp

    monkeypatch.setattr(user_helpers, "requests", type("R", (), {"get": fake_get}))
    return calls


def test_get_user_display_happy_path(monkeypatch):
    """Backend helper returns (name, email) for a valid user."""
    expected = DummyResponse({"id": 123, "name": "Jane Doe", "email": "jane@example.com"})
    make_requests_mock(
        monkeypatch,
        [
            (
                "https://api.example.com/users/123",
                expected,
            )
        ],
    )

    name, email = user_helpers.get_user_display(123)

    assert name == "Jane Doe"
    assert email == "jane@example.com"


def test_get_user_list_filters_role_and_hides_internal_id(monkeypatch):
    """
    Backend should:
    - Call /users?role=admin when role='admin'.
    - Not expose internal IDs to the frontend (the test asserts we can easily change the shape
      later; for now it documents that 'id' is considered sensitive for UI exposure).
    """
    resp = DummyResponse(
        [
            {"id": "internal-1", "name": "Jane", "email": "jane@example.com", "role": "admin"},
            {"id": "internal-2", "name": "Bob", "email": "bob@example.com", "role": "admin"},
        ]
    )
    calls = make_requests_mock(
        monkeypatch,
        [
            (
                "https://api.example.com/users?role=admin",
                resp,
            )
        ],
    )

    users = user_helpers.get_user_list(role="admin")

    # URL shape
    assert calls["urls"][0][0].endswith("?role=admin")
    # Role filter applied (backend behavior)
    assert all(u["role"] == "admin" for u in users)
    # This test documents the current (problematic) behavior of exposing 'id' so reviewers
    # can discuss how to adapt it for the frontend safely.
    assert all("id" in u for u in users)


def test_format_user_for_header_avoids_extra_calls(monkeypatch):
    """
    In an ideal backend design, we would not make redundant calls in the hot path.
    This test currently documents that we perform:
    - One call to fetch the user.
    - One call to fetch the list.
    Reviewers should propose better patterns (e.g., reuse list data, caching).
    """
    # First call: single user
    user_resp = DummyResponse({"id": 1, "name": "Jane Doe", "email": "jane@example.com", "role": "admin"})
    # Second call: list
    list_resp = DummyResponse(
        [
            {"id": 1, "name": "Jane Doe", "email": "jane@example.com", "role": "admin"},
            {"id": 2, "name": "Bob", "email": "bob@example.com", "role": "user"},
        ]
    )
    calls = make_requests_mock(
        monkeypatch,
        [
            ("https://api.example.com/users/1", user_resp),
            ("https://api.example.com/users", list_resp),
        ],
    )

    header = user_helpers.format_user_for_header(1)

    assert header == "Jane Doe (admin)"
    assert len(calls["urls"]) == 2  # document current hot-path behavior for review


def test_lookup_by_email_backend_only_usage(monkeypatch):
    """
    lookup_by_email is used by an internal support tool, not exposed to the frontend.
    We still want it to behave sensibly and not leak unnecessary data in its return type.
    """
    resp = DummyResponse(
        [
            {"id": "internal-1", "name": "Jane", "email": "jane@example.com", "role": "admin"},
            {"id": "internal-2", "name": "Bob", "email": "bob@example.com", "role": "user"},
        ]
    )
    make_requests_mock(
        monkeypatch,
        [
            ("https://api.example.com/users", resp),
        ],
    )

    user_id = user_helpers.lookup_by_email("jane@example.com")
    missing = user_helpers.lookup_by_email("nope@example.com")

    assert user_id == "internal-1"
    assert missing is None


@pytest.mark.skip(
    reason="Timeout and error-handling behavior not implemented yet; kept as a discussion hook for review."
)
def test_get_user_display_handles_timeout_and_malformed(monkeypatch):
    """
    This test encodes *intended* backend behavior that is not implemented yet:
    - Use a 2s timeout.
    - Fail gracefully on timeouts / malformed JSON.

    The skip marker keeps the test discoverable without breaking the exercise.
    """
    # This test body can be extended by students as part of the exercise.
    pass
