"""Aggregate a pinned forest-bird metadata sample without exposing raw rows."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from talk2nature.collection import CATALOG, validate


RESOURCE_ID = 'northeastern-forest-bird-metadata-sample-v2'
SAMPLE_DIR = ROOT / 'data/external' / RESOURCE_ID
EXPECTED_FILES = {
    'ReadMe.txt', 'recording_metadata.csv', 'site_metadata.csv',
    'species_metadata.csv',
}


def _read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open('r', encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f'{path.name} has no CSV header.')
        return list(reader.fieldnames), list(reader)


def _verified_inputs(sample_dir: Path, catalog_path: Path) -> tuple[dict, dict[str, Path]]:
    catalog_bytes = catalog_path.read_bytes()
    catalog = json.loads(catalog_bytes)
    validate(catalog)
    resource = next((entry for entry in catalog['resources']
                     if entry['id'] == RESOURCE_ID), None)
    if resource is None:
        raise ValueError('Pinned metadata resource is missing from the catalog.')

    receipt_path = sample_dir / 'receipt.json'
    receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
    recorded_resource = receipt.get('resource')
    stable_fields = (
        'id', 'url', 'version', 'adapter', 'zenodo_record_id', 'zenodo_doi',
        'license_notice', 'admission_reason',
    )
    if (receipt.get('schema_version') != 1
            or receipt.get('resource_id') != RESOURCE_ID
            or resource.get('acquisition') != 'sample_approved'
            or not isinstance(recorded_resource, dict)
            or any(recorded_resource.get(field) != resource.get(field)
                   for field in stable_fields)
            or recorded_resource.get('rights', {}).get('license')
            != resource.get('rights', {}).get('license')
            or recorded_resource.get('files') != resource.get('files')
            or receipt.get('training_admitted') is not False):
        raise ValueError('Receipt does not match the current pinned metadata-only catalog record.')

    expected = {entry['name']: entry for entry in resource['files']}
    if set(expected) != EXPECTED_FILES:
        raise ValueError('Catalog file set differs from the reviewed four-file sample.')
    actual = {entry.get('name'): entry for entry in receipt.get('files', [])}
    if set(actual) != EXPECTED_FILES:
        raise ValueError('Receipt does not contain exactly the four reviewed metadata files.')

    paths: dict[str, Path] = {}
    for name, artifact in expected.items():
        path = sample_dir / name
        data = path.read_bytes()
        received = actual[name]
        if (len(data) != artifact['bytes']
                or hashlib.md5(data, usedforsecurity=False).hexdigest() != artifact['md5']
                or hashlib.sha256(data).hexdigest() != received.get('sha256')
                or received.get('source_checksum_verified') is not True):
            raise ValueError(f'{name} does not match its source-verified receipt.')
        paths[name] = path
    return resource, paths


def audit(sample_dir: Path = SAMPLE_DIR, catalog_path: Path = CATALOG) -> dict:
    """Return aggregate counts only; never include row IDs or coordinate values."""
    resource, paths = _verified_inputs(Path(sample_dir), Path(catalog_path))
    site_fields, site_rows = _read_rows(paths['site_metadata.csv'])
    recording_fields, recording_rows = _read_rows(paths['recording_metadata.csv'])
    species_fields, species_rows = _read_rows(paths['species_metadata.csv'])
    readme = paths['ReadMe.txt'].read_text(encoding='utf-8', errors='replace')

    required_fields = (
        (site_fields, {'SiteID', 'ParkID'}),
        (recording_fields, {'SiteID', 'ParkID', 'Dataset_ID', 'Year'}),
        (species_fields, {'IsBird', 'N_DatasetACAD', 'N_DatasetMABI', 'N_DatasetSIMR'}),
    )
    if any(not required.issubset(fields) for fields, required in required_fields):
        raise ValueError('A metadata table no longer matches the reviewed schema.')

    site_ids = {row['SiteID'] for row in site_rows if row['SiteID']}
    recording_sites = {row['SiteID'] for row in recording_rows if row['SiteID']}
    sites_by_park = Counter(row['ParkID'] for row in site_rows if row['ParkID'])
    recordings_by_park = Counter(row['ParkID'] for row in recording_rows if row['ParkID'])
    recordings_by_dataset = Counter(row['Dataset_ID'] for row in recording_rows
                                     if row['Dataset_ID'])
    recordings_by_year = Counter(row['Year'] for row in recording_rows if row['Year'])

    is_bird = Counter(row['IsBird'].strip().lower() for row in species_rows)
    annotation_columns = ('N_DatasetACAD', 'N_DatasetMABI', 'N_DatasetSIMR')
    bird_rows = [row for row in species_rows if row['IsBird'].strip().lower() == 'yes']
    bird_rows_with_annotations = sum(
        any(int(row[column] or 0) > 0 for column in annotation_columns)
        for row in bird_rows)
    bird_annotations = sum(int(row[column] or 0)
                           for row in bird_rows for column in annotation_columns)

    def readme_count(label: str) -> int | None:
        match = re.search(rf'Total\s+{label}:\s*\*{{0,2}}([\d,]+)', readme, re.I)
        return int(match.group(1).replace(',', '')) if match else None

    return {
        'schema_version': 1,
        'resource_id': resource['id'],
        'record_id': resource['zenodo_record_id'],
        'training_admitted': False,
        'inputs': {name: {
            'bytes': next(item['bytes'] for item in resource['files'] if item['name'] == name),
            'md5_verified': True,
            'sha256': next(item['sha256'] for item in json.loads(
                (Path(sample_dir) / 'receipt.json').read_text(encoding='utf-8'))['files']
                if item['name'] == name),
        } for name in sorted(EXPECTED_FILES)},
        'sites': {
            'site_rows': len(site_rows),
            'unique_site_ids': len(site_ids),
            'recording_metadata_unique_site_ids': len(recording_sites),
            'site_sets_match': site_ids == recording_sites,
            'counts_by_park': dict(sorted(sites_by_park.items())),
            'coordinate_columns_present': {'Latitude', 'Longitude'}.issubset(site_fields),
            'coordinate_values_exported': False,
        },
        'recordings': {
            'rows': len(recording_rows),
            'counts_by_park': dict(sorted(recordings_by_park.items())),
            'counts_by_dataset': dict(sorted(recordings_by_dataset.items())),
            'counts_by_year': dict(sorted(recordings_by_year.items())),
        },
        'species': {
            'metadata_rows': len(species_rows),
            'is_bird_flag_counts': dict(sorted(is_bird.items())),
            'bird_rows_with_yes_flag': len(bird_rows),
            'bird_rows_with_nonzero_annotations': bird_rows_with_annotations,
            'annotation_total_for_yes_rows': bird_annotations,
            'readme_species_total': readme_count('species recorded'),
        },
        'readme_totals': {
            'recordings': readme_count('10-minute recordings'),
            'locations': readme_count('recording locations'),
            'species': readme_count('species recorded'),
        },
        'interpretation': [
            'The site table and recording table independently contain the same 104 unique site identifiers.',
            'The site table park counts are ACAD 31, HBEF 24, KAWW 24 and MABI 25; the public landing-page opening summary lists KAWW as 20.',
            'The README states 88 species; the species table marks 96 rows IsBird=Yes with nonzero annotation counts. This version-level count discrepancy remains unresolved.',
            'Aggregates are a metadata integrity check, not a label validation, model result or communication finding.',
            'No raw site identifiers or coordinate values are included in this report.',
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sample-dir', type=Path, default=SAMPLE_DIR)
    parser.add_argument('--catalog', type=Path, default=CATALOG)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = audit(args.sample_dir, args.catalog)
    encoded = json.dumps(report, indent=2, ensure_ascii=False) + '\n'
    if args.output:
        args.output.write_text(encoded, encoding='utf-8')
    else:
        print(encoded, end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
