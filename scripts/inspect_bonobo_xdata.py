#!/usr/bin/env python3
"""Checksum-pinned, row-value-free structure check for bonobo xdata.txt."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FILE = ROOT / 'data/external/bonobo-compositionality-original-dataset-figshare-v1/xdata.txt'
DEFAULT_RECEIPT = ROOT / 'data/external/bonobo-compositionality-original-dataset-figshare-v1/receipt.json'
DEFAULT_OUTPUT = ROOT / 'research/bonobo_xdata_structure_report.json'
RESOURCE_ID = 'bonobo-compositionality-original-dataset-figshare-v1'
EXPECTED_BYTES = 801667
EXPECTED_MD5 = '24bcbb0c1b4d98ad645168307cb4f500'
EXPECTED_SHA256 = '84ad7b48bb41cf55b4f92c5a2fcf57780ad5590b0b4d941684f3a843b1abd6a4'
EXPECTED_ROWS = 735
EXPECTED_COLUMNS = 343
FEATURE_COLUMNS = 336
METADATA_HEADERS = (
    'Recording', 'Combination', 'Caller', 'Group', 'Sex',
    'Duration_focal_sec', 'Number_call',
)


def inspect_payload(raw: bytes, receipt: dict, *, expected_md5: str = EXPECTED_MD5,
                    expected_sha256: str = EXPECTED_SHA256,
                    expected_bytes: int = EXPECTED_BYTES) -> dict:
    """Verify receipt and report aggregate shape without retaining row values."""
    if not isinstance(receipt, dict) or receipt.get('resource_id') != RESOURCE_ID:
        raise ValueError('Receipt does not identify the reviewed Figshare item.')
    if receipt.get('training_admitted') is not False:
        raise ValueError('This structural audit requires a non-training source receipt.')
    matching = [item for item in receipt.get('files', []) if item.get('name') == 'xdata.txt']
    if len(matching) != 1:
        raise ValueError('Receipt must contain exactly one xdata.txt file.')
    recorded = matching[0]

    md5 = hashlib.md5(raw).hexdigest()
    sha256 = hashlib.sha256(raw).hexdigest()
    if len(raw) != expected_bytes or md5 != expected_md5 or sha256 != expected_sha256:
        raise ValueError('xdata.txt bytes differ from the pinned reviewed file.')
    if (recorded.get('bytes') != len(raw) or recorded.get('md5') != md5
            or recorded.get('sha256') != sha256):
        raise ValueError('Receipt hashes or size do not match xdata.txt.')

    try:
        text = raw.decode('utf-8-sig')
        rows = csv.reader(io.StringIO(text, newline=''), delimiter='\t', strict=True)
        header = next(rows)
    except (UnicodeDecodeError, csv.Error, StopIteration) as exc:
        raise ValueError('xdata.txt is not a valid nonempty UTF-8 tab-delimited table.') from exc
    if (len(header) != EXPECTED_COLUMNS or len(set(header)) != len(header)
            or tuple(header[:len(METADATA_HEADERS)]) != METADATA_HEADERS):
        raise ValueError('xdata.txt does not match the reviewed 343-column script layout.')

    row_count = 0
    widths: Counter[int] = Counter()
    try:
        for row in rows:
            row_count += 1
            widths[len(row)] += 1
    except csv.Error as exc:
        raise ValueError('xdata.txt contains malformed tab-delimited rows.') from exc
    if row_count != EXPECTED_ROWS or widths != Counter({EXPECTED_COLUMNS: EXPECTED_ROWS}):
        raise ValueError('xdata.txt rows do not match the reviewed 735-by-343 layout.')

    return {
        'schema_version': 1,
        'resource_id': RESOURCE_ID,
        'file': {
            'name': 'xdata.txt',
            'bytes': len(raw),
            'provider_md5': md5,
            'sha256': sha256,
            'receipt_verified': True,
        },
        'structure': {
            'delimiter': 'tab',
            'data_rows': row_count,
            'columns': len(header),
            'metadata_columns': len(METADATA_HEADERS),
            'feature_columns': len(header) - len(METADATA_HEADERS),
            'uniform_row_width': True,
            'unique_headers': True,
            'required_header_positions_match': True,
            'matches_script_dimensions': True,
        },
        'comparison': {
            'critique_data_rows_reported': 735,
            'original_abstract_count_reported': 700,
            'released_table_matches_critique_count': True,
            'script_01_02_feature_columns': '8-343 (one-based in the original file)',
            'script_03_expected_input': 'read.delim xdata.txt; removes Recording; uses Combination, Caller, Group, Sex as categorical supplementary variables and Duration_focal_sec, Number_call as quantitative supplementary variables',
            'input_layout_match': 'The released header positions and dimensions match the pinned scripts; this does not establish scientific reproducibility.',
        },
        'scope': {
            'raw_row_values_emitted': False,
            'code_executed': False,
            'analysis_reproduced': False,
            'training_admitted': False,
            'private_server_admitted': False,
        },
        'limitations': [
            'This is a structural compatibility check, not an analysis or validation of labels, context, missingness mechanisms or scientific claims.',
            'The table has 735 rows, matching the PeerJ critique and script dimensions; the original abstract reports 700, and that publication-level discrepancy remains unresolved.',
            'The tagged weighted-MCA script sets nperm=100 while the paper reports 10,000 permutations and p=0.2597; no result was reproduced.',
            'No raw row values, exact animal identifiers or precise locations are emitted in this report.',
        ],
    }


def inspect_file(path: Path = DEFAULT_FILE, receipt_path: Path = DEFAULT_RECEIPT) -> dict:
    raw = path.read_bytes()
    receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
    return inspect_payload(raw, receipt)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=DEFAULT_FILE)
    parser.add_argument('--receipt', type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    report = inspect_file(args.input, args.receipt)
    args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'report': str(args.output), 'rows': report['structure']['data_rows'],
                      'columns': report['structure']['columns'],
                      'raw_row_values_emitted': False}, indent=2))


if __name__ == '__main__':
    main()
