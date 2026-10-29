import copy
import csv
import hashlib
import io
import json
import unittest
from unittest.mock import Mock, patch

from scripts import inspect_hsn_metadata as audit


class Response(io.BytesIO):
    status = 200

    def __init__(self, data, url, content_type):
        super().__init__(data)
        self.url = url
        self.headers = {'Content-Type': content_type, 'Content-Length': str(len(data))}

    def geturl(self):
        return self.url


def fixture():
    output = io.StringIO(newline='')
    writer = csv.writer(output, lineterminator='\n')
    writer.writerow(audit.EXPECTED_COLUMNS)
    writer.writerows([
        ['HSN_001_20150709_061000.flac', '1.0', '1.0', '900', '2400', 'SP_TEST'],
        ['HSN_002_20150709_062000.flac', '5.0', '6.0', '1100', '3000', '????'],
        ['HSN_003_20150710_063000.flac', '8.0', '9.0', '800', '2500', 'SP_TEST'],
    ])
    annotation_bytes = output.getvalue().encode()
    location_bytes = b'High Sierra coarse region\nLat: 37.0\nLon: -118.5\n'
    bodies = {'annotations.csv': annotation_bytes,
              'recording_location.txt': location_bytes}
    manifest = {}
    files = []
    for key, data in bodies.items():
        checksum = 'md5:' + hashlib.md5(data).hexdigest()
        manifest[key] = {'size': len(data), 'checksum': checksum}
        files.append({
            'key': key,
            'size': len(data),
            'checksum': checksum,
            'links': {'self': f'{audit.API_URL}/files/{key}/content'},
        })
    record = {
        'id': audit.RECORD_ID,
        'doi': audit.DOI,
        'metadata': {
            'license': {'id': 'cc-by-4.0'},
            'creators': [{'name': name} for name in
                         ('Mary Clapp', 'Stefan Kahl', 'Erik Meyer', 'Megan McKenna',
                          'Holger Klinck', 'Gail Patricelli')],
        },
        'files': files,
    }
    opener = Mock()

    def open_request(request, timeout):
        url = request.full_url
        if url == audit.API_URL:
            return Response(json.dumps(record).encode(), url, 'application/json')
        for key, data in bodies.items():
            if url == f'{audit.API_URL}/files/{key}/content':
                return Response(data, url,
                                'text/csv' if key.endswith('.csv') else 'text/plain')
        raise AssertionError('Unexpected request URL')

    opener.open.side_effect = open_request
    return record, manifest, bodies, opener


class HsnMetadataAuditTests(unittest.TestCase):
    def test_aggregate_metadata_is_verified_and_coordinates_are_not_reported(self):
        record, manifest, _, opener = fixture()
        with patch.dict(audit.EXPECTED_MANIFEST, manifest, clear=True):
            report = audit.inspect(opener)

        self.assertEqual(report['annotations']['recordings'], 3)
        self.assertEqual(report['annotations']['annotation_rows'], 3)
        self.assertEqual(report['annotations']['identified_species_codes'], 1)
        self.assertEqual(report['annotations']['identified_species_rows'], 2)
        self.assertEqual(report['annotations']['unknown_or_unidentified_rows'], 1)
        self.assertEqual(report['annotations']['species_date_support_histogram'], {'2': 1})
        self.assertEqual(report['annotations']['interval_structure']['zero_duration_intervals'], 1)
        self.assertEqual(report['location']['approximate_coordinate_pairs'], 1)
        self.assertFalse(report['location']['per_recording_or_lake_key_present'])
        self.assertFalse(report['location']['coordinate_values_retained_or_reported'])
        self.assertFalse(report['assessment']['site_held_out_evaluation_supported'])
        serialized = json.dumps(report)
        for value in ('37.0', '-118.5', 'SP_TEST', 'HSN_001_20150709_061000.flac'):
            self.assertNotIn(value, serialized)

    def test_non_cc_by_record_and_manifest_change_are_rejected(self):
        record, manifest, _, opener = fixture()
        with patch.dict(audit.EXPECTED_MANIFEST, manifest, clear=True):
            record['metadata']['license']['id'] = 'cc-by-nc-4.0'
            with self.assertRaisesRegex(ValueError, 'CC BY 4.0 declaration changed'):
                audit.inspect(opener)

            record, manifest, _, opener = fixture()
            record['files'][0]['checksum'] = 'md5:' + '0' * 32
            with self.assertRaisesRegex(ValueError, 'manifest changed'):
                audit.inspect(opener)

    def test_csv_schema_and_receipt_bytes_are_pinned(self):
        record, manifest, bodies, opener = fixture()
        bodies['annotations.csv'] = b'wrong,columns\n'
        updated = copy.deepcopy(record)
        data = bodies['annotations.csv']
        updated['files'][0]['size'] = len(data)
        updated['files'][0]['checksum'] = 'md5:' + hashlib.md5(data).hexdigest()
        expected = dict(manifest)
        expected['annotations.csv'] = {
            'size': len(data), 'checksum': updated['files'][0]['checksum']}
        opener.open.side_effect = lambda request, timeout: (
            Response(json.dumps(updated).encode(), request.full_url, 'application/json')
            if request.full_url == audit.API_URL else
            Response(data if request.full_url.endswith('/annotations.csv/content')
                     else bodies['recording_location.txt'], request.full_url,
                     'text/csv' if request.full_url.endswith('/annotations.csv/content')
                     else 'text/plain'))
        with patch.dict(audit.EXPECTED_MANIFEST, expected, clear=True):
            with self.assertRaisesRegex(ValueError, 'columns differ from the reviewed schema'):
                audit.inspect(opener)


if __name__ == '__main__':
    unittest.main()
