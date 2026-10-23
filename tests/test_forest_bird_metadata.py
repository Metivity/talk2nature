import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.audit_forest_bird_metadata import audit
from talk2nature.collection import CATALOG


class ForestBirdMetadataAuditTests(unittest.TestCase):
    def _write_csv(self, path, fields, rows):
        with path.open('w', encoding='utf-8', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def test_aggregate_report_reconciles_counts_without_exporting_sites_or_coordinates(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            catalog_path = root / 'resources.json'
            sample_dir = root / 'sample'
            sample_dir.mkdir()
            catalog = json.loads(CATALOG.read_text())
            resource = next(item for item in catalog['resources']
                            if item['id'] == 'northeastern-forest-bird-metadata-sample-v2')
            data = {
                'ReadMe.txt': b'Total 10-minute recordings: **2**\nTotal recording locations: **2**\nTotal species recorded: **1**\n',
                'site_metadata.csv': (
                    b'ParkID,SiteID,Latitude,Longitude\nACAD,PRIVATE_SITE_A,44.1,-68.2\n'
                    b'HBEF,PRIVATE_SITE_B,43.9,-71.7\n'),
                'recording_metadata.csv': (
                    b'Dataset_ID,SiteID,ParkID,Year\nACAD,PRIVATE_SITE_A,ACAD,2022\n'
                    b'MABI,PRIVATE_SITE_B,HBEF,2023\n'),
                'species_metadata.csv': (
                    b'IsBird,N_DatasetACAD,N_DatasetMABI,N_DatasetSIMR\nYes,2,3,0\n'
                    b'No,0,0,0\n'),
            }
            for artifact in resource['files']:
                contents = data[artifact['name']]
                artifact['bytes'] = len(contents)
                artifact['md5'] = hashlib.md5(contents, usedforsecurity=False).hexdigest()
                (sample_dir / artifact['name']).write_bytes(contents)
            catalog_path.write_text(json.dumps(catalog), encoding='utf-8')
            receipt_files = []
            for artifact in resource['files']:
                contents = data[artifact['name']]
                receipt_files.append({
                    **artifact,
                    'sha256': hashlib.sha256(contents).hexdigest(),
                    'source_checksum_verified': True,
                })
            (sample_dir / 'receipt.json').write_text(json.dumps({
                'schema_version': 1,
                'resource_id': resource['id'],
                'resource': resource,
                'training_admitted': False,
                'files': receipt_files,
            }), encoding='utf-8')

            report = audit(sample_dir, catalog_path)
            rendered = json.dumps(report)
            self.assertEqual(report['sites']['unique_site_ids'], 2)
            self.assertEqual(report['sites']['recording_metadata_unique_site_ids'], 2)
            self.assertTrue(report['sites']['site_sets_match'])
            self.assertEqual(report['sites']['counts_by_park'], {'ACAD': 1, 'HBEF': 1})
            self.assertEqual(report['recordings']['rows'], 2)
            self.assertEqual(report['species']['bird_rows_with_yes_flag'], 1)
            self.assertEqual(report['species']['bird_rows_with_nonzero_annotations'], 1)
            self.assertEqual(report['species']['annotation_total_for_yes_rows'], 5)
            self.assertEqual(report['readme_totals'], {
                'recordings': 2, 'locations': 2, 'species': 1,
            })
            self.assertFalse(report['sites']['coordinate_values_exported'])
            self.assertNotIn('PRIVATE_SITE_A', rendered)
            self.assertNotIn('PRIVATE_SITE_B', rendered)
            self.assertNotIn('44.1', rendered)
            self.assertNotIn('-68.2', rendered)

    def test_audit_rejects_changed_sample_bytes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            catalog_path = root / 'resources.json'
            sample_dir = root / 'sample'
            sample_dir.mkdir()
            catalog = json.loads(CATALOG.read_text())
            resource = next(item for item in catalog['resources']
                            if item['id'] == 'northeastern-forest-bird-metadata-sample-v2')
            catalog_path.write_text(json.dumps(catalog), encoding='utf-8')
            (sample_dir / 'receipt.json').write_text(json.dumps({
                'schema_version': 1,
                'resource_id': resource['id'],
                'resource': resource,
                'training_admitted': False,
                'files': [],
            }), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'exactly the four reviewed'):
                audit(sample_dir, catalog_path)


if __name__ == '__main__':
    unittest.main()
