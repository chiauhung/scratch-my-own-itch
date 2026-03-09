"""SQLite-backed session store.

Maps Slack thread_ts → ADK session_id.

Production equivalent: Firestore with TTL-based expiry and distributed access.
Gap: SQLite is single-process and has no TTL. In production, Firestore handles
multi-instance access and session expiry automatically.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path("data/sessions.db")


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                thread_ts  TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


def get_session_id(thread_ts: str) -> str | None:
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT session_id FROM sessions WHERE thread_ts = ?", (thread_ts,)
        ).fetchone()
    return row[0] if row else None


def upsert_session(thread_ts: str, session_id: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO sessions (thread_ts, session_id, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(thread_ts) DO UPDATE SET
                session_id = excluded.session_id,
                updated_at = CURRENT_TIMESTAMP
            """,
            (thread_ts, session_id),
        )
