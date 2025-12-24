from typing import Optional, Dict

from .db import get_connection, using_postgres
INITIAL_CREDITS = 30
FIRST_SUMMARY_BONUS = 10


def _get_connection():
    return get_connection()


def init_credits_db():
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_credits (
            user_id TEXT PRIMARY KEY,
            credits INTEGER NOT NULL DEFAULT 0,
            total_used INTEGER NOT NULL DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    id_type = "SERIAL PRIMARY KEY" if using_postgres() else "INTEGER PRIMARY KEY AUTOINCREMENT"
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS credit_events (
            id %s,
            user_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            cost INTEGER NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """ % id_type)
    conn.commit()
    conn.close()


def ensure_user_credits(user_id: str, initial_credits: int = INITIAL_CREDITS) -> Dict:
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT credits, total_used, created_at, updated_at FROM user_credits WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if row:
        conn.close()
        return {
            "credits": row["credits"],
            "total_used": row["total_used"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"]
        }
    cursor.execute("""
        INSERT INTO user_credits (user_id, credits)
        VALUES (?, ?)
    """, (user_id, initial_credits))
    cursor.execute("""
        INSERT INTO credit_events (user_id, event_type, cost)
        VALUES (?, ?, ?)
    """, (user_id, "grant", 0))
    conn.commit()
    conn.close()
    return {
        "credits": initial_credits,
        "total_used": 0,
        "created_at": None,
        "updated_at": None
    }


def get_user_credits(user_id: str) -> Optional[Dict]:
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT credits, total_used, created_at, updated_at FROM user_credits WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "credits": row["credits"],
        "total_used": row["total_used"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"]
    }


def charge_user_credits(user_id: str, cost: int) -> bool:
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE user_credits
        SET credits = credits - ?,
            total_used = total_used + 1,
            updated_at = CURRENT_TIMESTAMP
        WHERE user_id = ? AND credits >= ?
    """, (cost, user_id, cost))
    if cursor.rowcount > 0:
        cursor.execute("""
            INSERT INTO credit_events (user_id, event_type, cost)
            VALUES (?, ?, ?)
        """, (user_id, "consume", cost))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success


def grant_credits(user_id: str, credits: int, event_type: str = "purchase") -> bool:
    if credits <= 0:
        return False
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE user_credits
        SET credits = credits + ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE user_id = ?
    """, (credits, user_id))
    if cursor.rowcount > 0:
        cursor.execute("""
            INSERT INTO credit_events (user_id, event_type, cost)
            VALUES (?, ?, ?)
        """, (user_id, event_type, credits))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success


def grant_first_summary_bonus(user_id: str, bonus: int = FIRST_SUMMARY_BONUS) -> bool:
    conn = _get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 1 FROM credit_events
            WHERE user_id = ? AND event_type = 'first_summary_bonus'
            LIMIT 1
        """, (user_id,))
        if cursor.fetchone():
            return False
        cursor.execute("""
            UPDATE user_credits
            SET credits = credits + ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """, (bonus, user_id))
        cursor.execute("""
            INSERT INTO credit_events (user_id, event_type, cost)
            VALUES (?, ?, ?)
        """, (user_id, "first_summary_bonus", 0))
        conn.commit()
        return True
    finally:
        conn.close()


def get_daily_usage(user_id: str, days: int = 14):
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DATE(created_at) as day, COUNT(*) as count
        FROM credit_events
        WHERE user_id = ? AND event_type = 'consume'
        GROUP BY DATE(created_at)
        ORDER BY day DESC
        LIMIT ?
    """, (user_id, days))
    rows = cursor.fetchall()
    conn.close()
    return {row["day"]: row["count"] for row in rows}


init_credits_db()
