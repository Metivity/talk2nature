"""Audit one rights-checked monk-parakeet selection table without exposing rows.

The report reproduces the 14-row cross-scale exclusion from the pinned analysis
logic using the Figshare selection CSV only. It does not read or validate audio,
run the authors' R code, reproduce the paper's models, or infer call meaning.
"""
import argparse
import csv
import hashlib
import io
import json
import re
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESOURCE_ID = 'monk-parakeet-identity-figshare-2023'
FILE_NAME = 'monk_parakeet_contactCalls_rangeComparison_selectionTable.csv'
FILE_ID = 40086154
ITEM_ID = 22582099
API_URL = f'https://api.figshare.com/v2/articles/{ITEM_ID}'
FILE_URL = f'https://ndownloader.figshare.com/files/{FILE_ID}'
REQUIRED_COLUMNS = {'sound.files', 'selec', 'social_scale', 'Bird_ID'}


def _read_json(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError('Expected a regular, non-linked metadata file.')
    return json.loads(path.read_text(encoding='utf-8'))


def inspect(sample_folder, catalog_path=ROOT / 'research/resources.json'):
    sample_folder = Path(sample_folder)
    if sample_folder.is_symlink() or not sample_folder.is_dir():
        raise ValueError('Expected a regular, non-linked sample directory.')
    receipt = _read_json(sample_folder / 'receipt.json')
    catalog = _read_json(catalog_path)
    if catalog.get('schema_version') != 1 or receipt.get('schema_version') != 1:
        raise ValueError('Expected collection catalog and receipt schema version 1.')
    resources = [r for r in catalog.get('resources', []) if r.get('id') == RESOURCE_ID]
    if len(resources) != 1:
        raise ValueError('Expected exactly one pinned resource in the collection catalog.')
    resource = resources[0]
    receipt_resource = receipt.get('resource', {})
    receipt_resource_files = receipt_resource.get('files', [])
    if (resource.get('adapter') != 'figshare_public'
            or resource.get('figshare_item_id') != ITEM_ID
            or resource.get('url') != API_URL
            or '.v2' not in resource.get('version', '')):
        raise ValueError('Collection resource no longer matches the reviewed Figshare v2 item.')
    catalog_files = resource.get('files', [])
    receipt_files = receipt.get('files', [])
    if (receipt.get('resource_id') != RESOURCE_ID
            or receipt.get('training_admitted') is not False
            or receipt_resource.get('id') != RESOURCE_ID
            or receipt_resource.get('version') != resource.get('version')
            or receipt_resource.get('figshare_item_id') != ITEM_ID
            or receipt_resource.get('url') != API_URL
            or not re.fullmatch('[a-f0-9]{64}', receipt.get('catalog_sha256', ''))
            or len(catalog_files) != 1 or len(receipt_resource_files) != 1
            or len(receipt_files) != 1):
        raise ValueError('Receipt does not identify the exact single-file, non-admitted sample.')
    expected = catalog_files[0]
    receipt_catalog_file = receipt_resource_files[0]
    received = receipt_files[0]
    expected_fields = {
        'name': FILE_NAME, 'url': FILE_URL, 'source_url': API_URL,
        'figshare_file_id': FILE_ID, 'bytes': expected.get('bytes'),
        'md5': expected.get('md5'),
    }
    if (expected.get('name') != FILE_NAME or expected.get('figshare_file_id') != FILE_ID
            or expected.get('url') != FILE_URL or expected.get('source_url') != API_URL
            or not isinstance(expected.get('bytes'), int) or expected['bytes'] <= 0
            or not re.fullmatch('[a-f0-9]{32}', expected.get('md5', ''))
            or any(receipt_catalog_file.get(key) != value for key, value in expected.items())
            or any(received.get(key) != value for key, value in expected_fields.items())
            or received.get('source_checksum_verified') is not True):
        raise ValueError('Receipt and catalog do not agree on the exact Figshare file.')

    path = sample_folder / FILE_NAME
    if path.is_symlink() or not path.is_file():
        raise ValueError('Pinned selection table is missing or linked.')
    data = path.read_bytes()
    if (len(data) != expected['bytes'] or hashlib.md5(data, usedforsecurity=False).hexdigest() != expected['md5']
            or hashlib.sha256(data).hexdigest() != received.get('sha256')):
        raise ValueError('Selection table differs from its provider and local checksum receipts.')

    try:
        reader = csv.DictReader(io.StringIO(data.decode('utf-8-sig')))
        if not reader.fieldnames or not REQUIRED_COLUMNS.issubset(reader.fieldnames):
            raise ValueError('Selection-table columns differ from the reviewed schema.')
        rows = []
        for row in reader:
            if None in row or any(value is None for value in row.values()):
                raise ValueError('Malformed row in the pinned selection table.')
            if any(not (row.get(field) or '').strip() for field in ('sound.files', 'social_scale', 'Bird_ID')):
                raise ValueError('A required grouping field is blank; inspect before continuing.')
            rows.append(row)
    except UnicodeDecodeError as exc:
        raise ValueError('Selection table is not UTF-8 text.') from exc
    if not rows:
        raise ValueError('Selection table has no rows.')

    scale_counts = Counter(row['social_scale'].strip() for row in rows)
    if set(scale_counts) != {'Individual', 'Site'}:
        raise ValueError('Unexpected social-scale values; do not silently recode them.')
    individual_ids = {row['Bird_ID'].strip() for row in rows
                      if row['social_scale'].strip() == 'Individual'}
    site_suffix_rows = [row for row in rows
                        if row['social_scale'].strip() == 'Site'
                        and '_site_scale' in row['sound.files']]
    shared_identity_rows = sum(row['Bird_ID'].strip() in individual_ids
                               for row in site_suffix_rows)
    return {
        'schema_version': 1,
        'reviewed': date.today().isoformat(),
        'resource_id': RESOURCE_ID,
        'figshare_item_doi': '10.6084/m9.figshare.22582099.v2',
        'figshare_file_id': FILE_ID,
        'analysis_reference': (
            'https://github.com/gsvidaurre/identity-information-post-introduction/'
            'blob/1f7031dc996c79914ccf5d042181f947793fb459/'
            'IdentityEncoding_Code_05_SiteScaleDatasets.Rmd#L129-L175'),
        'file_bytes': len(data),
        'provider_md5': expected['md5'],
        'local_sha256': hashlib.sha256(data).hexdigest(),
        'selection_table_rows': len(rows),
        'rows_by_social_scale': dict(sorted(scale_counts.items())),
        'site_scale_rows_with_site_scale_filename_suffix': len(site_suffix_rows),
        'site_scale_suffix_rows_for_ids_also_in_individual_scale': shared_identity_rows,
        'rows_after_applying_the_pinned_cross_scale_exclusion': len(rows) - shared_identity_rows,
        'analysis_script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'training_admitted': False,
        'interpretation': (
            'Aggregate CSV-level reproduction of the pinned R exclusion rule. '
            'Raw rows, caller IDs, file names, sites, coordinates and free text are omitted. '
            'No audio, extended selection-table object, R code or model was run; '
            'the result is not a benchmark or a claim about call meaning.'),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sample', type=Path,
                        default=ROOT / 'data/external' / RESOURCE_ID)
    parser.add_argument('--catalog', type=Path, default=ROOT / 'research/resources.json')
    parser.add_argument('--output', type=Path, default=ROOT / 'research/monk_parakeet_selection_audit.json')
    args = parser.parse_args()
    report = inspect(args.sample, args.catalog)
    args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'report': str(args.output), 'selection_table_rows': report['selection_table_rows'],
                      'training_admitted': False}))


if __name__ == '__main__':
    main()
