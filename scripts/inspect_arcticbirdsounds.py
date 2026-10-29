"""Audit ArcticBirdSounds metadata joins without acquiring audio or annotations.

The script reads the small deployment table and OSF file manifests in memory,
checks the table checksum, and writes aggregate-only counts. It never reads WAV,
FLAC, or annotation CSV payloads, and never reports exact site coordinates.
"""
import argparse
import csv
from datetime import datetime
import hashlib
import io
import json
import re
import ssl
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit

try:
    import certifi
except ImportError:  # pragma: no cover - exercised only without certifi installed
    certifi = None

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / 'research/arcticbirdsounds_metadata_report.json'
NODE_ID = 'b9trx'
NODE_API = f'https://api.osf.io/v2/nodes/{NODE_ID}/'
LICENSE_ID = '563c1cf88c5e4a3877f9e96a'
EXPECTED_SITE_INFO_ID = '6400f2dff014b90ab5eb3e75'
EXPECTED_SITE_INFO_SIZE = 2001
EXPECTED_SITE_INFO_SHA256 = '1f2594a6fc1b1feb3a38e3f105c074d846e26626e188c80486c0b5f0e698dc1b'
EXPECTED_AUDIO_FOLDER_ID = '6400e0c040cecd0b0976ee56'
EXPECTED_DATA_FOLDER_ID = '6400f2d340cecd0b1f76eb8e'
EXPECTED_ANNOTATION_FOLDER_ID = '64022a339d44790c1232b22f'
MAX_API_BYTES = 2 * 1024 * 1024
MAX_TABLE_BYTES = 64 * 1024
MAX_PAGES = 50
PAGE_WORKERS = 4
MAX_FOLDER_ITEMS = 5000
ALLOWED_HOSTS = {'api.osf.io', 'osf.io', 'files.osf.io', 'files.us.osf.io'}
OSF_OBJECT_STORAGE_HOST = re.compile(
    r'^[a-z0-9-]+\.compat\.objectstorage\.us-ashburn-1\.oraclecloud\.com$')
REQUIRED_COLUMNS = {'plot', 'year', 'site', 'recorder_id'}
DATASET_NAME = re.compile(
    r'^(?P<year>2018|2019)(?:\s+|_)'
    r'(?P<plot>[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*)'
    r'(?:\s+|_)(?P<timestamp>\d{8}-\d{6})'
    r'(?:\s+|_)(?P<segment>10|[1-9])(?P<tags>-tags)?$'
)


def _trusted_host(host):
    return host in ALLOWED_HOSTS or bool(OSF_OBJECT_STORAGE_HOST.fullmatch(host or ''))


class _AllowedRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, file_pointer, code, message, headers, new_url):
        parsed = urlsplit(new_url)
        if (parsed.scheme != 'https' or not _trusted_host(parsed.hostname)
                or parsed.username or parsed.password or parsed.port not in (None, 443)):
            raise ValueError('Unexpected redirect outside the pinned OSF origins.')
        return super().redirect_request(request, file_pointer, code, message, headers, new_url)


def _opener():
    context = ssl.create_default_context(
        cafile=certifi.where() if certifi is not None else None)
    return urllib.request.build_opener(
        _AllowedRedirect(), urllib.request.HTTPSHandler(context=context))


def _read(opener, url, maximum, content_types, allowed_hosts=None):
    parsed = urlsplit(url)
    hosts = allowed_hosts or {'api.osf.io'}
    if (parsed.scheme != 'https' or parsed.hostname not in hosts
            or parsed.username or parsed.password or parsed.port not in (None, 443)
            or parsed.fragment):
        raise ValueError('OSF request URL is outside the pinned HTTPS origins.')
    request = urllib.request.Request(url, headers={
        'User-Agent': 'Talk2Nature-metadata-audit/1',
        'Accept-Encoding': 'identity',
    })
    try:
        with opener.open(request, timeout=20) as response:
            final = urlsplit(response.geturl())
            if (response.status != 200 or final.scheme != 'https'
                    or not _trusted_host(final.hostname)
                    or final.username or final.password
                    or final.port not in (None, 443)):
                raise ValueError('Unexpected OSF response origin or status.')
            if response.headers.get('Content-Encoding', 'identity') != 'identity':
                raise ValueError('Encoded OSF response refused.')
            content_type = response.headers.get('Content-Type', '').split(';', 1)[0].lower()
            if content_type not in content_types:
                raise ValueError('Unexpected OSF content type.')
            declared = response.headers.get('Content-Length')
            if declared is not None and int(declared) > maximum:
                raise ValueError('OSF response exceeds the inspection limit.')
            data = response.read(maximum + 1)
    except ValueError:
        raise
    except Exception:
        raise ValueError('Pinned OSF metadata request failed.') from None
    if len(data) > maximum:
        raise ValueError('OSF response exceeds the inspection limit.')
    return data


def _json(opener, url):
    raw = _read(opener, url, MAX_API_BYTES,
                {'application/json', 'application/vnd.api+json'})
    try:
        result = json.loads(raw)
    except (ValueError, UnicodeDecodeError):
        raise ValueError('OSF metadata is not valid JSON.') from None
    if not isinstance(result, dict):
        raise ValueError('OSF response is not an object.')
    return result


def _children(opener, folder_id):
    folder_path = f'/v2/nodes/{NODE_ID}/files/osfstorage/{folder_id}/'
    first_url = f'https://api.osf.io{folder_path}?page%5Bsize%5D=100'
    first_payload = _json(opener, first_url)
    first_items = first_payload.get('data')
    if not isinstance(first_items, list):
        raise ValueError('OSF file listing has no data array.')
    next_url = first_payload.get('links', {}).get('next')
    last_url = first_payload.get('links', {}).get('last')
    total_pages = _page_count(last_url)
    if total_pages > MAX_PAGES:
        pages_to_read = MAX_PAGES
    else:
        pages_to_read = total_pages
    if len(first_items) > MAX_FOLDER_ITEMS:
        raise ValueError('OSF file listing exceeds the bounded item limit.')
    if total_pages == 1:
        if next_url:
            raise ValueError('OSF pagination links disagree about the page count.')
        return first_items, {
            'pages_inspected': 1,
            'total_pages': total_pages,
            'complete': True,
        }
    if not next_url:
        raise ValueError('OSF multi-page folder has no next-page link.')

    template_parts, query = _validate_page_url(next_url, folder_path, 2)
    _validate_page_url(last_url, folder_path, total_pages)
    page_urls = []
    for page_number in range(2, pages_to_read + 1):
        page_query = dict(query)
        page_query['page'] = [str(page_number)]
        page_url = urlunsplit((
            template_parts.scheme,
            template_parts.netloc,
            template_parts.path,
            urlencode(page_query, doseq=True),
            '',
        ))
        _validate_page_url(page_url, folder_path, page_number)
        page_urls.append(page_url)

    with ThreadPoolExecutor(max_workers=PAGE_WORKERS) as pool:
        payloads = list(pool.map(lambda url: _json(opener, url), page_urls))
    all_items = list(first_items)
    for payload in payloads:
        items = payload.get('data')
        if not isinstance(items, list):
            raise ValueError('OSF file listing has no data array.')
        all_items.extend(items)
        if len(all_items) > MAX_FOLDER_ITEMS:
            raise ValueError('OSF file listing exceeds the bounded item limit.')
    return all_items, {
        'pages_inspected': 1 + len(payloads),
        'total_pages': total_pages,
        'complete': pages_to_read == total_pages,
    }


def _validate_page_url(url, folder_path, expected_page):
    parsed = urlsplit(url or '')
    query = parse_qs(parsed.query)
    if (parsed.scheme != 'https' or parsed.hostname != 'api.osf.io'
            or parsed.username or parsed.password or parsed.port not in (None, 443)
            or parsed.fragment or parsed.path != folder_path
            or query.get('page') != [str(expected_page)]
            or query.get('page[size]') != ['100']):
        raise ValueError('OSF pagination escaped the pinned folder or page sequence.')
    return parsed, query


def _page_count(url):
    if not url:
        return 1
    page = parse_qs(urlsplit(url).query).get('page', ['1'])[0]
    return int(page) if page.isdigit() else 1


def _file_record(opener, file_id):
    payload = _json(opener, f'https://api.osf.io/v2/files/{file_id}/')
    record = payload.get('data')
    if not isinstance(record, dict) or record.get('id') != file_id:
        raise ValueError('OSF file identity changed.')
    return record


def _site_rows(data):
    try:
        text = data.decode('utf-8-sig')
        reader = csv.DictReader(io.StringIO(text))
        columns = set(reader.fieldnames or ())
        if not REQUIRED_COLUMNS.issubset(columns):
            raise ValueError('Deployment table lacks expected grouping fields.')
        rows = list(reader)
    except UnicodeDecodeError:
        raise ValueError('Deployment table is not UTF-8 text.') from None
    if not rows or any(None in row or any(value is None for value in row.values()) for row in rows):
        raise ValueError('Deployment table is empty or malformed.')
    for row in rows:
        if not all(row[name].strip() for name in REQUIRED_COLUMNS):
            raise ValueError('Deployment table contains a blank grouping field.')
    return rows


def _norm(value):
    return re.sub(r'[^a-z0-9]+', '', str(value).casefold())


def _dataset_key(name):
    """Parse the publisher-documented recording/annotation filename key."""
    path = Path(name)
    suffix = path.suffix.casefold()
    if suffix not in {'.wav', '.flac', '.csv'}:
        return None
    stem = path.stem
    is_tags_csv = suffix == '.csv' and stem.endswith('-tags')
    if suffix == '.csv' and not is_tags_csv:
        return None
    match = DATASET_NAME.fullmatch(stem)
    if not match or bool(match.group('tags')) != is_tags_csv:
        return None
    try:
        stamp = datetime.strptime(match.group('timestamp'), '%Y%m%d-%H%M%S')
    except ValueError:
        return None
    year = match.group('year')
    if stamp.year != int(year):
        return None
    return (year, _norm(match.group('plot')), match.group('timestamp'),
            int(match.group('segment')))


def _deployment_groups(deployments):
    groups = Counter()
    for row in deployments:
        groups[(row['year'].strip(), _norm(row['plot'].strip()))] += 1
    return groups


def _site_group_for_key(key, deployments, key_counts):
    if key is None:
        return set()
    year, plot, _, _ = key
    if key_counts[(year, plot)] != 1:
        return set()
    return {
        (row['site'].strip(), row['plot'].strip(), row['year'].strip())
        for row in deployments
        if row['year'].strip() == year and _norm(row['plot'].strip()) == plot
    }


def summarize(site_rows, audio_items, annotation_items, source_sha256,
              audio_manifest, annotation_manifest):
    """Return aggregate-only join counts from metadata already in memory."""
    site_groups = {
        (row['site'].strip(), row['plot'].strip(), row['year'].strip())
        for row in site_rows
    }
    site_ids = {row['site'].strip() for row in site_rows}
    plots = {row['plot'].strip() for row in site_rows}
    recorder_ids = {row['recorder_id'].strip() for row in site_rows}

    wav_items = [item for item in audio_items
                 if item.get('attributes', {}).get('kind') == 'file'
                 and item.get('attributes', {}).get('name', '').lower().endswith('.wav')]
    wav_names = [item['attributes']['name'] for item in wav_items]
    if len(wav_names) != len(set(wav_names)):
        raise ValueError('OSF audio listing contains duplicate WAV names.')
    wav_keys = [_dataset_key(name) for name in wav_names]
    deployment_key_counts = _deployment_groups(site_rows)
    wav_groups = [_site_group_for_key(key, site_rows, deployment_key_counts)
                  for key in wav_keys]
    wav_matched = sum(len(groups) == 1 for groups in wav_groups)
    wav_ambiguous = sum(len(groups) > 1 for groups in wav_groups)
    sites_with_audio = {
        next(iter(groups))[0] for groups in wav_groups if len(groups) == 1
    }

    files = [item for item in annotation_items
             if item.get('attributes', {}).get('kind') == 'file']
    csv_files = [item for item in files
                 if item['attributes']['name'].lower().endswith('.csv')]
    flac_files = [item for item in files
                  if item['attributes']['name'].lower().endswith('.flac')]
    csv_names = [item['attributes']['name'] for item in csv_files]
    flac_names = [item['attributes']['name'] for item in flac_files]
    csv_keys = [_dataset_key(name) for name in csv_names]
    flac_keys = [_dataset_key(name) for name in flac_names]
    csv_key_counts = Counter(key for key in csv_keys if key is not None)
    flac_key_counts = Counter(key for key in flac_keys if key is not None)
    wav_key_counts = Counter(key for key in wav_keys if key is not None)
    exact_pairs = len(set(csv_key_counts) & set(flac_key_counts))
    csv_wav_key_pairs = len(set(csv_key_counts) & set(wav_key_counts))
    duplicate_wav_keys = sum(count - 1 for count in wav_key_counts.values() if count > 1)
    duplicate_csv_keys = sum(count - 1 for count in csv_key_counts.values() if count > 1)
    duplicate_flac_keys = sum(count - 1 for count in flac_key_counts.values() if count > 1)
    plot_year_segment_counts = Counter(
        (key[0], key[1]) for key in csv_keys if key is not None
    )
    recording_segment_counts = Counter(
        (key[0], key[1], key[2]) for key in csv_keys if key is not None
    )
    plot_year_segment_histogram = Counter(plot_year_segment_counts.values())
    recording_segment_histogram = Counter(recording_segment_counts.values())
    ann_names = [item['attributes']['name'] for item in csv_files]
    annotation_groups = [_site_group_for_key(key, site_rows, deployment_key_counts)
                         for key in csv_keys]
    annotations_matched = sum(len(groups) == 1 for groups in annotation_groups)
    annotation_sites = {
        next(iter(groups))[0] for groups in annotation_groups if len(groups) == 1
    }
    annotation_audio_keys = csv_wav_key_pairs

    per_site_audio = Counter(next(iter(groups))[0]
                             for groups in wav_groups if len(groups) == 1)
    per_site_annotation = Counter(next(iter(groups))[0]
                                  for groups in annotation_groups if len(groups) == 1)
    audio_support = Counter(per_site_audio.values())
    annotation_support = Counter(per_site_annotation.values())
    return {
        'dataset_node': NODE_ID,
        'site_info_sha256': source_sha256,
        'deployment_table': {
            'deployment_rows': len(site_rows),
            'distinct_sites': len(site_ids),
            'distinct_plots': len(plots),
            'distinct_site_plot_year_groups': len(site_groups),
            'distinct_recorder_ids': len(recorder_ids),
            'coordinate_values_retained_or_reported': False,
            'ambiguous_year_plot_keys': sum(count > 1 for count in deployment_key_counts.values()),
        },
        'publisher_schema': {
            'filename_schema_documented': True,
            'site_join_key': 'year plus plot',
            'annotation_audio_filename_field_documented': True,
            'timestamp_clock_exceptions_within_30_seconds_documented': True,
        },
        'published_count_comparison': {
            'paper_reported_locations_in_abstract': 6,
            'supplement_narrative_locations': 7,
            'deployment_table_distinct_site_labels': len(site_ids),
            'paper_reported_plot_year_groups': 20,
            'manifest_plot_year_groups': len(plot_year_segment_counts),
            'paper_reported_30_second_audio_segments': 2400,
            'manifest_csv_flac_key_pairs': exact_pairs,
            'source_count_discrepancy_resolved': False,
        },
        'full_audio_manifest': {
            'representation': 'uncompressed WAV directory',
            'wav_files_in_inspected_pages': len(wav_names),
            'manifest_pages_inspected': audio_manifest['pages_inspected'],
            'manifest_total_pages': audio_manifest['total_pages'],
            'manifest_complete': audio_manifest['complete'],
            'unique_filename_count_in_inspected_pages': len(set(wav_names)),
            'schema_valid_filenames': sum(key is not None for key in wav_keys),
            'duplicate_schema_keys': duplicate_wav_keys,
            'unambiguous_plot_year_to_site_matches': wav_matched,
            'ambiguous_plot_year_matches': wav_ambiguous,
            'unmatched_recordings_in_inspected_pages': len(wav_names) - wav_matched - wav_ambiguous,
            'sites_with_unambiguous_audio_in_inspected_pages': len(sites_with_audio),
            'site_audio_sample_count_histogram': {
                str(count): audio_support[count] for count in sorted(audio_support)
            },
        },
        'annotation_file_manifest': {
            'flac_files_are_audio': True,
            'csv_files_in_inspected_pages': len(ann_names),
            'flac_files_in_inspected_pages': len(flac_files),
            'manifest_pages_inspected': annotation_manifest['pages_inspected'],
            'manifest_total_pages': annotation_manifest['total_pages'],
            'manifest_complete': annotation_manifest['complete'],
            'exact_csv_flac_schema_key_pairs': exact_pairs,
            'csv_keys_matching_wav_files': annotation_audio_keys,
            'schema_valid_csv_filenames': sum(key is not None for key in csv_keys),
            'schema_valid_flac_filenames': sum(key is not None for key in flac_keys),
            'distinct_plot_year_groups': len(plot_year_segment_counts),
            'plot_year_segment_count_histogram': {
                str(count): plot_year_segment_histogram[count]
                for count in sorted(plot_year_segment_histogram)
            },
            'five_minute_recording_timestamp_groups': len(recording_segment_counts),
            'segments_per_timestamp_group_histogram': {
                str(count): recording_segment_histogram[count]
                for count in sorted(recording_segment_histogram)
            },
            'timestamp_groups_with_all_10_segments': sum(
                count == 10 for count in recording_segment_counts.values()),
            'duplicate_csv_schema_keys': duplicate_csv_keys,
            'duplicate_flac_schema_keys': duplicate_flac_keys,
            'csv_keys_missing_matching_flac': len(set(csv_key_counts) - set(flac_key_counts)),
            'flac_keys_missing_matching_csv': len(set(flac_key_counts) - set(csv_key_counts)),
            'csv_keys_missing_matching_wav': len(set(csv_key_counts) - set(wav_key_counts)),
            'unambiguous_plot_year_to_site_matches': annotations_matched,
            'unmatched_or_ambiguous_csv_files_in_inspected_pages': len(ann_names) - annotations_matched,
            'sites_with_unambiguous_annotation_files_in_inspected_pages': len(annotation_sites),
            'site_annotation_sample_count_histogram': {
                str(count): annotation_support[count]
                for count in sorted(annotation_support)
            },
            'annotation_csv_contents_read': False,
        },
        'assessment': {
            'audio_sample_file_to_site_keys_present': wav_matched == len(wav_names) and bool(wav_names),
            'annotation_sample_to_site_keys_present': (
                annotations_matched == len(ann_names) and bool(ann_names)),
            'complete_audio_corpus_file_to_site_mapping_verified': (
                audio_manifest['complete'] and wav_matched == len(wav_names) and bool(wav_names)
                and all(key is not None for key in wav_keys) and duplicate_wav_keys == 0),
            'complete_annotation_corpus_to_site_mapping_verified': (
                annotation_manifest['complete'] and annotations_matched == len(ann_names)
                and bool(ann_names) and all(key is not None for key in csv_keys)
                and all(key is not None for key in flac_keys)
                and duplicate_csv_keys == 0 and duplicate_flac_keys == 0
                and exact_pairs == len(csv_key_counts)
                and set(csv_key_counts) == set(flac_key_counts)),
            'site_grouped_holdout_candidate': (
                annotation_manifest['complete'] and len(annotation_sites) >= 2
                and annotations_matched == len(ann_names)
                and all(key is not None for key in csv_keys + flac_keys)
                and duplicate_csv_keys == duplicate_flac_keys == 0
                and exact_pairs == len(csv_key_counts)
                and set(csv_key_counts) == set(flac_key_counts)
            ),
            'uncompressed_wav_directory_covers_all_annotated_audio': (
                csv_wav_key_pairs == len(csv_key_counts)),
            'mapping_scope': (
                'Complete paginated filename manifests' if
                audio_manifest['complete'] and annotation_manifest['complete'] else
                'Publisher schema verified; first manifest pages only, full manifests unverified.'),
            'benchmark_ready': False,
            'decision': 'Complete FLAC/annotation filename-to-site mapping is a grouped-split candidate; event-label coverage, group independence, component rights and pretrained-data leakage remain open.',
        },
        'payloads': {
            'wav_bytes_downloaded_or_opened': False,
            'flac_bytes_downloaded_or_opened': False,
            'annotation_rows_read': False,
            'coordinates_reported': False,
            'model_or_embedding_used': False,
            'training_admitted': False,
        },
    }


def inspect(opener=None):
    opener = opener or _opener()
    node = _json(opener, NODE_API)
    node_data = node.get('data')
    license_ref = (node_data or {}).get('relationships', {}).get('license', {}).get('data')
    if (not isinstance(node_data, dict) or node_data.get('id') != NODE_ID
            or not isinstance(license_ref, dict) or license_ref.get('id') != LICENSE_ID):
        raise ValueError('OSF node identity or license relationship changed.')
    license_payload = _json(opener, f'https://api.osf.io/v2/licenses/{LICENSE_ID}/')
    license_data = license_payload.get('data', {})
    license_name = license_data.get('attributes', {}).get('name', '')
    if license_data.get('id') != LICENSE_ID or 'CC-By Attribution 4.0' not in license_name:
        raise ValueError('OSF dataset license is not the expected CC BY 4.0 declaration.')

    root_listing = _json(
        opener, f'https://api.osf.io/v2/nodes/{NODE_ID}/files/osfstorage/?page%5Bsize%5D=100'
    )
    root_items = root_listing.get('data', [])
    if root_listing.get('links', {}).get('next'):
        raise ValueError('OSF root folder listing unexpectedly requires pagination.')
    by_name = {item.get('attributes', {}).get('name'): item for item in root_items}
    audio_folder = by_name.get('uncompressed_audio')
    data_folder = by_name.get('DataS1')
    if (not isinstance(audio_folder, dict) or audio_folder.get('id') != EXPECTED_AUDIO_FOLDER_ID
            or not isinstance(data_folder, dict) or data_folder.get('id') != EXPECTED_DATA_FOLDER_ID):
        raise ValueError('OSF dataset folder manifest changed.')

    data_items, data_manifest = _children(opener, EXPECTED_DATA_FOLDER_ID)
    if not data_manifest['complete']:
        raise ValueError('Small DataS1 metadata folder unexpectedly exceeds the bounded listing.')
    data_by_name = {item.get('attributes', {}).get('name'): item for item in data_items}
    site_info = data_by_name.get('site_infos.csv')
    annotation_folder = data_by_name.get('audio_annots')
    if (not isinstance(site_info, dict) or site_info.get('id') != EXPECTED_SITE_INFO_ID
            or not isinstance(annotation_folder, dict)
            or annotation_folder.get('id') != EXPECTED_ANNOTATION_FOLDER_ID):
        raise ValueError('OSF DataS1 manifest changed.')

    file_record = _file_record(opener, EXPECTED_SITE_INFO_ID)
    attributes = file_record.get('attributes', {})
    hashes = attributes.get('extra', {}).get('hashes', {})
    download_url = file_record.get('links', {}).get('download')
    if (attributes.get('name') != 'site_infos.csv'
            or attributes.get('size') != EXPECTED_SITE_INFO_SIZE
            or hashes.get('sha256') != EXPECTED_SITE_INFO_SHA256
            or not isinstance(download_url, str)):
        raise ValueError('Pinned deployment-table file metadata changed.')
    table_bytes = _read(opener, download_url, MAX_TABLE_BYTES,
                        {'text/csv', 'application/octet-stream'},
                        allowed_hosts={'osf.io', 'files.osf.io'})
    digest = hashlib.sha256(table_bytes).hexdigest()
    if len(table_bytes) != EXPECTED_SITE_INFO_SIZE or digest != EXPECTED_SITE_INFO_SHA256:
        raise ValueError('Deployment-table checksum changed.')

    audio_items, audio_manifest = _children(opener, EXPECTED_AUDIO_FOLDER_ID)
    annotation_items, annotation_manifest = _children(opener, EXPECTED_ANNOTATION_FOLDER_ID)
    report = summarize(_site_rows(table_bytes), audio_items, annotation_items, digest,
                       audio_manifest, annotation_manifest)
    report['rights'] = {
        'dataset_license': license_name,
        'license_id': LICENSE_ID,
        'preparation_code_license': 'MIT declared by linked public GitHub repository',
        'preparation_code_license_evidence': 'https://github.com/Vin985/arctic_songs',
        'preparation_code_contents_acquired_or_reviewed': False,
        'paper_and_supplement_rights_are_separate': True,
        'audio_or_annotation_payload_reuse_authorized_by_this_audit': False,
    }
    report['reviewed_at'] = '2026-10-29'
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = json.dumps(inspect(), indent=2) + '\n'
    args.output.write_text(result)
    print(json.dumps({'report': str(args.output), 'summary': json.loads(result)}, indent=2))
