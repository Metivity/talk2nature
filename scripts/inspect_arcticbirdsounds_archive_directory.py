"""Inspect only the bounded ZIP directory metadata for ArcticBirdSounds.

The script reads the OSF root/file APIs, the ZIP end record and central
directory using HTTP byte ranges. It never reads a compressed audio or
annotation payload and writes only aggregate counts. Embedded filenames and
location values remain transient in memory and are never printed or saved.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path, PurePosixPath
import re
import struct
import sys
from urllib.parse import urlsplit
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import inspect_arcticbirdsounds as metadata_audit

NODE_ID = 'b9trx'
ARCHIVE_NAME = 'DataS1.zip'
ARCHIVE_ID = '6414ae138604900fc4087a35'
ARCHIVE_SIZE = 1_326_435_558
ROOT_API = f'https://api.osf.io/v2/nodes/{NODE_ID}/files/osfstorage/?page%5Bsize%5D=100'
MAX_TAIL_BYTES = 131_072
MAX_CENTRAL_DIRECTORY_BYTES = 16 * 1024 * 1024
MAX_ENTRIES = 100_000
DEFAULT_OUTPUT = ROOT / 'research/arcticbirdsounds_archive_directory_report.json'
OBJECT_STORAGE_HOST = re.compile(
    r'^[a-z0-9-]+\.compat\.objectstorage\.us-ashburn-1\.oraclecloud\.com$')


def _trusted_download_url(url):
    parsed = urlsplit(url)
    if (parsed.scheme != 'https' or not parsed.hostname
            or parsed.username or parsed.password
            or parsed.port not in (None, 443) or parsed.fragment
            or not metadata_audit._trusted_host(parsed.hostname)):
        raise ValueError('Archive download URL is outside the pinned HTTPS origins.')
    return parsed


def _range_read(opener, url, start, end, total_size):
    parsed = _trusted_download_url(url)
    if (type(start) is not int or type(end) is not int or type(total_size) is not int
            or start < 0 or end < start or end >= total_size):
        raise ValueError('Invalid bounded byte range.')
    expected_length = end - start + 1
    request = urllib.request.Request(url, headers={
        'Range': f'bytes={start}-{end}',
        'Accept-Encoding': 'identity',
        'User-Agent': 'Talk2Nature-archive-metadata-audit/1',
    })
    response = None
    try:
        response = opener.open(request, timeout=45)
        final = urlsplit(response.geturl())
        if (response.status != 206 or final.scheme != 'https'
                or not final.hostname or not metadata_audit._trusted_host(final.hostname)
                or final.username or final.password or final.port not in (None, 443)):
            raise ValueError('Server did not honor the bounded range at a trusted HTTPS origin.')
        if response.headers.get('Content-Encoding', 'identity') != 'identity':
            raise ValueError('Encoded archive range refused.')
        expected_range = f'bytes {start}-{end}/{total_size}'
        if response.headers.get('Content-Range') != expected_range:
            raise ValueError('Archive Content-Range did not match the request.')
        declared = response.headers.get('Content-Length')
        if declared is not None and int(declared) != expected_length:
            raise ValueError('Archive range Content-Length did not match the request.')
        payload = response.read(expected_length + 1)
    except ValueError:
        raise
    except Exception:
        raise ValueError('Bounded OSF archive range request failed.') from None
    finally:
        if response is not None:
            response.close()
    if len(payload) != expected_length:
        raise ValueError('Archive range response length did not match the request.')
    return payload


def _directory_layout(tail, total_size):
    """Return (entry_count, directory_size, directory_offset, is_zip64)."""
    if not isinstance(tail, bytes) or len(tail) > MAX_TAIL_BYTES or len(tail) > total_size:
        raise ValueError('ZIP tail exceeds the bounded inspection limit.')
    eocd_pos = -1
    for pos in range(len(tail) - 22, -1, -1):
        if tail[pos:pos + 4] != b'PK\x05\x06':
            continue
        comment_size = struct.unpack_from('<H', tail, pos + 20)[0]
        if pos + 22 + comment_size == len(tail):
            eocd_pos = pos
            break
    if eocd_pos < 0:
        raise ValueError('ZIP end-of-central-directory record was not found.')
    fields = struct.unpack_from('<4s4H2LH', tail, eocd_pos)
    _, disk_number, central_disk, disk_entries, total_entries, directory_size, directory_offset, _ = fields
    if disk_number != 0 or central_disk != 0 or disk_entries != total_entries:
        raise ValueError('Multi-disk ZIP archives are outside this audit.')
    if (total_entries == 0xFFFF or directory_size == 0xFFFFFFFF
            or directory_offset == 0xFFFFFFFF):
        raise ValueError('ZIP64 archive layout is outside this bounded audit.')
    if total_entries > MAX_ENTRIES:
        raise ValueError('ZIP entry count exceeds the inspection limit.')
    if directory_size > MAX_CENTRAL_DIRECTORY_BYTES:
        raise ValueError('ZIP central directory exceeds the inspection limit.')
    if directory_size and directory_offset + directory_size > total_size:
        raise ValueError('ZIP central directory points outside the archive.')
    return total_entries, directory_size, directory_offset, False


def _summarize_central_directory(central, declared_entries):
    if not isinstance(central, bytes) or len(central) > MAX_CENTRAL_DIRECTORY_BYTES:
        raise ValueError('ZIP central directory exceeds the inspection limit.')
    entries = files = directories = 0
    suffixes = Counter()
    schema_valid = Counter()
    keys = {'.wav': set(), '.flac': set(), '.csv': set()}
    plot_years = {'.wav': set(), '.flac': set(), '.csv': set()}
    compressed_total = uncompressed_total = 0
    pos = 0
    while pos < len(central):
        if pos + 46 > len(central) or central[pos:pos + 4] != b'PK\x01\x02':
            raise ValueError('Unexpected ZIP central-directory entry structure.')
        compressed = struct.unpack_from('<I', central, pos + 20)[0]
        uncompressed = struct.unpack_from('<I', central, pos + 24)[0]
        name_length, extra_length, comment_length = struct.unpack_from('<HHH', central, pos + 28)
        name_start = pos + 46
        name_end = name_start + name_length
        entry_end = name_end + extra_length + comment_length
        if entry_end > len(central):
            raise ValueError('ZIP central-directory entry exceeds the bounded response.')
        raw_name = central[name_start:name_end]
        flags = struct.unpack_from('<H', central, pos + 8)[0]
        name = raw_name.decode('utf-8' if flags & 0x800 else 'cp437', errors='replace')
        entries += 1
        if name.endswith('/'):
            directories += 1
        else:
            files += 1
            compressed_total += compressed
            uncompressed_total += uncompressed
            basename = PurePosixPath(name).name
            suffix = PurePosixPath(basename).suffix.casefold() or '[none]'
            suffixes[suffix] += 1
            if suffix in keys:
                key = metadata_audit._dataset_key(basename)
                if key is not None:
                    schema_valid[suffix] += 1
                    keys[suffix].add(key)
                    plot_years[suffix].add((key[0], key[1]))
        pos = entry_end
    if entries != declared_entries:
        raise ValueError('Parsed central-directory count did not match the ZIP end record.')
    csv_keys = keys['.csv']
    flac_keys = keys['.flac']
    return {
        'central_directory_entries': entries,
        'files': files,
        'directories': directories,
        'entry_compressed_bytes_total': compressed_total,
        'entry_uncompressed_bytes_total': uncompressed_total,
        'suffix_counts': dict(sorted(suffixes.items())),
        'schema_valid_filename_counts': dict(sorted(schema_valid.items())),
        'unique_schema_keys_by_suffix': {
            suffix: len(values) for suffix, values in keys.items()},
        'distinct_plot_year_groups_by_suffix': {
            suffix: len(values) for suffix, values in plot_years.items()},
        'csv_flac_intersection_unique_keys': len(csv_keys & flac_keys),
        'unique_csv_keys_missing_flac': len(csv_keys - flac_keys),
        'unique_flac_keys_missing_csv': len(flac_keys - csv_keys),
        'csv_entries_outside_published_filename_schema': (
            suffixes['.csv'] - schema_valid['.csv']),
    }


def inspect(opener=None):
    opener = opener or metadata_audit._opener()
    root = metadata_audit._json(opener, ROOT_API)
    if root.get('links', {}).get('next'):
        raise ValueError('OSF root listing unexpectedly requires pagination.')
    matches = [item for item in root.get('data', [])
               if item.get('attributes', {}).get('name') == ARCHIVE_NAME]
    if len(matches) != 1 or matches[0].get('id') != ARCHIVE_ID:
        raise ValueError('Pinned OSF dataset archive identity changed.')
    file_record = metadata_audit._file_record(opener, ARCHIVE_ID)
    attributes = file_record.get('attributes', {})
    download_url = file_record.get('links', {}).get('download')
    size = attributes.get('size')
    if (attributes.get('name') != ARCHIVE_NAME or size != ARCHIVE_SIZE
            or not isinstance(download_url, str)):
        raise ValueError('Pinned OSF archive metadata changed.')
    _trusted_download_url(download_url)

    tail_size = min(MAX_TAIL_BYTES, size)
    tail_start = size - tail_size
    tail = _range_read(opener, download_url, tail_start, size - 1, size)
    entry_count, directory_size, directory_offset, zip64 = _directory_layout(tail, size)
    central = (_range_read(opener, download_url, directory_offset,
                           directory_offset + directory_size - 1, size)
               if directory_size else b'')
    summary = _summarize_central_directory(central, entry_count)
    summary.update({
        'dataset_node': NODE_ID,
        'archive_file_id': ARCHIVE_ID,
        'archive_size_bytes': size,
        'zip64': zip64,
        'central_directory_bytes': directory_size,
        'range_bytes_read': tail_size + directory_size,
        'archive_file_payload_bytes_read': 0,
        'audio_or_annotation_payload_opened': False,
        'filenames_or_location_values_retained_or_reported': False,
        'full_archive_checksum_verified': False,
        'reviewed_at': datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z'),
    })
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    report = inspect()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
