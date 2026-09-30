import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from admin.recovery import rehearse
from admin.store import Store


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'active.sqlite3'
        self.store = Store(self.source)

    def test_round_trip_preserves_research_and_owner_but_removes_live_auth(self):
        with self.store.connect() as db:
            db.execute("INSERT INTO owner VALUES(1,'synthetic-owner')")
            db.execute("INSERT INTO sessions VALUES('session-marker','synthetic-owner','csrf-marker',12345)")
            db.execute("INSERT INTO challenges VALUES('challenge-marker',12345)")
            db.execute("INSERT INTO observations VALUES('obs','{}','withdrawn',2,123)")
            db.execute("INSERT INTO releases VALUES('release','[\"obs\"]','checksum',1,123)")
            db.execute("INSERT INTO studies VALUES('study','{}','study-checksum','active',2,123)")
            db.execute("INSERT INTO study_sessions VALUES('visit','study','{}','closed',2,123)")
            db.execute("INSERT INTO evidence_versions VALUES('note:demo','hash','{}')")
            db.execute("INSERT INTO evidence_catalog VALUES('note:demo','note','Demo','hash',1)")
            db.execute("INSERT INTO study_evidence VALUES('study','note:demo','hash')")
        report = rehearse(self.source, self.root / 'recovery')
        self.assertEqual(report['inventory']['counts']['study_evidence'], 1)
        self.assertEqual(report['inventory']['counts']['sessions'], 0)
        self.assertEqual(report['inventory']['counts']['challenges'], 0)
        with self.store.connect() as db:
            self.assertEqual(db.execute('SELECT count(*) FROM sessions').fetchone()[0], 1)
            self.assertEqual(db.execute('SELECT count(*) FROM challenges').fetchone()[0], 1)
        recovered = sqlite3.connect(self.root / 'recovery/restored.sqlite3')
        try:
            self.assertEqual(recovered.execute('SELECT subject FROM owner').fetchone()[0], 'synthetic-owner')
            self.assertEqual(recovered.execute('SELECT state FROM observations').fetchone()[0], 'withdrawn')
            self.assertEqual(recovered.execute('SELECT revoked FROM releases').fetchone()[0], 1)
            self.assertEqual(recovered.execute('PRAGMA foreign_key_check').fetchall(), [])
        finally:
            recovered.close()
        self.assertEqual((self.root / 'recovery').stat().st_mode & 0o777, 0o700)
        for name in ('snapshot.sqlite3', 'restored.sqlite3', 'report.json'):
            path = self.root / 'recovery' / name
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertNotIn(b'csrf-marker', path.read_bytes())
            self.assertNotIn(b'challenge-marker', path.read_bytes())
        self.assertEqual(json.loads((self.root / 'recovery/report.json').read_text()), report)

    def test_refuses_overwrite_and_never_activates_the_restored_database(self):
        destination = self.root / 'recovery'
        rehearse(self.source, destination)
        before = {p.name: p.read_bytes() for p in destination.iterdir()}
        with self.assertRaises(FileExistsError):
            rehearse(self.source, destination)
        self.assertEqual(before, {p.name: p.read_bytes() for p in destination.iterdir()})
        with self.assertRaises(FileExistsError):
            rehearse(self.source, self.source)

    def test_missing_symlink_and_unrecognized_sources_fail_without_creating_output(self):
        symlink = self.root / 'alias.sqlite3'
        symlink.symlink_to(self.source)
        bad = self.root / 'wrong.sqlite3'
        db = sqlite3.connect(bad)
        db.execute('CREATE TABLE unrelated(value TEXT)')
        db.close()
        for source in (self.root / 'missing.sqlite3', symlink, bad):
            with self.subTest(source=source), self.assertRaises(ValueError):
                rehearse(source, self.root / 'recovery')
            self.assertFalse((self.root / 'recovery').exists())

    def test_broken_references_are_not_presented_as_a_successful_recovery(self):
        db = sqlite3.connect(self.source)
        db.execute("INSERT INTO observation_links VALUES('missing-observation','missing-session')")
        db.commit()
        db.close()
        with self.assertRaisesRegex(ValueError, 'broken research references'):
            rehearse(self.source, self.root / 'recovery')
        self.assertFalse((self.root / 'recovery').exists())


if __name__ == '__main__':
    unittest.main()
