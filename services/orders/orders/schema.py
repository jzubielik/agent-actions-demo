"""Applies the SQL files in migrations/ in order and records each one.

Usage: python -m orders.schema DATABASE
"""
import sqlite3
import sys
from pathlib import Path

MIGRATIONS = Path(__file__).resolve().parents[3] / "migrations"


def pending(conn: sqlite3.Connection, directory: Path) -> list[Path]:
    conn.execute("CREATE TABLE IF NOT EXISTS schema_migrations (name TEXT PRIMARY KEY)")
    applied = {row[0] for row in conn.execute("SELECT name FROM schema_migrations")}
    return [path for path in sorted(directory.glob("*.sql")) if path.name not in applied]


def migrate(conn: sqlite3.Connection, directory: Path = MIGRATIONS) -> list[str]:
    """Applies every pending migration. A file that fails leaves no part of itself behind.

    The connection must be in autocommit mode (isolation_level=None): the transaction around
    each file is opened and closed here.
    """
    done = []
    for path in pending(conn, directory):
        try:
            conn.executescript(f"BEGIN;\n{path.read_text()}")
            conn.execute("INSERT INTO schema_migrations (name) VALUES (?)", (path.name,))
            conn.execute("COMMIT")
        except sqlite3.Error:
            if conn.in_transaction:
                conn.execute("ROLLBACK")
            raise
        done.append(path.name)
    return done


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    for name in migrate(sqlite3.connect(sys.argv[1], isolation_level=None)):
        print(f"applied {name}")
