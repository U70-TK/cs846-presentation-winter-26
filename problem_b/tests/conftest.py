import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from main import app


@pytest.fixture()
def auth_env(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTH_DB_PATH", str(tmp_path / "test_auth.db"))
    monkeypatch.setenv(
        "AUTH_JWT_SECRET",
        "test-secret-key-at-least-32-bytes-long",
    )


@pytest.fixture()
def client(auth_env):
    with TestClient(app) as test_client:
        yield test_client
