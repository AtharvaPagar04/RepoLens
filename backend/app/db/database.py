"""Database helpers."""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from app.core.config import DEFAULT_DATABASE_PATH
from app.db.schema import SCHEMA_SQL


def get_database_path() -> Path:
    raw = os.getenv("REPOLENS_DATABASE_PATH", str(DEFAULT_DATABASE_PATH)).strip()
    return Path(raw).expanduser().resolve()


def init_db() -> None:
    db_path = get_database_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(str(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON;")
        conn.executescript(SCHEMA_SQL)


@contextmanager
def db_cursor():
    init_db()
    conn = sqlite3.connect(str(get_database_path()))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON;")
    try:
        cursor = conn.cursor()
        yield conn, cursor
        conn.commit()
    finally:
        conn.close()
