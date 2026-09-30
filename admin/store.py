"""Local prototype storage. Hosted deployment needs a reviewed storage adapter."""
import json
import sqlite3
from contextlib import contextmanager


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
            """)
        path.chmod(0o600)

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
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
