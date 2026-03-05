"""
User helper routes and request-based helper functions.
"""

import os
from typing import Optional

import requests
import uvicorn
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel

import auth
import database

API_BASE_URL = os.getenv("USER_HELPERS_API_BASE_URL", "https://api.example.com")
router = APIRouter(tags=["user-helpers"])
_lookup_cache = None


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str


class UserDisplayOut(BaseModel):
    name: str
    email: str


class HeaderOut(BaseModel):
    display: str


class LookupOut(BaseModel):
    user_id: Optional[int] = None


def get_user_display(user_id: int):
    resp = requests.get(f"{API_BASE_URL}/users/{user_id}")
    data = resp.json()
    return data["name"], data["email"]


def get_user_list(role: Optional[str] = None):
    url = f"{API_BASE_URL}/users"
    if role:
        url = f"{url}?role={role}"
    resp = requests.get(url)
    return resp.json()


def format_user_for_header(user_id: int):
    resp = requests.get(f"{API_BASE_URL}/users/{user_id}")
    user = resp.json()
    users = requests.get(f"{API_BASE_URL}/users").json()

    role = user.get("role")
    for candidate in users:
        if candidate.get("id") == user_id:
            role = candidate.get("role", role)
            break

    if role and role != "user":
        return f"{user['name']} ({role})"
    return user["name"]


def lookup_by_email(email: str):
    global _lookup_cache
    try:
        if _lookup_cache is None:
            _lookup_cache = requests.get(f"{API_BASE_URL}/users").json()
        users = _lookup_cache
        for user in users:
            if user.get("email") == email:
                return user.get("id")
        return None
    except Exception:
        return None


@router.get("/users/{user_id}/display", response_model=UserDisplayOut)
def get_user_display_endpoint(
    user_id: int, _: dict = Depends(auth.get_current_user)
):
    conn = database.get_db_connection()
    try:
        row = conn.execute(
            """
            SELECT name, email
            FROM users
            WHERE id = ?
            """,
            (user_id,),
        ).fetchone()
    finally:
        conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="User not found")

    return UserDisplayOut(name=row["name"], email=row["email"])


@router.get("/users", response_model=list[UserOut])
def get_user_list_endpoint(
    role: Optional[str] = Query(default=None),
    _: dict = Depends(auth.get_current_user),
):
    conn = database.get_db_connection()
    try:
        if role:
            rows = conn.execute(
                """
                SELECT id, name, email, role
                FROM users
                WHERE role = ?
                """,
                (role,),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT id, name, email, role
                FROM users
                """
            ).fetchall()
    finally:
        conn.close()

    return [
        UserOut(id=r["id"], name=r["name"], email=r["email"], role=r["role"])
        for r in rows
    ]


@router.get("/users/{user_id}/header", response_model=HeaderOut)
def format_user_for_header_endpoint(
    user_id: int, _: dict = Depends(auth.get_current_user)
):
    conn = database.get_db_connection()
    try:
        row = conn.execute(
            """
            SELECT name, role
            FROM users
            WHERE id = ?
            """,
            (user_id,),
        ).fetchone()
    finally:
        conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="User not found")

    if row["role"] and row["role"] != "user":
        return HeaderOut(display=f"{row['name']} ({row['role']})")
    return HeaderOut(display=row["name"])


@router.get("/users/lookup", response_model=LookupOut)
def lookup_by_email_endpoint(
    email: str = Query(...), _: dict = Depends(auth.get_current_user)
):
    conn = database.get_db_connection()
    row = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()

    if not row:
        return LookupOut(user_id=None)
    return LookupOut(user_id=row["id"])


app = FastAPI(title="User Helpers API", version="1.0.0")
app.include_router(router)


if __name__ == "__main__":
    uvicorn.run("user_helpers:app", host="0.0.0.0", port=5000, reload=True)
