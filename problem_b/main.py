"""
Auth API with login and /me endpoints.
"""

from contextlib import asynccontextmanager

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel

import auth
import user_helpers
from database import get_db_connection, init_db
from seed import seed_users


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    seed_users()
    yield


app = FastAPI(title="Auth Service", version="1.0.0", lifespan=lifespan)
app.include_router(user_helpers.router)


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class MeResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str


@app.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    conn = get_db_connection()
    try:
        row = conn.execute(
            """
            SELECT id, email, password_hash
            FROM users
            WHERE email = ?
            """,
            (payload.email,),
        ).fetchone()
    finally:
        conn.close()

    if not row or not auth.verify_password(payload.password, row["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = auth.create_access_token(user_id=row["id"], email=row["email"])
    return LoginResponse(
        access_token=token,
        expires_in=auth.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@app.get("/me", response_model=MeResponse)
def me(current_user: dict = Depends(auth.get_current_user)) -> MeResponse:
    return MeResponse(**current_user)


def main() -> None:
    uvicorn.run("main:app", host="0.0.0.0", port=4000, reload=True)


if __name__ == "__main__":
    main()
