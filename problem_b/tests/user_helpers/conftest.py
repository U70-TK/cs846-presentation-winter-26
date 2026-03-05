"""
Shared pytest fixtures for the user_helpers backend tests.

Creates an isolated, in-memory SQLite database for every test so that
tests never touch the production `users.db` file and never leak state
between each other.
"""

import sys
import os
import sqlite3

import pytest

# Make sure `database` and `user_helpers` can be imported from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import auth  # noqa: E402  (after path manipulation)
import database  # noqa: E402  (after path manipulation)
from user_helpers import app  # noqa: E402

from fastapi.testclient import TestClient


# ── helpers ───────────────────────────────────────────────────────────────────

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name     TEXT    NOT NULL,
    full_name TEXT   NOT NULL,
    email    TEXT    NOT NULL UNIQUE,
    password_hash TEXT NOT NULL DEFAULT '',
    role     TEXT    NOT NULL DEFAULT 'user'
);
"""

SEED_ROWS = [
    ("Jane Doe", "Jane Doe", "jane.doe@example.com", "", "admin"),
    ("John Smith", "John Smith", "john.smith@example.com", "", "user"),
    ("Alice Wong", "Alice Wong", "alice.wong@example.com", "", "support"),
    ("Bob Martin", "Bob Martin", "bob.martin@example.com", "", "user"),
]


class _UnclosableConnection:
    """
    Thin wrapper around a real sqlite3.Connection that ignores .close()
    so the shared in-memory DB survives endpoint code that calls conn.close().
    """

    def __init__(self, real_conn: sqlite3.Connection):
        self._conn = real_conn

    def __getattr__(self, name):
        return getattr(self._conn, name)

    def close(self):  # noqa: D401
        """No-op – prevent endpoints from closing the shared test connection."""
        pass

    def really_close(self):
        self._conn.close()


def _create_test_db() -> _UnclosableConnection:
    """Return an in-memory SQLite connection seeded with test data."""
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute(SCHEMA_SQL)
    conn.executemany(
        """
        INSERT INTO users (name, full_name, email, password_hash, role)
        VALUES (?, ?, ?, ?, ?)
        """,
        SEED_ROWS,
    )
    conn.commit()
    return _UnclosableConnection(conn)


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def _patch_db(monkeypatch):
    """
    Monkey-patch `database.get_db_connection` so every call inside the
    FastAPI app returns a cursor on the same in-memory DB.
    """
    test_conn = _create_test_db()

    def _get_conn():
        return test_conn

    monkeypatch.setattr(database, "get_db_connection", _get_conn)
    monkeypatch.setattr(auth, "get_db_connection", _get_conn)
    monkeypatch.setenv("AUTH_JWT_SECRET", "test-secret-key-at-least-32-bytes-long")
    yield
    test_conn.really_close()


@pytest.fixture()
def admin_auth_header():
    token = auth.create_access_token(user_id=1, email="jane.doe@example.com")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def user_auth_header():
    token = auth.create_access_token(user_id=2, email="john.smith@example.com")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def client(admin_auth_header):
    """FastAPI TestClient wired to the patched database with admin auth."""
    with TestClient(app, headers=admin_auth_header) as test_client:
        yield test_client


@pytest.fixture()
def unauthenticated_client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def user_client(user_auth_header):
    with TestClient(app, headers=user_auth_header) as test_client:
        yield test_client
