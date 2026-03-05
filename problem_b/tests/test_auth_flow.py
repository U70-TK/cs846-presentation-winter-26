import os
import sqlite3
import sys
from datetime import datetime, timedelta, timezone

import jwt
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import auth
from database import get_db_path, init_db
from seed import SEED_USERS, seed_users

pytestmark = pytest.mark.usefixtures("auth_env")


def test_schema_and_seed_data_created():
    init_db()
    inserted = seed_users()
    assert inserted == len(SEED_USERS)

    conn = sqlite3.connect(get_db_path())
    try:
        count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    finally:
        conn.close()
    assert count == len(SEED_USERS)


def test_seed_is_idempotent():
    init_db()
    seed_users()
    inserted_again = seed_users()
    assert inserted_again == 0


def test_login_success_returns_bearer_token_and_30_min_expiry(client):
    target = SEED_USERS[0]
    resp = client.post(
        "/login",
        json={"email": target["email"], "password": target["password"]},
    )
    assert resp.status_code == 200
    body = resp.json()

    assert body["token_type"] == "bearer"
    assert isinstance(body["access_token"], str)
    assert body["expires_in"] == 30 * 60

    payload = jwt.decode(
        body["access_token"],
        auth.get_jwt_secret(),
        algorithms=[auth.ALGORITHM],
        options={"verify_exp": False},
    )
    assert payload["exp"] - payload["iat"] == 30 * 60


def test_login_rejects_invalid_password(client):
    target = SEED_USERS[0]
    resp = client.post(
        "/login",
        json={"email": target["email"], "password": "wrong-password"},
    )
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid email or password"


def test_login_rejects_unknown_user(client):
    resp = client.post(
        "/login",
        json={"email": "missing@example.com", "password": "does-not-matter"},
    )
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid email or password"


def test_me_returns_current_user_profile(client):
    target = SEED_USERS[1]
    login = client.post(
        "/login",
        json={"email": target["email"], "password": target["password"]},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]

    resp = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] > 0
    assert data["email"] == target["email"]
    assert data["full_name"] == target["full_name"]
    assert data["role"] == target["role"]


def test_me_requires_bearer_token(client):
    resp = client.get("/me")
    assert resp.status_code == 401


def test_me_rejects_expired_token(client):
    now = datetime.now(timezone.utc)
    expired_payload = {
        "sub": "1",
        "email": "admin@example.com",
        "iat": int((now - timedelta(minutes=35)).timestamp()),
        "exp": int((now - timedelta(minutes=5)).timestamp()),
    }
    expired_token = jwt.encode(
        expired_payload,
        auth.get_jwt_secret(),
        algorithm=auth.ALGORITHM,
    )

    resp = client.get("/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid or expired token"
