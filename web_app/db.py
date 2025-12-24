import os
import sqlite3
from urllib.parse import urlparse
from typing import Any, Optional, Callable


_PG_POOL = None


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
    def __init__(self, conn: Any, is_postgres: bool, releaser: Optional[Callable[[Any], None]] = None) -> None:
        self._conn = conn
        self._is_postgres = is_postgres
        self._releaser = releaser

    def cursor(self) -> CursorProxy:
        return CursorProxy(self._conn.cursor(), self._is_postgres)

    def close(self) -> None:
        if self._releaser:
            self._releaser(self._conn)
        else:
            self._conn.close()

    def __getattr__(self, name: str) -> Any:
        return getattr(self._conn, name)


def get_connection() -> ConnectionProxy:
    if using_postgres():
        import psycopg2
        from psycopg2 import pool
        from psycopg2.extras import DictCursor
        global _PG_POOL
        if _PG_POOL is None:
            min_conn = int(os.getenv("PG_POOL_MIN", "1"))
            max_conn = int(os.getenv("PG_POOL_MAX", "5"))
            _PG_POOL = pool.SimpleConnectionPool(
                min_conn,
                max_conn,
                os.getenv("DATABASE_URL"),
                cursor_factory=DictCursor
            )

        conn = _PG_POOL.getconn()
        return ConnectionProxy(conn, True, releaser=_PG_POOL.putconn)

    db_path = os.getenv("DB_PATH", "cache.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return ConnectionProxy(conn, False)


def get_backend_info() -> dict:
    if using_postgres():
        url = urlparse(os.getenv("DATABASE_URL") or "")
        return {
            "backend": "postgres",
            "host": url.hostname,
            "port": url.port,
            "database": url.path.lstrip("/"),
            "sslmode": (url.query or "").split("sslmode=")[-1] if "sslmode=" in (url.query or "") else None
        }
    return {
        "backend": "sqlite",
        "path": os.getenv("DB_PATH", "cache.db")
    }
