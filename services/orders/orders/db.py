"""SQLite connection of the orders service."""
import sqlite3

from .schema import migrate


def connect(path: str) -> sqlite3.Connection:
    """Opens the database with the schema up to date.

    check_same_thread is off because the web framework runs handlers in a thread pool; each
    request still uses the connection for one statement or one transaction at a time.
    """
    conn = sqlite3.connect(path, check_same_thread=False, isolation_level=None)
    conn.row_factory = sqlite3.Row
    # SQLite does not enforce foreign keys unless each connection asks for it.
    conn.execute("PRAGMA foreign_keys = ON")
    migrate(conn)
    return conn
