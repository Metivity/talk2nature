"""Import curated public metadata into the private database; never read raw samples."""
import argparse
import hashlib
import json
import time
from pathlib import Path

from admin.store import Store, audit
from talk2nature.collection import validate

ROOT = Path(__file__).resolve().parents[1]


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def fingerprint(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def read_catalog(root=ROOT):
    sources = json.loads((root / 'content/sources.json').read_text())
    notes = json.loads((root / 'content/research.json').read_text())
    resources = validate(json.loads((root / 'research/resources.json').read_text()))['resources']
    entries = []
    for kind, rows, field in [('source', sources, 'id'), ('note', notes, 'slug'), ('resource', resources, 'id')]:
        for row in rows:
            if not isinstance(row, dict) or not row.get('title') or field not in row:
                raise ValueError('Invalid public catalog record.')
            entries.append({'key': f'{kind}:{row[field]}', 'kind': kind,
                            'title': row['title'], 'payload': row})
    if len({e['key'] for e in entries}) != len(entries):
        raise ValueError('Duplicate catalog key.')
    if any(not set(n['source_ids']) <= {s['id'] for s in sources} for n in notes):
        raise ValueError('Evidence note cites a missing source.')
    return entries


def sync_catalog(store, entries, now=None):
    # Validate the complete input before making a transaction visible.
    keys = [e['key'] for e in entries]
    if not entries or len(set(keys)) != len(keys):
        raise ValueError('A nonempty catalog with unique keys is required.')
    prepared = [(e, canonical(e['payload']), fingerprint(e['payload'])) for e in entries]
    created = changed = retired = 0
    with store.connect() as db:
        existing = {r['key']: r for r in db.execute('SELECT * FROM evidence_catalog')}
        for entry, payload, checksum in prepared:
            previous = existing.get(entry['key'])
            created += previous is None
            changed += bool(previous and (previous['fingerprint'] != checksum or not previous['active']))
            db.execute('INSERT OR IGNORE INTO evidence_versions VALUES(?,?,?)', (entry['key'], checksum, payload))
            db.execute('''INSERT INTO evidence_catalog VALUES(?,?,?,?,1)
                ON CONFLICT(key) DO UPDATE SET kind=excluded.kind,title=excluded.title,
                fingerprint=excluded.fingerprint,active=1''',
                (entry['key'], entry['kind'], entry['title'], checksum))
        for key, previous in existing.items():
            if key not in keys and previous['active']:
                db.execute('UPDATE evidence_catalog SET active=0 WHERE key=?', (key,))
                retired += 1
        if created or changed or retired:
            audit(db, 'catalog_synced', fingerprint(entries), int(time.time()) if now is None else now)
    return {'records': len(entries), 'created': created, 'changed': changed, 'retired': retired}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', type=Path, default=ROOT / 'data/private/admin.sqlite3')
    args = parser.parse_args()
    print(json.dumps(sync_catalog(Store(args.database), read_catalog()), indent=2))
