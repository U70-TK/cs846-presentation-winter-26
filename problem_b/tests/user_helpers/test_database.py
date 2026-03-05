"""
Tests for the database module (database.py) and seed script (seed.py).

These tests use tmp_path for a real file-based SQLite DB and override
the autouse _patch_db fixture so they test actual init_db / seed logic.
"""

import sqlite3
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import database
from seed import seed_users, SEED_USERS


class TestInitDb:
    """database.init_db() schema creation."""

    @pytest.fixture(autouse=True)
    def _patch_db(self):
        """Override the conftest autouse fixture – do nothing."""
        yield

    def test_creates_users_table(self, tmp_path, monkeypatch):
        db_path = str(tmp_path / "test.db")
        monkeypatch.setattr(database, "DB_PATH", db_path)

        database.init_db()

        conn = sqlite3.connect(db_path)
        cur = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
        )
        assert cur.fetchone() is not None
        conn.close()

    def test_idempotent(self, tmp_path, monkeypatch):
        db_path = str(tmp_path / "test.db")
        monkeypatch.setattr(database, "DB_PATH", db_path)

        database.init_db()
        database.init_db()  # should not raise


class TestGetDbConnection:
    """database.get_db_connection() returns a usable connection."""

    @pytest.fixture(autouse=True)
    def _patch_db(self):
        """Override the conftest autouse fixture – do nothing."""
        yield

    def test_row_factory_set(self, tmp_path, monkeypatch):
        db_path = str(tmp_path / "test.db")
        monkeypatch.setattr(database, "DB_PATH", db_path)
        database.init_db()

        conn = database.get_db_connection()
        assert conn.row_factory is sqlite3.Row
        conn.close()


class TestSeedScript:
    """seed.py populates the database correctly."""

    @pytest.fixture(autouse=True)
    def _patch_db(self):
        """Override the conftest autouse fixture – do nothing."""
        yield

    def test_inserts_all_seed_users(self, tmp_path, monkeypatch):
        db_path = str(tmp_path / "test.db")
        monkeypatch.setattr(database, "DB_PATH", db_path)

        seed_users()

        conn = sqlite3.connect(db_path)
        count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        conn.close()
        assert count == len(SEED_USERS)

    def test_idempotent_no_duplicates(self, tmp_path, monkeypatch):
        db_path = str(tmp_path / "test.db")
        monkeypatch.setattr(database, "DB_PATH", db_path)

        seed_users()
        seed_users()  # run again

        conn = sqlite3.connect(db_path)
        count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        conn.close()
        assert count == len(SEED_USERS)
