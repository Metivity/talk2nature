"""Explicit PostgreSQL schema initialization and public-catalog import."""
import argparse
import json
import os
from pathlib import Path

from admin.postgres import LOCK_ID, SCHEMA_VERSION, PostgresStore, validate_database_url
from admin.store import StorageUnavailable


def initialize(database_url):
    import psycopg
    validate_database_url(database_url)
    try:
        with psycopg.connect(database_url, connect_timeout=10, prepare_threshold=None) as db:
            db.execute("SET LOCAL statement_timeout='20s'")
            db.execute("SET LOCAL lock_timeout='5s'")
            db.execute('SELECT pg_advisory_xact_lock(%s)', (LOCK_ID,))
            if db.execute("SELECT to_regnamespace('talk2nature')").fetchone()[0]:
                row = db.execute('SELECT version FROM talk2nature.schema_version WHERE singleton=1').fetchone()
                if not row or row[0] != SCHEMA_VERSION:
                    raise StorageUnavailable('Existing schema needs an explicit reviewed migration.')
                return False
            db.execute((Path(__file__).parent / 'schema/postgres-v1.sql').read_text())
            db.execute((Path(__file__).parent / 'schema/research-v2.sql').read_text())
            db.execute('UPDATE schema_version SET version=2 WHERE singleton=1')
            return True
    except psycopg.Error:
        raise StorageUnavailable('Schema initialization failed; no connection details have been logged.') from None


def migrate(database_url):
    """Schema-owner operation; runtime credentials cannot migrate."""
    import psycopg
    validate_database_url(database_url)
    try:
        with psycopg.connect(database_url, connect_timeout=10, prepare_threshold=None) as db:
            db.execute("SET LOCAL statement_timeout='20s'")
            db.execute("SET LOCAL lock_timeout='5s'")
            db.execute('SELECT pg_advisory_xact_lock(%s)', (LOCK_ID,))
            db.execute('SET LOCAL search_path=talk2nature,pg_catalog')
            row = db.execute('SELECT version FROM schema_version WHERE singleton=1').fetchone()
            if row and row[0] == SCHEMA_VERSION:
                return False
            if not row or row[0] != 1:
                raise StorageUnavailable('Unrecognized schema version; migration refused.')
            db.execute((Path(__file__).parent / 'schema/research-v2.sql').read_text())
            db.execute('UPDATE schema_version SET version=2 WHERE singleton=1')
            return True
    except psycopg.Error:
        raise StorageUnavailable('Migration failed and rolled back; no connection details have been logged.') from None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['init', 'migrate', 'migrate-sqlite', 'import-catalog', 'check'])
    parser.add_argument('--database', type=Path, help='Existing SQLite file, for migrate-sqlite only.')
    args = parser.parse_args()
    if args.action == 'migrate-sqlite':
        from admin.migrations import migrate_sqlite
        if not args.database:
            parser.error('--database is required for migrate-sqlite.')
        print(json.dumps({'schema_migrated': migrate_sqlite(args.database), 'version': SCHEMA_VERSION}))
        return
    if args.database:
        parser.error('--database applies only to migrate-sqlite.')
    database_url = os.getenv('T2N_DATABASE_URL', '')
    if not database_url:
        parser.error('Set T2N_DATABASE_URL in the environment; never pass credentials on the command line.')
    if args.action == 'migrate':
        print(json.dumps({'schema_migrated': migrate(database_url), 'version': SCHEMA_VERSION}))
        return
    if args.action == 'init':
        print(json.dumps({'schema_created': initialize(database_url), 'version': SCHEMA_VERSION}))
        return
    store = PostgresStore(database_url)
    if args.action == 'import-catalog':
        from admin.catalog import read_catalog, sync_catalog
        print(json.dumps(sync_catalog(store, read_catalog())))
    else:
        print(json.dumps({'database': 'postgresql', 'schema_version': SCHEMA_VERSION, 'connected': True}))


if __name__ == '__main__':
    main()
