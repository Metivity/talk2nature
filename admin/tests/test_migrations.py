from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from admin.migrations import migrate_sqlite
from admin.recovery import rehearse
from admin.store import Store, StorageUnavailable


class SQLiteMigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root / 'legacy.sqlite3'
        Store(self.path)
        # Reconstruct the exact unversioned v1 tables from a fresh local store.
        with sqlite3.connect(self.path) as db:
            for table in ('model_results','model_inputs','model_runs','media_sync','research_media'):
                db.execute(f'DROP TABLE {table}')
            db.execute('PRAGMA user_version=0')
            db.execute("INSERT INTO owner VALUES(1,'synthetic-owner')")
            db.execute("INSERT INTO observations VALUES('retained','{}','withdrawn',2,123)")

    def test_explicit_migration_preserves_records_owner_and_recovery(self):
        with self.assertRaises(StorageUnavailable):
            Store(self.path)
        legacy = rehearse(self.path, self.root / 'before')
        self.assertEqual(legacy['inventory']['counts']['observations'],1)
        self.assertTrue(migrate_sqlite(self.path))
        self.assertFalse(migrate_sqlite(self.path))
        with Store(self.path).connect() as db:
            self.assertEqual(db.execute('PRAGMA user_version').fetchone()[0],2)
            self.assertEqual(db.execute('SELECT subject FROM owner').fetchone()[0],'synthetic-owner')
            self.assertEqual(db.execute('SELECT state FROM observations').fetchone()[0],'withdrawn')
            self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(),[])
        result = rehearse(self.path,self.root / 'after')
        self.assertEqual(result['inventory']['counts']['model_inputs'],0)

    def test_failed_migration_rolls_back_ddl_and_version(self):
        with patch('admin.migrations.SQL') as sql:
            sql.read_text.return_value = 'CREATE TABLE migration_probe(id TEXT); CREATE TABLE owner(id TEXT);'
            with self.assertRaises(sqlite3.OperationalError):
                migrate_sqlite(self.path)
        with sqlite3.connect(self.path) as db:
            self.assertEqual(db.execute('PRAGMA user_version').fetchone()[0],0)
            self.assertIsNone(db.execute("SELECT name FROM sqlite_master WHERE name='migration_probe'").fetchone())
            self.assertEqual(db.execute('SELECT COUNT(*) FROM owner').fetchone()[0],1)

    def test_refuses_unknown_missing_or_symlink_sources(self):
        link = self.root / 'link.sqlite3'; link.symlink_to(self.path)
        for path in (link,self.root/'missing.sqlite3'):
            with self.assertRaises(ValueError): migrate_sqlite(path)
        with sqlite3.connect(self.path) as db: db.execute('PRAGMA user_version=999')
        with self.assertRaises(ValueError): migrate_sqlite(self.path)
