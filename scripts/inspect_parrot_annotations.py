"""Summarize the collected parrot table without exporting free-text observations.

Counts are table diagnostics, not numbers of calls or independently labeled birds.
The source table must match its acquisition receipt before it is summarized.
"""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def inspect(folder):
    folder = Path(folder)
    receipt = json.loads((folder / 'receipt.json').read_text())
    artifact = next(f for f in receipt['files'] if f['name'] == 'annotations-2020.csv')
    data = (folder / artifact['name']).read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != artifact['sha256']:
        raise ValueError('Annotation table differs from the collected source.')
    reader = csv.DictReader(io.StringIO(data.decode('utf-8-sig')), delimiter=';')
    required = ['annotation_ref', 'uncertain', 'bird', 'behaviour', 'location',
                'others', 'association', 'notes']
    if reader.fieldnames != required:
        raise ValueError('Source schema changed; inspect before interpreting columns.')
    rows = list(reader)
    if any(None in row or any(v is None for v in row.values()) for row in rows):
        raise ValueError('Malformed CSV row.')
    populated = {k: sum(bool(r[k].strip()) for r in rows) for k in required}
    refs = [r['annotation_ref'].strip() for r in rows if r['annotation_ref'].strip()]
    behaviors = {r['behaviour'].strip() for r in rows if r['behaviour'].strip()}
    return {'resource_id': receipt['resource_id'], 'source_sha256': digest,
            'source_url': artifact['url'], 'source_version': receipt['resource']['version'],
            'rows': len(rows), 'columns': required, 'nonempty': populated,
            'unique_nonempty_behavior_strings': len(behaviors),
            'duplicate_nonempty_annotation_refs': len(refs) - len(set(refs)),
            'uncertainty_flag_1': sum(r['uncertain'].strip() == '1' for r in rows),
            'training_admitted': False,
            'limitations': [
                'Rows are annotations, not necessarily one call each.',
                'Bird values are not yet normalized individual identities.',
                'Blank uncertainty flags do not establish label reliability.',
                'Behavior strings mix visible actions, vocal events and interpretation.',
                'Audio, selection-table joins, session keys and independent label agreement are absent.',
                'No raw notes, locations or individual identifiers are exported by this report.']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--folder', type=Path,
                        default=ROOT / 'data/external/monk-parakeet-annotations')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = json.dumps(inspect(args.folder), indent=2) + '\n'
    if args.output:
        args.output.write_text(result)
    else:
        print(result, end='')
