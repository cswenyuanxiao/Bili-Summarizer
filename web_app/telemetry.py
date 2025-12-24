from typing import Optional

from .db import get_connection, using_postgres


def _get_connection():
    return get_connection()


def init_telemetry_db():
    conn = _get_connection()
    cursor = conn.cursor()
    if using_postgres():
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS failure_events (
                id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                user_id TEXT,
                code TEXT NOT NULL,
                stage TEXT NOT NULL,
                detail TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)\n    else:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS failure_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                code TEXT NOT NULL,
                stage TEXT NOT NULL,
                detail TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
    conn.commit()
    conn.close()


def record_failure(user_id: Optional[str], code: str, stage: str, detail: str = ""):
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO failure_events (user_id, code, stage, detail)
        VALUES (?, ?, ?, ?)
    """, (user_id, code, stage, detail))
    conn.commit()
    conn.close()


init_telemetry_db()
