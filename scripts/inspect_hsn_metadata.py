"""Audit HSN annotation grouping while keeping recordings and coordinates closed.

Only the annotation CSV and coarse location text are fetched into memory. The
script verifies their pinned Zenodo checksums, emits aggregate metadata only,
and never writes source files, row labels, or coordinate values.
"""
import argparse
import csv
import hashlib
import io
import json
import re
import ssl
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / 'research/hsn_metadata_report.json'
RECORD_ID = 7525805
DOI = '10.5281/zenodo.7525805'
API_URL = f'https://zenodo.org/api/records/{RECORD_ID}'
MAX_API_BYTES = 1024 * 1024
MAX_DATA_BYTES = 1024 * 1024
EXPECTED_MANIFEST = {
    'annotations.csv': {
        'size': 631187,
        'checksum': 'md5:0f300f5536784cc34f51f9f42e80756e',
    },
    'recording_location.txt': {
        'size': 105,
        'checksum': 'md5:bf5aae95885ee85fcdcc0a408e45bfe9',
    },
}
EXPECTED_COLUMNS = (
    'Filename', 'Start Time (s)', 'End Time (s)', 'Low Freq (Hz)',
    'High Freq (Hz)', 'Species eBird Code',
)
FILENAME_RE = re.compile(r'^HSN_(\d{3})_(\d{8})_(\d{6})\.flac$')
COORDINATE_RE = re.compile(r'(?im)^\s*(?:lat|latitude)\s*:\s*(-?\d+(?:\.\d+)?)\s*$')


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('Unexpected redirect from the pinned Zenodo source.')


def _opener(ca_file=None):
    context = ssl.create_default_context(cafile=ca_file)
    return urllib.request.build_opener(
        NoRedirect(), urllib.request.HTTPSHandler(context=context))


def _read(opener, url, maximum, content_types):
    parsed = urlsplit(url)
    if (parsed.scheme != 'https' or parsed.hostname != 'zenodo.org'
            or parsed.username or parsed.password or parsed.port not in (None, 443)
            or parsed.query or parsed.fragment):
        raise ValueError('Source URL is outside the pinned Zenodo origin.')
    request = urllib.request.Request(url, headers={
        'User-Agent': 'Talk2Nature-metadata-audit/1',
        'Accept-Encoding': 'identity',
    })
    try:
        with opener.open(request, timeout=30) as response:
            if response.status != 200 or response.geturl() != url:
                raise ValueError('Unexpected source response.')
            if response.headers.get('Content-Encoding', 'identity') != 'identity':
                raise ValueError('Encoded source response refused.')
            content_type = response.headers.get('Content-Type', '').split(';', 1)[0].lower()
            if content_type not in content_types:
                raise ValueError('Unexpected source content type.')
            declared = response.headers.get('Content-Length')
            if declared is not None and int(declared) > maximum:
                raise ValueError('Source exceeds the inspection limit.')
            data = response.read(maximum + 1)
    except ValueError:
        raise
    except Exception:
        raise ValueError('Pinned Zenodo source request failed.') from None
    if len(data) > maximum:
        raise ValueError('Source exceeds the inspection limit.')
    return data


def _record(opener):
    raw = _read(opener, API_URL, MAX_API_BYTES, {'application/json'})
    try:
        record = json.loads(raw)
    except (ValueError, UnicodeDecodeError):
        raise ValueError('Zenodo metadata is not valid JSON.') from None
    if not isinstance(record, dict):
        raise ValueError('Zenodo metadata is not a record object.')
    metadata = record.get('metadata')
    license_record = metadata.get('license') if isinstance(metadata, dict) else None
    if (record.get('id') != RECORD_ID
            or str(record.get('doi', '')).casefold() != DOI.casefold()
            or not isinstance(license_record, dict)
            or license_record.get('id') != 'cc-by-4.0'):
        raise ValueError('Zenodo record identity, DOI, or CC BY 4.0 declaration changed.')
    creators = metadata.get('creators', [])
    creator_names = [creator.get('name') for creator in creators if isinstance(creator, dict)]
    if not {'Mary Clapp', 'Gail Patricelli'}.issubset(set(creator_names)):
        raise ValueError('Expected dataset attribution is missing from the Zenodo record.')
    files = record.get('files')
    if not isinstance(files, list):
        raise ValueError('Zenodo file manifest is missing.')
    by_key = {item.get('key'): item for item in files if isinstance(item, dict)}
    selected = {}
    for key, expected in EXPECTED_MANIFEST.items():
        item = by_key.get(key)
        links = item.get('links') if isinstance(item, dict) else None
        expected_url = f'{API_URL}/files/{key}/content'
        if (not isinstance(item, dict) or item.get('size') != expected['size']
                or item.get('checksum') != expected['checksum']
                or not isinstance(links, dict) or links.get('self') != expected_url):
            raise ValueError(f'Pinned Zenodo manifest changed for {key}.')
        selected[key] = item
    return record, selected


def _data(opener, item, key):
    url = item['links']['self']
    data = _read(opener, url, MAX_DATA_BYTES,
                 {'text/csv', 'text/plain', 'application/octet-stream'})
    expected = EXPECTED_MANIFEST[key]
    if (len(data) != expected['size']
            or hashlib.md5(data).hexdigest() != expected['checksum'].split(':', 1)[1]):
        raise ValueError(f'Pinned Zenodo checksum mismatch for {key}.')
    return data


def _location_summary(data):
    text = data.decode('utf-8-sig')
    latitude_count = len(COORDINATE_RE.findall(text))
    longitude_count = len(re.findall(
        r'(?im)^\s*(?:lon|longitude)\s*:\s*-?\d+(?:\.\d+)?\s*$', text))
    return {
        'approximate_coordinate_pairs': min(latitude_count, longitude_count),
        'per_recording_or_lake_key_present': False,
        'coordinate_values_retained_or_reported': False,
        'mapping_assessment': 'One coarse regional point is not a recording-to-lake crosswalk.',
    }


def _annotation_summary(data):
    try:
        text = data.decode('utf-8-sig')
        reader = csv.DictReader(io.StringIO(text))
        if tuple(reader.fieldnames or ()) != EXPECTED_COLUMNS:
            raise ValueError('Annotation CSV columns differ from the reviewed schema.')
        total = 0
        identified = 0
        unidentified = 0
        non_numeric_intervals = 0
        zero_duration_intervals = 0
        reversed_or_negative_time = 0
        out_of_clip_intervals = 0
        invalid_frequency_intervals = 0
        all_classes = set()
        files_by_date = defaultdict(set)
        rows_by_date = Counter()
        class_dates = defaultdict(set)
        seen_rows = set()
        for row in reader:
            if None in row or any(value is None for value in row.values()):
                raise ValueError('Malformed annotation row.')
            match = FILENAME_RE.fullmatch(row['Filename'].strip())
            if not match:
                raise ValueError('Unexpected HSN filename schema.')
            _, date_token, _ = match.groups()
            label = row['Species eBird Code'].strip()
            try:
                start, end = float(row['Start Time (s)']), float(row['End Time (s)'])
                low, high = float(row['Low Freq (Hz)']), float(row['High Freq (Hz)'])
                if start == end:
                    zero_duration_intervals += 1
                elif start > end or start < 0:
                    reversed_or_negative_time += 1
                if end > 600:
                    out_of_clip_intervals += 1
                if low < 0 or high < low:
                    invalid_frequency_intervals += 1
            except (TypeError, ValueError):
                non_numeric_intervals += 1
            key = (row['Filename'], row['Start Time (s)'], row['End Time (s)'],
                   row['Low Freq (Hz)'], row['High Freq (Hz)'], label)
            if key in seen_rows:
                raise ValueError('Duplicate annotation row detected.')
            seen_rows.add(key)
            total += 1
            rows_by_date[date_token] += 1
            files_by_date[date_token].add(row['Filename'])
            if not label or label == '????':
                unidentified += 1
            else:
                identified += 1
                all_classes.add(label)
                class_dates[label].add(date_token)
    except UnicodeDecodeError:
        raise ValueError('Annotation CSV is not UTF-8 text.') from None

    date_records = {
        f'{token[:4]}-{token[4:6]}-{token[6:]}': {
            'recordings': len(files_by_date[token]),
            'annotation_rows': rows_by_date[token],
        }
        for token in sorted(files_by_date)
    }
    class_support = Counter(len(days) for days in class_dates.values())
    return {
        'columns': list(EXPECTED_COLUMNS),
        'annotation_rows': total,
        'identified_species_codes': len(all_classes),
        'identified_species_rows': identified,
        'unknown_or_unidentified_rows': unidentified,
        'recordings': sum(len(names) for names in files_by_date.values()),
        'filename_date_groups': date_records,
        'species_date_support_histogram': {
            str(count): class_support[count] for count in sorted(class_support)
        },
        'interval_structure': {
            'zero_duration_intervals': zero_duration_intervals,
            'reversed_or_negative_time': reversed_or_negative_time,
            'end_after_600_seconds': out_of_clip_intervals,
            'negative_or_reversed_frequency': invalid_frequency_intervals,
            'non_numeric_interval_fields': non_numeric_intervals,
        },
        'row_level_labels_reported': False,
    }


def inspect(opener=None):
    opener = opener or _opener()
    record, files = _record(opener)
    annotation_bytes = _data(opener, files['annotations.csv'], 'annotations.csv')
    location_bytes = _data(opener, files['recording_location.txt'], 'recording_location.txt')
    annotation = _annotation_summary(annotation_bytes)
    location = _location_summary(location_bytes)
    return {
        'dataset': {
            'title': 'A collection of fully-annotated soundscape recordings from the southern Sierra Nevada mountain range',
            'doi': DOI,
            'zenodo_record_id': RECORD_ID,
            'license': 'CC BY 4.0',
            'attribution': ', '.join(
                creator.get('name', '') for creator in record['metadata']['creators']
                if isinstance(creator, dict) and creator.get('name')),
            'manifest_sha256_basis': 'Zenodo API MD5 checksums verified for the two in-memory metadata files.',
            'files_reviewed': [
                {'name': key, 'bytes': EXPECTED_MANIFEST[key]['size'],
                 'md5': EXPECTED_MANIFEST[key]['checksum'].split(':', 1)[1]}
                for key in ('annotations.csv', 'recording_location.txt')
            ],
        },
        'annotations': annotation,
        'location': location,
        'source_description_comparison': {
            'source_reported_recordings': 100,
            'source_reported_known_species': 21,
            'source_reported_known_species_boxes': 10296,
            'source_reported_sample_window': 'July 9-12, 2015',
            'annotation_csv_has_extra_undetermined_labels': (
                annotation['unknown_or_unidentified_rows'] == 680
                and annotation['identified_species_rows'] == 10296
            ),
            'filename_dates_outside_reported_window': {
                day: data for day, data in annotation['filename_date_groups'].items()
                if day < '2015-07-09' or day > '2015-07-12'
            },
        },
        'assessment': {
            'site_held_out_evaluation_supported': False,
            'reason': 'The published location text gives one coarse point, not a file-to-lake/site crosswalk.',
            'date_grouped_evaluation': (
                f"Filename dates are available for {len(annotation['filename_date_groups'])} groups; "
                'this is not a site holdout. Resolve source-date provenance and prior benchmark overlap first.'
            ),
            'audio_acquired_or_opened': False,
            'model_or_embedding_run': False,
            'coordinates_reported': False,
            'training_admitted': False,
        },
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument('--ca-file', type=Path,
                        help='Optional local CA bundle if the system certificate store needs one.')
    args = parser.parse_args()
    report = inspect(_opener(args.ca_file))
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'report': str(args.output), 'assessment': report['assessment'],
                      'annotations': report['annotations'],
                      'location': report['location']}, indent=2))
