"""Local SQLite recovery rehearsal; never replaces or activates a database."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
TABLES = ('owner', 'challenges', 'sessions', 'observations', 'releases', 'audit',
          'evidence_versions', 'evidence_catalog', 'studies', 'study_evidence',
          'study_sessions', 'observation_links')


def readonly(path):
    if path.is_symlink() or not path.is_file():
        raise ValueError('Source must be an existing regular database file, not a symlink.')
    return sqlite3.connect(path.resolve().as_uri() + '?mode=ro', uri=True, timeout=10)


def inventory(db):
    schema = db.execute("SELECT type,name,sql FROM sqlite_master WHERE name NOT LIKE 'sqlite_%' ORDER BY name").fetchall()
    tables = {row[1] for row in schema if row[0] == 'table'}
    if tables != set(TABLES) or any(row[0] not in ('table', 'index') for row in schema):
        raise ValueError('Unrecognized schema: review the recovery tool before using this database.')
    if db.execute('PRAGMA integrity_check').fetchall() != [('ok',)]:
        raise ValueError('Database integrity check failed.')
    if db.execute('PRAGMA foreign_key_check').fetchall():
        raise ValueError('Database has broken research references.')
    digest = hashlib.sha256(json.dumps(schema, separators=(',', ':')).encode())
    counts = {}
    for table in TABLES:
        # Table names are fixed above, never supplied by a database or CLI user.
        records = sorted(json.dumps(row, separators=(',', ':')) for row in db.execute(f'SELECT * FROM {table}'))
        counts[table] = len(records)
        digest.update(json.dumps([table, records], separators=(',', ':')).encode())
    return {'counts': counts, 'content_sha256': digest.hexdigest()}


def copy_database(source, destination, strip_auth=False):
    fd = os.open(destination, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    os.close(fd)
    source_db = destination_db = None
    deadline = time.monotonic() + 30

    def progress(*_):
        if time.monotonic() > deadline:
            raise TimeoutError('Database copy exceeded the rehearsal time limit.')

    try:
        source_db = readonly(source)
        destination_db = sqlite3.connect(destination)
        source_db.backup(destination_db, pages=128, progress=progress)
        inventory(destination_db)
        if strip_auth:
            # A recovered database must require a fresh login. Keep the pinned owner.
            destination_db.execute('PRAGMA secure_delete=ON')
            destination_db.execute('DELETE FROM sessions')
            destination_db.execute('DELETE FROM challenges')
            destination_db.commit()
            destination_db.execute('VACUUM')
        result = inventory(destination_db)
        if result['counts']['sessions'] or result['counts']['challenges']:
            raise ValueError('Recovery artifact contains active authentication state.')
        return result
    finally:
        if destination_db is not None:
            destination_db.close()
        if source_db is not None:
            source_db.close()


def rehearse(source, directory):
    """Create a scrubbed snapshot and restore into a NEW private directory only."""
    source, directory = Path(source), Path(directory)
    # Validate before creating artifacts; never create a missing source database.
    connection = readonly(source)
    try:
        inventory(connection)
    finally:
        connection.close()
    directory.mkdir(mode=0o700, parents=True, exist_ok=False)
    try:
        with tempfile.TemporaryDirectory(prefix='.rehearsal-', dir=directory) as temporary:
            work = Path(temporary)
            snapshot = work / 'snapshot.sqlite3'
            restored = work / 'restored.sqlite3'
            expected = copy_database(source, snapshot, strip_auth=True)
            actual = copy_database(snapshot, restored)
            if actual != expected:
                raise ValueError('Restored database does not match the snapshot.')
            report = {
                'format': 1, 'scope': 'local recovery rehearsal; not an activated restore',
                'auth_sessions_removed': True, 'owner_binding_preserved': True,
                'inventory': actual,
                'snapshot_sha256': hashlib.sha256(snapshot.read_bytes()).hexdigest(),
                'restored_sha256': hashlib.sha256(restored.read_bytes()).hexdigest(),
                'limitations': ['Unencrypted local copies; no off-device backup.',
                                'A stale snapshot can predate withdrawals. Never activate it without reconciling later deletions and revoked releases.',
                                'Hosted storage, retention and operational recovery remain unverified.'],
            }
            for file in (snapshot, restored):
                file.rename(directory / file.name)
            report_path = directory / 'report.json'
            fd = os.open(report_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            with os.fdopen(fd, 'w') as output:
                json.dump(report, output, indent=2)
                output.write('\n')
            return report
    except Exception:
        # Leave any complete published artifacts for inspection; never touch the source.
        if not any(directory.iterdir()):
            directory.rmdir()
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', type=Path, default=ROOT / 'data/private/admin.sqlite3')
    parser.add_argument('--name', required=True, help='New rehearsal directory name (letters, digits, hyphens).')
    args = parser.parse_args()
    if not args.name or len(args.name) > 80 or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-' for c in args.name):
        parser.error('Use a short directory name containing only letters, digits and hyphens.')
    directory = ROOT / 'data/private/recovery' / args.name
    report = rehearse(args.database, directory)
    print(json.dumps({'directory': str(directory), 'restored_counts': report['inventory']['counts'],
                      'content_verified': True, 'active_database_replaced': False}, indent=2))


if __name__ == '__main__':
    main()
