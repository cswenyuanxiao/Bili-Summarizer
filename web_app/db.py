import os
import sqlite3
from typing import Any, Optional


def using_postgres() -> bool:
    return bool(os.getenv("DATABASE_URL"))


class CursorProxy:
    def __init__(self, cursor: Any, is_postgres: bool) -> None:
        self._cursor = cursor
        self._is_postgres = is_postgres

    def execute(self, query: str, params: Optional[tuple] = None) -> Any:
        if self._is_postgres:
            query = query.replace("?", "%s")
        return self._cursor.execute(query, params or ())

    def executemany(self, query: str, params: list) -> Any:
        if self._is_postgres:
            query = query.replace("?", "%s")
        return self._cursor.executemany(query, params)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._cursor, name)


class ConnectionProxy:
    def __init__(self, conn: Any, is_postgres: bool) -> None:
        self._conn = conn
        self._is_postgres = is_postgres

    def cursor(self) -> CursorProxy:
        return CursorProxy(self._conn.cursor(), self._is_postgres)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._conn, name)


def get_connection() -> ConnectionProxy:
    if using_postgres():
        import psycopg2
        from psycopg2.extras import DictCursor

        conn = psycopg2.connect(os.getenv("DATABASE_URL"), cursor_factory=DictCursor)
        return ConnectionProxy(conn, True)

    db_path = os.getenv("DB_PATH", "cache.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return ConnectionProxy(conn, False)
