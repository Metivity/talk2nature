import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.audit_parakeet_joins import audit


def write_sample(folder, resource_id, files, version='a' * 40):
    folder.mkdir()
    records = []
    for name, data in files.items():
        (folder / name).write_bytes(data)
        records.append({'name': name, 'bytes': len(data),
                        'sha256': hashlib.sha256(data).hexdigest(),
                        'url': f'https://example.test/{name}'})
    receipt = {'schema_version': 1, 'resource_id': resource_id,
               'resource': {'id': resource_id, 'version': version,
                            'files': records},
               'files': records, 'training_admitted': False}
    (folder / 'receipt.json').write_text(json.dumps(receipt))


def write_catalog(path, admitted=True):
    ids = ('monk-parakeet-annotations', 'monk-parakeet-selection-tables-2020',
           'monk-parakeet-code')
    status = 'conditional' if admitted else 'unresolved'
    resources = [{
        'id': resource_id,
        'kind': 'code' if resource_id == 'monk-parakeet-code' else 'dataset',
        **({'analysis_admission': 'approved' if admitted else 'not_admitted'}
           if resource_id != 'monk-parakeet-code' else {}),
        'acquisition': 'sample_approved' if admitted else 'metadata_only',
        'rights': {'license': 'MIT' if resource_id == 'monk-parakeet-code' else 'CC-BY-4.0',
                   'research_use': status, 'commercial_use': status,
                   'redistribution': status},
    } for resource_id in ids]
    path.write_text(json.dumps({'schema_version': 1, 'resources': resources}))
    return path


class ParakeetJoinAuditTests(unittest.TestCase):
    def test_mirrors_waveform_filter_and_left_join_without_leaking_source_text(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            catalog = write_catalog(root / 'catalog.json')
            annotations = root / 'annotations'
            selection = root / 'selection'
            loader = root / 'loader'
            csv_data = (
                'annotation_ref;bird;location;notes\n'
                '1;secretbird;secretplace;secretnote\n'
                '2;secretbird;secretplace;secretnote\n'
                '3;secretbird;secretplace;secretnote\n'
                '4;secretbird;secretplace;secretnote\n').encode()
            write_sample(annotations, 'monk-parakeet-annotations',
                         {'annotations-2020.csv': csv_data})
            header = 'Selection\tView\tAnnotation\n'
            table_a = (header + '1\tWaveform 1\t1\n2\tSpectrogram 1\t2\n'
                       '3\tWaveform 1\t3\n4\tWaveform 1\t3\n').encode()
            table_b = (header + '1\tWaveform 1\t1\n2\tWaveform 1\t5\n').encode()
            write_sample(selection, 'monk-parakeet-selection-tables-2020', {
                'LICENSE-MIT.txt': b'fixture license',
                '2020_a.txt': table_a,
                '2020_b.txt': table_b,
            })
            loader_code = b'filter(View == "Waveform 1")\nleft_join(annotation_ref)\n'
            write_sample(loader, 'monk-parakeet-loader-code', {
                'LICENSE-MIT.txt': b'fixture license',
                'load.selection.tables.R': loader_code,
            })
            result = audit(annotations, selection, loader, catalog)
            self.assertEqual(result['annotation_csv_rows'], 4)
            self.assertEqual(result['selection_table_files'], 2)
            self.assertEqual(result['selection_rows_all_views'], 6)
            self.assertEqual(result['selection_rows_waveform_1'], 5)
            self.assertEqual(result['unique_waveform_annotation_keys'], 3)
            self.assertEqual(result['annotation_refs_present'], 2)
            self.assertEqual(result['annotation_refs_unmatched_by_selection_tables'], 2)
            self.assertEqual(result['annotation_refs_found_in_multiple_files'], 1)
            self.assertEqual(result['annotation_refs_expanding_to_multiple_waveform_rows'], 2)
            self.assertEqual(result['waveform_rows_with_annotation_csv_match'], 4)
            self.assertEqual(result['annotation_version'], 'a' * 40)
            self.assertEqual(result['loader_code_version'], 'a' * 40)
            self.assertEqual(result['loader_code_sha256'], hashlib.sha256(loader_code).hexdigest())
            self.assertEqual(result['annotation_csv_sha256'], hashlib.sha256(csv_data).hexdigest())
            table_manifest = [
                {'name': '2020_a.txt', 'bytes': len(table_a),
                 'sha256': hashlib.sha256(table_a).hexdigest()},
                {'name': '2020_b.txt', 'bytes': len(table_b),
                 'sha256': hashlib.sha256(table_b).hexdigest()},
            ]
            expected_manifest_hash = hashlib.sha256(
                json.dumps(table_manifest, sort_keys=True, separators=(',', ':')).encode()
            ).hexdigest()
            self.assertEqual(result['selection_table_manifest_sha256'], expected_manifest_hash)
            self.assertRegex(result['analysis_script_sha256'], r'^[a-f0-9]{64}$')
            self.assertEqual(result['schema_version'], 2)
            self.assertFalse(result['training_admitted'])
            rendered = json.dumps(result)
            for secret in ('secretbird', 'secretplace', 'secretnote', '2020_a.txt', '2020_b.txt'):
                self.assertNotIn(secret, rendered)

    def test_receipt_mismatch_stops_the_audit(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            catalog = write_catalog(root / 'catalog.json')
            annotations = root / 'annotations'
            selection = root / 'selection'
            loader = root / 'loader'
            write_sample(annotations, 'monk-parakeet-annotations', {
                'annotations-2020.csv': b'annotation_ref;bird\n1;secret\n'})
            write_sample(selection, 'monk-parakeet-selection-tables-2020', {
                '2020_a.txt': b'Selection\tView\tAnnotation\n1\tWaveform 1\t1\n'})
            write_sample(loader, 'monk-parakeet-loader-code', {
                'load.selection.tables.R': b'pinned loader source'})
            (selection / '2020_a.txt').write_bytes(b'tampered')
            with self.assertRaisesRegex(ValueError, 'receipt'):
                audit(annotations, selection, loader, catalog)

    def test_source_snapshots_must_match(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            catalog = write_catalog(root / 'catalog.json')
            annotations = root / 'annotations'
            selection = root / 'selection'
            loader = root / 'loader'
            write_sample(annotations, 'monk-parakeet-annotations', {
                'annotations-2020.csv': b'annotation_ref;bird\n1;hidden\n'}, version='a' * 40)
            write_sample(selection, 'monk-parakeet-selection-tables-2020', {
                '2020_a.txt': b'Selection\tView\tAnnotation\n1\tWaveform 1\t1\n'}, version='a' * 40)
            write_sample(loader, 'monk-parakeet-loader-code', {
                'load.selection.tables.R': b'pinned loader source'}, version='b' * 40)
            with self.assertRaisesRegex(ValueError, 'do not share one snapshot'):
                audit(annotations, selection, loader, catalog)

    def test_unresolved_catalog_blocks_before_any_source_read(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            catalog = write_catalog(root / 'catalog.json', admitted=False)
            with self.assertRaisesRegex(ValueError, 'Processing is not admitted'):
                audit(root / 'missing-annotations', root / 'missing-tables',
                      root / 'missing-loader', catalog)


if __name__ == '__main__':
    unittest.main()
