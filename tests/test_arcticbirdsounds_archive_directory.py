import io
import struct
import unittest
import zipfile

from scripts import inspect_arcticbirdsounds_archive_directory as audit


def archive_fixture():
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('clips/2018 TESTPLOT 20180601-120000 1.flac', b'fixture audio bytes')
        archive.writestr('annotations/2018 TESTPLOT 20180601-120000 1-tags.csv', b'fixture label bytes')
        archive.writestr('clips/2018 TESTPLOT 20180601-120000 2.flac', b'fixture audio bytes')
        archive.writestr('annotations/2018 TESTPLOT 20180601-120000 2-tags.csv', b'fixture label bytes')
        archive.writestr('metadata/readme.csv', b'fixture metadata')
        archive.writestr('empty-folder/', b'')
    payload = buffer.getvalue()
    eocd_pos = payload.rfind(b'PK\x05\x06')
    fields = struct.unpack_from('<4s4H2LH', payload, eocd_pos)
    entry_count, directory_size, directory_offset = fields[4], fields[5], fields[6]
    tail_size = min(audit.MAX_TAIL_BYTES, len(payload))
    tail = payload[-tail_size:]
    central = payload[directory_offset:directory_offset + directory_size]
    return len(payload), tail, central, entry_count


class FakeResponse:
    def __init__(self, status, headers, body=b'', url='https://files.osf.io/sample'):
        self.status = status
        self.headers = headers
        self.body = body
        self.url = url
        self.read_calls = 0
        self.closed = False

    def geturl(self):
        return self.url

    def read(self, maximum=-1):
        self.read_calls += 1
        return self.body[:maximum]

    def close(self):
        self.closed = True


class FakeOpener:
    def __init__(self, response):
        self.response = response
        self.open_calls = 0

    def open(self, request, timeout=None):
        self.open_calls += 1
        self.request = request
        return self.response


class ArcticBirdSoundsArchiveDirectoryTests(unittest.TestCase):
    def test_directory_summary_counts_schema_pairs_without_emitting_names(self):
        size, tail, central, entry_count = archive_fixture()
        layout = audit._directory_layout(tail, size)
        self.assertEqual(layout[0], entry_count)
        report = audit._summarize_central_directory(central, entry_count)
        self.assertEqual(report['files'], 5)
        self.assertEqual(report['directories'], 1)
        self.assertEqual(report['suffix_counts']['.csv'], 3)
        self.assertEqual(report['schema_valid_filename_counts']['.csv'], 2)
        self.assertEqual(report['schema_valid_filename_counts']['.flac'], 2)
        self.assertEqual(report['csv_flac_intersection_unique_keys'], 2)
        self.assertEqual(report['unique_csv_keys_missing_flac'], 0)
        self.assertEqual(report['unique_flac_keys_missing_csv'], 0)
        self.assertEqual(report['csv_entries_outside_published_filename_schema'], 1)
        self.assertNotIn('readme.csv', repr(report))
        self.assertNotIn('TESTPLOT', repr(report))

    def test_malformed_central_directory_is_rejected(self):
        with self.assertRaises(ValueError):
            audit._summarize_central_directory(b'not a central directory', 0)

    def test_directory_entry_count_mismatch_is_rejected(self):
        _, _, central, entry_count = archive_fixture()
        with self.assertRaises(ValueError):
            audit._summarize_central_directory(central, entry_count + 1)

    def test_range_request_requires_exact_partial_response_before_reading(self):
        response = FakeResponse(
            200, {'Content-Length': '100'}, b'x' * 100)
        opener = FakeOpener(response)
        with self.assertRaises(ValueError):
            audit._range_read(opener, 'https://files.osf.io/sample', 0, 9, 100)
        self.assertEqual(response.read_calls, 0)
        self.assertTrue(response.closed)

    def test_range_request_rejects_untrusted_origin_before_network(self):
        response = FakeResponse(206, {}, b'0123456789')
        opener = FakeOpener(response)
        with self.assertRaises(ValueError):
            audit._range_read(opener, 'http://example.com/sample', 0, 9, 100)
        self.assertEqual(opener.open_calls, 0)

    def test_exact_range_response_is_bounded_and_read(self):
        body = b'0123456789'
        response = FakeResponse(
            206,
            {'Content-Range': 'bytes 0-9/100', 'Content-Length': '10', 'Content-Encoding': 'identity'},
            body,
        )
        opener = FakeOpener(response)
        self.assertEqual(audit._range_read(opener, 'https://files.osf.io/sample', 0, 9, 100), body)
        self.assertEqual(opener.request.get_header('Range'), 'bytes=0-9')
        self.assertEqual(response.read_calls, 1)
        self.assertTrue(response.closed)


if __name__ == '__main__':
    unittest.main()
