import sqlite3

import pytest

from orders.schema import MIGRATIONS, migrate


def fresh() -> sqlite3.Connection:
    return sqlite3.connect(":memory:", isolation_level=None)


def test_every_migration_applies_once_from_an_empty_database():
    conn = fresh()
    names = [path.name for path in sorted(MIGRATIONS.glob("*.sql"))]
    assert migrate(conn) == names
    assert migrate(conn) == []
    assert names == sorted(names) and len({name[:4] for name in names}) == len(names)


def test_a_failing_migration_leaves_nothing_behind(tmp_path):
    (tmp_path / "0001_ok.sql").write_text("CREATE TABLE a (id INTEGER);")
    (tmp_path / "0002_bad.sql").write_text("CREATE TABLE b (id INTEGER); CREATE TABLE a (id INTEGER);")
    conn = fresh()
    with pytest.raises(sqlite3.Error):
        migrate(conn, tmp_path)
    tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    assert tables == {"schema_migrations", "a"}
    assert [row[0] for row in conn.execute("SELECT name FROM schema_migrations")] == ["0001_ok.sql"]
