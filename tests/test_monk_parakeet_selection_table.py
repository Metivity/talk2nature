import csv
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from scripts.inspect_monk_parakeet_selection_table import (
    API_URL, FILE_ID, FILE_NAME, FILE_URL, ITEM_ID, RESOURCE_ID, inspect,
)


def build_fixture(root, rows):
    sample = root / RESOURCE_ID
    sample.mkdir()
    output = io.StringIO(newline='')
    columns = ['sound.files', 'selec', 'social_scale', 'Bird_ID', 'lat', 'lon', 'notes']
    writer = csv.DictWriter(output, fieldnames=columns)
    writer.writeheader()
    writer.writerows(rows)
    data = output.getvalue().encode('utf-8')
    path = sample / FILE_NAME
    path.write_bytes(data)
    md5 = hashlib.md5(data, usedforsecurity=False).hexdigest()
    sha256 = hashlib.sha256(data).hexdigest()
    resource = {
        'id': RESOURCE_ID,
        'version': f'Figshare DOI 10.6084/m9.figshare.{ITEM_ID}.v2',
        'url': API_URL,
        'adapter': 'figshare_public',
        'figshare_item_id': ITEM_ID,
        'files': [{
            'name': FILE_NAME, 'url': FILE_URL, 'source_url': API_URL,
            'figshare_file_id': FILE_ID, 'bytes': len(data), 'md5': md5,
        }],
    }
    catalog = root / 'catalog.json'
    catalog.write_text(json.dumps({'schema_version': 1, 'resources': [resource]}))
    receipt = {
        'schema_version': 1, 'resource_id': RESOURCE_ID, 'training_admitted': False,
        'catalog_sha256': hashlib.sha256(b'test-catalog').hexdigest(),
        'resource': resource,
        'files': [{**resource['files'][0], 'sha256': sha256,
                   'source_checksum_verified': True}],
    }
    (sample / 'receipt.json').write_text(json.dumps(receipt))
    return sample, catalog


class MonkParakeetSelectionAuditTests(unittest.TestCase):
    def test_reproduces_aggregate_cross_scale_exclusion_without_row_leakage(self):
        with tempfile.TemporaryDirectory() as temp:
            sample, catalog = build_fixture(Path(temp), [
                {'sound.files': 'private_individual.wav', 'selec': '1',
                 'social_scale': 'Individual', 'Bird_ID': 'PRIVATE_BIRD',
                 'lat': '40.1', 'lon': '2.2', 'notes': 'PRIVATE_NOTE'},
                {'sound.files': 'private_site_scale.wav', 'selec': '1',
                 'social_scale': 'Site', 'Bird_ID': 'PRIVATE_BIRD',
                 'lat': '40.1', 'lon': '2.2', 'notes': 'PRIVATE_NOTE'},
                {'sound.files': 'other_site_scale.wav', 'selec': '2',
                 'social_scale': 'Site', 'Bird_ID': 'OTHER_BIRD',
                 'lat': '41.1', 'lon': '3.2', 'notes': 'OTHER_NOTE'},
                {'sound.files': 'ordinary_site.wav', 'selec': '3',
                 'social_scale': 'Site', 'Bird_ID': 'OTHER_BIRD',
                 'lat': '42.1', 'lon': '4.2', 'notes': 'OTHER_NOTE'},
            ])
            result = inspect(sample, catalog)
            self.assertEqual(result['selection_table_rows'], 4)
            self.assertEqual(result['rows_by_social_scale'], {'Individual': 1, 'Site': 3})
            self.assertEqual(result['site_scale_rows_with_site_scale_filename_suffix'], 2)
            self.assertEqual(result['site_scale_suffix_rows_for_ids_also_in_individual_scale'], 1)
            self.assertEqual(result['rows_after_applying_the_pinned_cross_scale_exclusion'], 3)
            self.assertFalse(result['training_admitted'])
            rendered = json.dumps(result)
            for secret in ('PRIVATE_BIRD', 'OTHER_BIRD', 'private_individual.wav',
                           'private_site_scale.wav', '40.1', '2.2', 'PRIVATE_NOTE'):
                self.assertNotIn(secret, rendered)

    def test_receipt_hash_mismatch_stops_inspection(self):
        with tempfile.TemporaryDirectory() as temp:
            sample, catalog = build_fixture(Path(temp), [
                {'sound.files': 'private_individual.wav', 'selec': '1',
                 'social_scale': 'Individual', 'Bird_ID': 'PRIVATE_BIRD',
                 'lat': '40.1', 'lon': '2.2', 'notes': 'PRIVATE_NOTE'},
                {'sound.files': 'private_site_scale.wav', 'selec': '1',
                 'social_scale': 'Site', 'Bird_ID': 'PRIVATE_BIRD',
                 'lat': '40.1', 'lon': '2.2', 'notes': 'PRIVATE_NOTE'},
            ])
            (sample / FILE_NAME).write_text('tampered')
            with self.assertRaisesRegex(ValueError, 'differs from its provider'):
                inspect(sample, catalog)


if __name__ == '__main__':
    unittest.main()
