from pathlib import Path
import sqlite3
from typing import Optional

DB_PATH = Path(__file__).resolve().parent.parent / "cache.db"


def _get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_telemetry_db():
    conn = _get_connection()
    cursor = conn.cursor()
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
