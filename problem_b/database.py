"""
SQLite database connection and schema setup for user helpers + auth service.
"""

import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")


def get_db_path() -> str:
    return os.getenv("AUTH_DB_PATH", DB_PATH)


def get_db_connection() -> sqlite3.Connection:
    """Return a connection with row-factory enabled."""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL DEFAULT '',
            role TEXT NOT NULL DEFAULT 'user',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    columns = {
        row["name"] for row in conn.execute("PRAGMA table_info(users)").fetchall()
    }

    if "name" not in columns:
        conn.execute("ALTER TABLE users ADD COLUMN name TEXT")
    if "full_name" not in columns:
        conn.execute("ALTER TABLE users ADD COLUMN full_name TEXT NOT NULL DEFAULT ''")
    if "password_hash" not in columns:
        conn.execute(
            "ALTER TABLE users ADD COLUMN password_hash TEXT NOT NULL DEFAULT ''"
        )
    if "role" not in columns:
        conn.execute("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'user'")
    if "created_at" not in columns:
        conn.execute(
            "ALTER TABLE users ADD COLUMN created_at TEXT NOT NULL DEFAULT ''"
        )

    conn.execute(
        """
        UPDATE users
        SET full_name = COALESCE(NULLIF(full_name, ''), name, email)
        """
    )
    conn.execute(
        """
        UPDATE users
        SET name = COALESCE(NULLIF(name, ''), full_name)
        """
    )


def init_db() -> None:
    """Create or migrate the users table schema."""
    conn = get_db_connection()
    try:
        _ensure_schema(conn)
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
    print(f"Database initialised at {get_db_path()}")
