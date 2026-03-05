"""
Seed users for local development/testing.
"""

from argon2 import PasswordHasher

from database import get_db_connection, init_db

SEED_USERS = [
    {
        "email": "admin@example.com",
        "password": "admin-pass-123",
        "full_name": "Admin User",
        "role": "admin",
    },
    {
        "email": "support@example.com",
        "password": "support-pass-123",
        "full_name": "Support User",
        "role": "support",
    },
    {
        "email": "user@example.com",
        "password": "user-pass-123",
        "full_name": "Regular User",
        "role": "user",
    },
    {"name": "Jane Doe", "email": "jane.doe@example.com", "role": "admin"},
    {"name": "John Smith", "email": "john.smith@example.com", "role": "user"},
    {"name": "Alice Wong", "email": "alice.wong@example.com", "role": "support"},
    {"name": "Bob Martin", "email": "bob.martin@example.com", "role": "user"},
    {
        "name": "Carlos Rivera",
        "email": "carlos.rivera@example.com",
        "role": "admin",
    },
    {
        "name": "Diana Patel",
        "email": "diana.patel@example.com",
        "role": "support",
    },
    {"name": "Eve Torres", "email": "eve.torres@example.com", "role": "user"},
    {"name": "Frank Lee", "email": "frank.lee@example.com", "role": "user"},
    {"name": "Grace Kim", "email": "grace.kim@example.com", "role": "admin"},
    {"name": "Hiro Tanaka", "email": "hiro.tanaka@example.com", "role": "user"},
]


def _default_password(email: str) -> str:
    local_part = email.split("@", 1)[0]
    return f"{local_part}-pass-123"


def _normalize_user(raw: dict) -> dict:
    full_name = raw.get("full_name") or raw.get("name") or raw["email"]
    name = raw.get("name") or full_name
    return {
        "email": raw["email"],
        "password": raw.get("password") or _default_password(raw["email"]),
        "full_name": full_name,
        "name": name,
        "role": raw.get("role", "user"),
    }


def seed_users() -> int:
    init_db()
    hasher = PasswordHasher()
    conn = get_db_connection()
    inserted = 0
    try:
        existing_emails = {
            row["email"] for row in conn.execute("SELECT email FROM users").fetchall()
        }

        for raw_user in SEED_USERS:
            user = _normalize_user(raw_user)
            if user["email"] in existing_emails:
                continue

            conn.execute(
                """
                INSERT INTO users (email, password_hash, full_name, name, role)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    user["email"],
                    hasher.hash(user["password"]),
                    user["full_name"],
                    user["name"],
                    user["role"],
                ),
            )
            inserted += 1

        conn.commit()
        return inserted
    finally:
        conn.close()


if __name__ == "__main__":
    created = seed_users()
    print(f"Seed complete: {created} user(s) inserted.")
