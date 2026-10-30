import sqlite3
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "ghosttext.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                filename TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                risk_level TEXT NOT NULL,
                findings_count INTEGER NOT NULL,
                characters_analyzed INTEGER NOT NULL,
                analyzed_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(analysis_history)"
            ).fetchall()
        }

        if "user_id" not in columns:
            connection.execute(
                "ALTER TABLE analysis_history ADD COLUMN user_id INTEGER "
                "REFERENCES users(id)"
            )


def create_user(username: str, password_hash: str):
    created_at = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        cursor = connection.execute("""
            INSERT INTO users (username, password_hash, created_at)
            VALUES (?, ?, ?)
        """, (username, password_hash, created_at))

        return cursor.lastrowid


def get_user_by_username(username: str):
    with get_connection() as connection:
        row = connection.execute("""
            SELECT id, username, password_hash, created_at
            FROM users
            WHERE username = ?
        """, (username,)).fetchone()

        return dict(row) if row else None


def get_user_by_id(user_id: int):
    with get_connection() as connection:
        row = connection.execute("""
            SELECT id, username, created_at
            FROM users
            WHERE id = ?
        """, (user_id,)).fetchone()

        return dict(row) if row else None


def save_analysis(
    user_id: int,
    filename: str,
    file_size: int,
    risk_level: str,
    findings_count: int,
    characters_analyzed: int
):
    analyzed_at = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        cursor = connection.execute("""
            INSERT INTO analysis_history (
                user_id,
                filename,
                file_size,
                risk_level,
                findings_count,
                characters_analyzed,
                analyzed_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            filename,
            file_size,
            risk_level,
            findings_count,
            characters_analyzed,
            analyzed_at
        ))

        return cursor.lastrowid


def get_history(user_id: int, limit: int = 50):
    limit = max(1, min(limit, 100))

    with get_connection() as connection:
        rows = connection.execute("""
            SELECT *
            FROM analysis_history
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
        """, (user_id, limit)).fetchall()

        return [dict(row) for row in rows]


def clear_history(user_id: int):
    with get_connection() as connection:
        connection.execute(
            "DELETE FROM analysis_history WHERE user_id = ?",
            (user_id,)
        )
