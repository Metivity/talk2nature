"""Run the full owner-workbench suite against an explicitly disposable local DB."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
import os
from pathlib import Path
import threading
import unittest
from urllib.parse import urlsplit

from admin.tests import test_workbench
from admin.database import initialize, migrate
from admin.postgres import PostgresStore
from admin.store import StorageUnavailable

TEST_URL = os.getenv('T2N_TEST_DATABASE_URL', '')
APP_URL = os.getenv('T2N_TEST_APP_DATABASE_URL', '')


def assert_disposable(value):
    url = urlsplit(value)
    if url.hostname not in {'localhost', '127.0.0.1', '::1'} or not url.path.startswith('/t2n_test_'):
        raise ValueError('PostgreSQL tests require an explicitly disposable local t2n_test_* database.')


@unittest.skipUnless(TEST_URL, 'Set T2N_TEST_DATABASE_URL to a disposable local database to run PostgreSQL integration.')
class PostgresWorkbenchTests(test_workbench.WorkbenchTests):
    def test_explicit_postgres_v1_migration_preserves_data_and_runtime_is_locked(self):
        import psycopg
        with psycopg.connect(TEST_URL) as db:
            db.execute('DROP SCHEMA talk2nature CASCADE')
            db.execute((Path(__file__).resolve().parents[1] / 'schema/postgres-v1.sql').read_text())
            db.execute("INSERT INTO owner VALUES(1,'synthetic-owner')")
            db.execute("INSERT INTO observations VALUES('retained','{}','withdrawn',2,123)")
        with self.assertRaises(StorageUnavailable): PostgresStore(TEST_URL)
        with self.assertRaises(StorageUnavailable): initialize(TEST_URL)
        self.assertTrue(migrate(TEST_URL))
        self.assertFalse(migrate(TEST_URL))
        with PostgresStore(TEST_URL).connect() as db:
            self.assertEqual(db.execute('SELECT subject FROM owner').fetchone()[0],'synthetic-owner')
            self.assertEqual(db.execute('SELECT state FROM observations').fetchone()[0],'withdrawn')
            self.assertEqual(db.execute('SELECT COUNT(*) FROM model_inputs').fetchone()[0],0)
        if APP_URL:
            with psycopg.connect(TEST_URL) as db:
                db.execute((Path(__file__).resolve().parents[1] / 'schema/grant-runtime.sql').read_text())
            with PostgresStore(APP_URL).connect() as db:
                self.assertEqual(db.execute('SELECT COUNT(*) FROM research_media').fetchone()[0],0)
            with self.assertRaises(StorageUnavailable):
                with PostgresStore(APP_URL).connect() as db:
                    db.execute('DROP TABLE research_media CASCADE')

    def settings_for_test(self):
        import psycopg
        assert_disposable(TEST_URL)
        with psycopg.connect(TEST_URL, connect_timeout=5) as db:
            db.execute('DROP SCHEMA IF EXISTS talk2nature CASCADE')
        initialize(TEST_URL)
        if APP_URL:
            assert_disposable(APP_URL)
            with psycopg.connect(TEST_URL) as db:
                db.execute((Path(__file__).resolve().parents[1] / 'schema/grant-runtime.sql').read_text())
        return replace(super().settings_for_test(), database_url=APP_URL or TEST_URL)

    @unittest.skipUnless(APP_URL, 'Runtime-role checks require T2N_TEST_APP_DATABASE_URL.')
    def test_runtime_role_cannot_change_schema_or_schema_version(self):
        for query in ('CREATE TABLE talk2nature.forbidden(id INTEGER)',
                      'UPDATE schema_version SET version=2', 'DROP TABLE observations'):
            with self.subTest(query=query), self.assertRaises(StorageUnavailable):
                with self.app.state.store.connect() as db:
                    db.execute(query)

    def test_postgres_schema_is_private_and_runtime_does_not_create_it(self):
        import psycopg
        self.assertFalse(initialize(TEST_URL))
        with psycopg.connect(TEST_URL) as db:
            self.assertIsNone(db.execute("SELECT to_regclass('public.observations')").fetchone()[0])
            # No PUBLIC grant on the private schema; role-specific grants are separately configured.
            acl = db.execute("SELECT nspacl::text FROM pg_namespace WHERE nspname='talk2nature'").fetchone()[0]
            self.assertNotIn('{=', acl)
            self.assertNotIn(',=', acl)
            db.execute('DROP SCHEMA talk2nature CASCADE')
        with self.assertRaises(StorageUnavailable): PostgresStore(TEST_URL)
        with psycopg.connect(TEST_URL) as db:
            self.assertIsNone(db.execute("SELECT to_regnamespace('talk2nature')").fetchone()[0])

    def test_postgres_serializes_replay_consumption_and_rolls_back_failed_batches(self):
        store = self.app.state.store
        with store.connect() as db:
            db.execute("INSERT INTO challenges VALUES(?,?)", ('concurrent-nonce',9999999999))
        barrier = threading.Barrier(2)
        def consume():
            barrier.wait(timeout=5)
            with store.connect() as db:
                return bool(db.execute('DELETE FROM challenges WHERE digest=? RETURNING digest',('concurrent-nonce',)).fetchone())
        with ThreadPoolExecutor(max_workers=2) as pool:
            self.assertEqual(sorted(pool.map(lambda _: consume(), range(2))), [False, True])
        with self.assertRaises(RuntimeError):
            with store.connect() as db:
                db.execute('INSERT INTO owner VALUES(1,?)', ('rollback-owner',))
                raise RuntimeError('Abort this unit of work')
        with store.connect() as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM owner').fetchone()[0],0)

    def test_sql_values_are_bound_and_literal_question_marks_survive(self):
        with self.app.state.store.connect() as db:
            value = "What? 100%; DROP TABLE owner; '"
            row = db.execute("SELECT ? AS value, 'a question?' AS literal",(value,)).fetchone()
            self.assertEqual(row['value'], value)
            self.assertEqual(row[1], 'a question?')
            self.assertEqual(dict(row), {'value':value,'literal':'a question?'})
