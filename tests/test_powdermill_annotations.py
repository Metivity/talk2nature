import csv
import hashlib
import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts.inspect_powdermill_annotations import EXPECTED_FIELDS, inspect


class PowdermillAnnotationInspectionTests(unittest.TestCase):
    def write_fixture(self, folder, members=None):
        members = members or {
            'Recording_1/Recording_1_Segment_01.Table.1.selections.txt': [
                ['1', 'Spectrogram 1', '1', '1.2', '2.1', '1000', '3000',
                 'SYNTHETIC_SECRET_TAXON'],
                ['2', 'Spectrogram 1', '1', '4.0', '4.8', '900', '2400', '????'],
            ],
            'Recording_2/Recording_2_Segment_01.Table.1.selections.txt': [],
        }
        raw = io.BytesIO()
        with zipfile.ZipFile(raw, 'w', zipfile.ZIP_DEFLATED) as archive:
            for name, rows in members.items():
                output = io.StringIO(newline='')
                writer = csv.writer(output, delimiter='\t', lineterminator='\n')
                writer.writerow(EXPECTED_FIELDS)
                writer.writerows(rows)
                archive.writestr(name, output.getvalue())
        data = raw.getvalue()
        (folder / 'annotation_Files.zip').write_bytes(data)
        receipt = {
            'resource_id': 'powdermill-bird-soundscapes',
            'training_admitted': False,
            'resource': {'version': 'synthetic fixture'},
            'files': [{
                'name': 'annotation_Files.zip',
                'url': 'https://zenodo.org/api/records/4656848/files/annotation_Files.zip/content',
                'sha256': hashlib.sha256(data).hexdigest(),
            }],
        }
        (folder / 'receipt.json').write_text(json.dumps(receipt))

    def test_aggregate_report_preserves_groups_and_does_not_publish_rows(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            self.write_fixture(folder)
            report = inspect(folder)

        self.assertEqual(report['recording_group_count'], 2)
        self.assertEqual(report['archive_members'], 2)
        self.assertEqual(report['annotation_count'], 2)
        self.assertEqual(report['unknown_or_blank_labels'], 1)
        self.assertEqual(report['empty_annotation_segments'], 1)
        self.assertEqual(report['unique_identified_species_codes'], 1)
        self.assertEqual(report['species_group_support_histogram'], {'1': 1})
        self.assertFalse(report['audio_opened'])
        self.assertFalse(report['training_admitted'])
        serialized = json.dumps(report)
        self.assertNotIn('SYNTHETIC_SECRET_TAXON', serialized)
        self.assertNotIn('1.2', serialized)

    def test_receipt_checksum_must_match_archive(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            self.write_fixture(folder)
            receipt_path = folder / 'receipt.json'
            receipt = json.loads(receipt_path.read_text())
            receipt['files'][0]['sha256'] = '0' * 64
            receipt_path.write_text(json.dumps(receipt))
            with self.assertRaisesRegex(ValueError, 'differs from its acquisition receipt'):
                inspect(folder)

    def test_audio_or_unexpected_members_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            self.write_fixture(folder, {
                'Recording_1/audio.wav': [],
            })
            with self.assertRaisesRegex(ValueError, 'Unexpected path or non-annotation'):
                inspect(folder)


if __name__ == '__main__':
    unittest.main()
