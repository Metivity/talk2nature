"""Explicit, transactional lineage migration; no cloud provisioning or media IO."""
from pathlib import Path
import sqlite3

VERSION = 2
SQL = Path(__file__).parent / 'schema/research-v2.sql'


def extend_sqlite(db):
    # Fixed project SQL only. execute (not executescript) preserves the transaction.
    for statement in SQL.read_text().split(';'):
        if statement.strip():
            db.execute(statement)
    db.execute('PRAGMA user_version=2')


def migrate_sqlite(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError('Migration requires an existing regular SQLite database.')
    with sqlite3.connect(path.resolve().as_uri() + '?mode=rw', uri=True, timeout=10) as db:
        db.execute('PRAGMA foreign_keys=ON')
        db.execute('BEGIN IMMEDIATE')
        version = db.execute('PRAGMA user_version').fetchone()[0]
        from admin.recovery import TABLES, inventory
        inventory(db)
        tables = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
        if version == VERSION:
            if tables != set(TABLES):
                raise ValueError('Incomplete v2 schema; migration refused.')
            return False
        if version != 0 or tables != set(TABLES[:-5]):
            raise ValueError('Unrecognized SQLite schema; migration refused.')
        extend_sqlite(db)
        if db.execute('PRAGMA foreign_key_check').fetchall():
            raise ValueError('Broken research references; migration rolled back.')
    return True
