"""Summarize the pinned CEB v1.1 data dictionary without reading annotation rows."""
import argparse
import hashlib
import json
from pathlib import Path

RESOURCE_ID = 'ceb-schema-json-v1-1'
EXPECTED_BYTES = 10237
EXPECTED_MD5 = '0ad197cf958d368dba94b555a8e02cf8'
EXPECTED_SHA256 = '07792fcc50dd82e74cf96fb528c2ac0c9ee5b0d038b76f01163436880a0742e1'
DEFAULT_DIRECTORY = Path(__file__).resolve().parents[1] / 'data/external' / RESOURCE_ID


def verify_local_schema(directory):
    directory = Path(directory)
    schema_path = directory / 'schema.json'
    receipt_path = directory / 'receipt.json'
    try:
        payload = schema_path.read_bytes()
        receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError('Pinned CEB schema and collection receipt are required.') from exc
    md5 = hashlib.md5(payload).hexdigest()
    sha256 = hashlib.sha256(payload).hexdigest()
    if (len(payload) != EXPECTED_BYTES or md5 != EXPECTED_MD5
            or sha256 != EXPECTED_SHA256):
        raise ValueError('CEB schema bytes do not match the pinned v1.1 file.')
    if (receipt.get('resource_id') != RESOURCE_ID or receipt.get('training_admitted') is not False
            or not any(f.get('name') == 'schema.json'
                       and f.get('bytes') == EXPECTED_BYTES
                       and f.get('md5') == EXPECTED_MD5
                       and f.get('sha256') == EXPECTED_SHA256
                       and f.get('source_checksum_verified') is True
                       for f in receipt.get('files', []))):
        raise ValueError('Collection receipt does not match the schema or its local-only boundary.')
    try:
        schema = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ValueError('Pinned CEB schema is not valid JSON.') from exc
    return schema


def summarize_schema(schema):
    if not isinstance(schema, dict) or schema.get('name') != 'ceb-schema':
        raise ValueError('Expected the CEB data dictionary.')
    fields = schema.get('fields')
    if not isinstance(fields, list) or not fields:
        raise ValueError('CEB schema has no field list.')
    names = [field.get('name') for field in fields if isinstance(field, dict)]
    if len(names) != len(fields) or not all(isinstance(name, str) for name in names):
        raise ValueError('CEB schema fields must have names.')
    if len(names) != len(set(names)):
        raise ValueError('CEB schema contains duplicate field names.')
    by_name = {field['name']: field for field in fields}
    path_description = by_name.get('filepath', {}).get('description', '')
    if not isinstance(path_description, str) or '<subset>_project_<NNN>/audio_<NNNNNN>.flac' not in path_description:
        raise ValueError('Expected the documented anonymized recording-path pattern.')
    if schema.get('primary_unit') != 'one annotated sound event per row':
        raise ValueError('Unexpected CEB row unit; review the schema before summarizing.')
    return {
        'dataset': 'Central European Birds v1.1',
        'record_doi': '10.5281/zenodo.21821133',
        'schema_file': {
            'name': 'schema.json',
            'bytes': EXPECTED_BYTES,
            'md5': EXPECTED_MD5,
            'sha256': EXPECTED_SHA256,
            'acquisition': 'local_schema_review_only',
            'training_admitted': False,
        },
        'applies_to': schema.get('applies_to', []),
        'primary_unit': schema['primary_unit'],
        'field_count': len(names),
        'field_names': names,
        'recording_path_template': '<subset>_project_<NNN>/audio_<NNNNNN>.flac',
        'split_guidance': 'Keep every annotation for the same exact filepath in one partition. The project token is anonymized; this schema does not establish independent site, device, session, or deployment groups.',
        'bird_presence_readiness': 'not_ready: the schema describes event rows, not verified negative intervals; unannotated time must not be treated as quiet.',
        'scope': 'Schema only. No annotation rows, audio, code, model, or test labels were inspected or executed.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, default=DEFAULT_DIRECTORY,
                        help='local directory containing the checksum-pinned schema.json and receipt.json')
    args = parser.parse_args()
    print(json.dumps(summarize_schema(verify_local_schema(args.directory)), indent=2))


if __name__ == '__main__':
    main()
