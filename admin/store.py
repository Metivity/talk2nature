"""Local prototype storage. Hosted deployment needs a reviewed storage adapter."""
import json
import sqlite3
from contextlib import contextmanager


class StorageUnavailable(Exception):
    """Deliberately excludes credentials, connection strings and raw SQL errors."""


def open_store(settings):
    if settings.database_url:
        from admin.postgres import PostgresStore
        return PostgresStore(settings.database_url, hosted=settings.hosted)
    return Store(settings.database)


class Store:
    def __init__(self, path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        with self.connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS owner (singleton INTEGER PRIMARY KEY CHECK(singleton=1), subject TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS challenges (digest TEXT PRIMARY KEY, expires INTEGER NOT NULL);
                CREATE TABLE IF NOT EXISTS sessions (digest TEXT PRIMARY KEY, subject TEXT NOT NULL, csrf TEXT NOT NULL, expires INTEGER NOT NULL);
                CREATE TABLE IF NOT EXISTS observations (id TEXT PRIMARY KEY, payload TEXT NOT NULL, state TEXT NOT NULL, version INTEGER NOT NULL DEFAULT 1, created INTEGER NOT NULL);
                CREATE TABLE IF NOT EXISTS releases (id TEXT PRIMARY KEY, members TEXT NOT NULL, fingerprint TEXT NOT NULL, revoked INTEGER NOT NULL DEFAULT 0, created INTEGER NOT NULL);
                CREATE TABLE IF NOT EXISTS audit (id INTEGER PRIMARY KEY, action TEXT NOT NULL, target TEXT NOT NULL, created INTEGER NOT NULL);
                CREATE TABLE IF NOT EXISTS evidence_versions (key TEXT NOT NULL, fingerprint TEXT NOT NULL, payload TEXT NOT NULL, PRIMARY KEY(key,fingerprint));
                CREATE TABLE IF NOT EXISTS evidence_catalog (key TEXT PRIMARY KEY, kind TEXT NOT NULL, title TEXT NOT NULL, fingerprint TEXT NOT NULL, active INTEGER NOT NULL DEFAULT 1, FOREIGN KEY(key,fingerprint) REFERENCES evidence_versions(key,fingerprint));
                CREATE TABLE IF NOT EXISTS studies (id TEXT PRIMARY KEY, payload TEXT NOT NULL, fingerprint TEXT NOT NULL, state TEXT NOT NULL, version INTEGER NOT NULL DEFAULT 1, created INTEGER NOT NULL);
                CREATE TABLE IF NOT EXISTS study_evidence (study_id TEXT NOT NULL REFERENCES studies(id), evidence_key TEXT NOT NULL, fingerprint TEXT NOT NULL, PRIMARY KEY(study_id,evidence_key), FOREIGN KEY(evidence_key,fingerprint) REFERENCES evidence_versions(key,fingerprint));
                CREATE TABLE IF NOT EXISTS study_sessions (id TEXT PRIMARY KEY, study_id TEXT NOT NULL REFERENCES studies(id), payload TEXT NOT NULL, state TEXT NOT NULL, version INTEGER NOT NULL DEFAULT 1, created INTEGER NOT NULL);
                CREATE TABLE IF NOT EXISTS observation_links (observation_id TEXT PRIMARY KEY REFERENCES observations(id), study_session_id TEXT NOT NULL REFERENCES study_sessions(id));
            """)
        path.chmod(0o600)

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        db.execute("PRAGMA secure_delete=ON")
        try:
            # Serialize read/modify/write transitions, including owner binding.
            db.execute("BEGIN IMMEDIATE")
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()


def observation(row):
    return {"id": row["id"], "state": row["state"], "version": row["version"],
            "created": row["created"], **json.loads(row["payload"])}


def audit(db, action, target, now):
    # No credentials, contact data, source recordings or free-text notes here.
    db.execute("INSERT INTO audit(action,target,created) VALUES(?,?,?)", (action, target, now))
