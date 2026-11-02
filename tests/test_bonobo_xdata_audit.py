import hashlib
import json
import unittest

from scripts.inspect_bonobo_xdata import (
    EXPECTED_ROWS,
    METADATA_HEADERS,
    RESOURCE_ID,
    inspect_payload,
)


def fixture_payload(*, malformed_row=False):
    headers = list(METADATA_HEADERS) + [f'feature_{index}' for index in range(1, 337)]
    lines = ['\t'.join(headers)]
    row = ['ROWVALUE_PRIVATE_7E91'] * 343
    for _ in range(EXPECTED_ROWS):
        current = row[:-1] if malformed_row else row
        lines.append('\t'.join(current))
    return ('\n'.join(lines) + '\n').encode()


def fixture_receipt(raw):
    return {
        'resource_id': RESOURCE_ID,
        'training_admitted': False,
        'files': [{
            'name': 'xdata.txt',
            'bytes': len(raw),
            'md5': hashlib.md5(raw).hexdigest(),
            'sha256': hashlib.sha256(raw).hexdigest(),
        }],
    }


class BonoboXdataAuditTests(unittest.TestCase):
    def test_reports_only_shape_and_confirms_pinned_script_layout(self):
        raw = fixture_payload()
        receipt = fixture_receipt(raw)
        report = inspect_payload(
            raw, receipt,
            expected_md5=hashlib.md5(raw).hexdigest(),
            expected_sha256=hashlib.sha256(raw).hexdigest(),
            expected_bytes=len(raw),
        )
        self.assertEqual(report['structure']['data_rows'], 735)
        self.assertEqual(report['structure']['columns'], 343)
        self.assertEqual(report['structure']['feature_columns'], 336)
        self.assertTrue(report['structure']['required_header_positions_match'])
        self.assertFalse(report['scope']['raw_row_values_emitted'])
        self.assertNotIn('ROWVALUE_PRIVATE_7E91', json.dumps(report))

    def test_rejects_receipt_or_byte_mismatch(self):
        raw = fixture_payload()
        receipt = fixture_receipt(raw)
        with self.assertRaisesRegex(ValueError, 'bytes differ'):
            inspect_payload(raw + b'\n', receipt)
        receipt['resource_id'] = 'other-source'
        with self.assertRaisesRegex(ValueError, 'Receipt does not identify'):
            inspect_payload(raw, receipt,
                            expected_md5=hashlib.md5(raw).hexdigest(),
                            expected_sha256=hashlib.sha256(raw).hexdigest(),
                            expected_bytes=len(raw))

    def test_rejects_nonuniform_row_widths(self):
        raw = fixture_payload(malformed_row=True)
        with self.assertRaisesRegex(ValueError, 'rows do not match'):
            inspect_payload(raw, fixture_receipt(raw),
                            expected_md5=hashlib.md5(raw).hexdigest(),
                            expected_sha256=hashlib.sha256(raw).hexdigest(),
                            expected_bytes=len(raw))


if __name__ == '__main__':
    unittest.main()
