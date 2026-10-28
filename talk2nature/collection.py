"""Catalog and acquire small reviewed research samples, without executing them.

License/admission fields are human-reviewed declarations, not legal or scientific
verification. Adapters support immutable GitHub files, reviewed Mendeley files
with deposit SHA-256 checksums, bounded Figshare files with item metadata and
optional provider MD5 verification, and pinned Zenodo record files. Downloads are not training releases and
never enter the private admin or website build.
"""
import argparse
import hashlib
import json
import re
import ssl
import tempfile
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / 'research/resources.json'
DESTINATION = ROOT / 'data/external'
MAX_FILE_BYTES = 5 * 1024 * 1024
MAX_BATCH_BYTES = 20 * 1024 * 1024
PERMITTED_LICENSES = {'MIT', 'Apache-2.0', 'CC-BY-4.0', 'CC0-1.0'}
FIGSHARE_STORAGE_PREFIXES = {
    'figshare_springernature': 'pstorage-npg-968563215',
    'figshare_public': 'pfigshare-u-files',
    # Observed in the verified PLOS Figshare file redirect for item 7184276.
    'figshare_plos': 'pstorage-plos-3567654',
}
ZENODO_ORIGIN = 'https://zenodo.org'


def require_text(record, field):
    value = record.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'Missing text: {field}')
    return value


def https_url(value):
    parsed = urlsplit(value)
    if (parsed.scheme != 'https' or not parsed.hostname or parsed.username
            or parsed.password or parsed.port not in (None, 443)):
        raise ValueError('Source must be an HTTPS URL without credentials.')
    return parsed


def validate(catalog):
    if not isinstance(catalog, dict) or catalog.get('schema_version') != 1:
        raise ValueError('Expected collection schema_version 1.')
    records = catalog.get('resources')
    if not isinstance(records, list) or not records:
        raise ValueError('Expected nonempty resources list.')
    seen = set()
    for resource in records:
        if not isinstance(resource, dict):
            raise ValueError('Resource must be an object.')
        identifier = require_text(resource, 'id')
        if not re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*', identifier) or identifier in seen:
            raise ValueError('Invalid or duplicate resource id.')
        seen.add(identifier)
        for field in ('title', 'version', 'review_depth', 'task', 'access', 'decision',
                      'limitations', 'attribution'):
            require_text(resource, field)
        https_url(require_text(resource, 'url'))
        date.fromisoformat(require_text(resource, 'reviewed'))
        if resource.get('kind') not in {'paper', 'code', 'dataset', 'model', 'standard', 'project'}:
            raise ValueError('Unknown resource kind.')
        if type(resource.get('priority')) is not int or resource['priority'] not in (1, 2, 3):
            raise ValueError('Priority must be 1, 2 or 3.')
        rights = resource.get('rights')
        if not isinstance(rights, dict):
            raise ValueError('Missing component-specific rights.')
        for field in ('license', 'scope', 'conditions'):
            require_text(rights, field)
        https_url(require_text(rights, 'evidence_url'))
        for field in ('research_use', 'commercial_use', 'redistribution'):
            if rights.get(field) not in ('conditional', 'not_admitted', 'unresolved'):
                raise ValueError(f'Invalid rights decision: {field}')
        if resource.get('acquisition') not in {'metadata_only', 'sample_approved'}:
            raise ValueError('Invalid acquisition status.')
        if ('analysis_admission' in resource
                and resource['analysis_admission'] not in {'not_admitted', 'approved'}):
            raise ValueError('Invalid analysis admission status.')
        if resource.get('analysis_admission') == 'approved' and (
                resource['acquisition'] != 'sample_approved'
                or rights['research_use'] != 'conditional'):
            raise ValueError('Analysis admission requires an approved sample and research-use rights.')
        files = resource.get('files', [])
        if not isinstance(files, list):
            raise ValueError('Files must be a list.')
        if resource['acquisition'] == 'metadata_only' and files:
            raise ValueError('Metadata-only resources cannot have acquisition files.')
        if resource['acquisition'] == 'sample_approved':
            if not files or rights['license'] not in PERMITTED_LICENSES:
                raise ValueError('Acquisition requires files and a reviewed permissive license.')
            if any(rights[k] != 'conditional' for k in ('research_use', 'commercial_use', 'redistribution')):
                raise ValueError('Unresolved/restricted rights cannot enter this acquisition adapter.')
            adapter = resource.get('adapter', 'github')
            deposit = re.fullmatch(r'10\.17632/([a-z0-9]{10})\.([1-9][0-9]*)', resource['version'])
            if adapter == 'github':
                if not re.fullmatch('[a-f0-9]{40}', resource['version']):
                    raise ValueError('Sample requires an immutable Git commit.')
            elif adapter == 'mendeley_sha256':
                if not deposit or resource['url'] != f'https://data.mendeley.com/datasets/{deposit[1]}/{deposit[2]}':
                    raise ValueError('Mendeley sample requires a versioned deposit.')
                require_text(resource, 'license_notice')
            elif adapter in FIGSHARE_STORAGE_PREFIXES:
                item_id = resource.get('figshare_item_id')
                if (type(item_id) is not int or item_id <= 0
                        or resource['url'] != f'https://api.figshare.com/v2/articles/{item_id}'
                        or str(item_id) not in resource['version']):
                    raise ValueError('Figshare sample requires a version-pinned public item API record.')
                require_text(resource, 'license_notice')
            elif adapter == 'zenodo_record':
                record_id = resource.get('zenodo_record_id')
                expected_doi = f'10.5281/zenodo.{record_id}' if type(record_id) is int else ''
                if (type(record_id) is not int or record_id <= 0
                        or resource['url'] != f'{ZENODO_ORIGIN}/records/{record_id}'
                        or resource.get('zenodo_doi') != expected_doi
                        or f'record {record_id}' not in resource['version'].lower()):
                    raise ValueError('Zenodo sample requires an exact versioned public record and DOI.')
                require_text(resource, 'license_notice')
            else:
                raise ValueError('Unknown acquisition adapter.')
            require_text(resource, 'admission_reason')
            names = set()
            for artifact in files:
                if not isinstance(artifact, dict):
                    raise ValueError('Artifact must be an object.')
                name = require_text(artifact, 'name')
                if not re.fullmatch('[A-Za-z0-9][A-Za-z0-9._-]*', name) or name in names or name == 'receipt.json':
                    raise ValueError('Invalid or duplicate artifact name.')
                names.add(name)
                parsed = https_url(require_text(artifact, 'url'))
                parts = parsed.path.split('/')
                if adapter == 'github':
                    if (parsed.hostname != 'raw.githubusercontent.com' or parsed.query or parsed.fragment
                            or len(parts) < 5 or parts[3] != resource['version']
                            or any(x in ('.', '..') for x in unquote(parsed.path).split('/'))):
                        raise ValueError('Artifact must use a pinned raw.githubusercontent.com URL.')
                    if not re.fullmatch('[a-f0-9]{40}', require_text(artifact, 'git_blob_sha1')) or 'sha256' in artifact:
                        raise ValueError('Missing or ambiguous Git blob checksum.')
                elif adapter == 'mendeley_sha256':
                    uuid = r'[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}'
                    if (parsed.hostname != 'prod-dcd-datasets-public-files-eu-west-1.s3.eu-west-1.amazonaws.com'
                            or parsed.query or parsed.fragment or not re.fullmatch('/' + uuid, parsed.path)):
                        raise ValueError('Mendeley artifact must pin the reviewed public S3 object.')
                    if not re.fullmatch('[a-f0-9]{64}', require_text(artifact, 'sha256')) or 'git_blob_sha1' in artifact:
                        raise ValueError('Missing or ambiguous deposit SHA-256.')
                    if not re.fullmatch(re.escape(f'https://data.mendeley.com/public-files/datasets/{deposit[1]}/files/') + uuid + '/file_downloaded', require_text(artifact, 'source_url')):
                        raise ValueError('Artifact provenance must match the named deposit.')
                elif adapter == 'zenodo_record':
                    record_id = resource['zenodo_record_id']
                    file_key = artifact.get('zenodo_file_key')
                    md5 = artifact.get('md5')
                    expected_path = f'/api/records/{record_id}/files/{name}/content'
                    if (parsed.hostname != 'zenodo.org' or parsed.path != expected_path
                            or parsed.query or parsed.fragment or file_key != name
                            or artifact.get('zenodo_record_id') != record_id
                            or artifact.get('source_url') != resource['url']
                            or not isinstance(md5, str) or not re.fullmatch('[a-f0-9]{32}', md5)
                            or 'sha256' in artifact or 'git_blob_sha1' in artifact):
                        raise ValueError('Zenodo artifact must pin its record, file key, content URL and MD5.')
                else:
                    file_id = artifact.get('figshare_file_id')
                    md5 = artifact.get('md5')
                    expected_prefix = FIGSHARE_STORAGE_PREFIXES[adapter]
                    prefix = artifact.get('figshare_storage_prefix', expected_prefix)
                    if (type(file_id) is not int or file_id <= 0
                            or parsed.hostname != 'ndownloader.figshare.com'
                            or parsed.path != f'/files/{file_id}' or parsed.query or parsed.fragment
                            or require_text(artifact, 'source_url') != resource['url']
                            or prefix != expected_prefix
                            or (adapter == 'figshare_public'
                                and artifact.get('figshare_storage_prefix') != expected_prefix)
                            or 'md5' not in artifact
                            or (md5 is not None and (not isinstance(md5, str)
                                or not re.fullmatch('[a-f0-9]{32}', md5)))
                            or 'sha256' in artifact or 'git_blob_sha1' in artifact):
                        raise ValueError('Figshare artifact must pin its item, file ID, download URL and checksum status.')
                    if md5 is None:
                        require_text(artifact, 'md5_unavailable_reason')
                    elif 'md5_unavailable_reason' in artifact:
                        raise ValueError('Do not describe a present Figshare MD5 as unavailable.')
                if type(artifact.get('bytes')) is not int or not 0 < artifact['bytes'] <= MAX_FILE_BYTES:
                    raise ValueError('Artifact exceeds file limit or has invalid size.')
            if adapter == 'github' and resource.get('license_file') not in names:
                raise ValueError('Every sample must retain a license file.')
    return catalog


def require_processing_admission(resource_ids, catalog_path=CATALOG):
    """Fail closed unless dataset processing and every input's rights are admitted."""
    try:
        catalog = json.loads(Path(catalog_path).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError('Could not read the current rights catalog; processing is blocked.') from exc
    if (not isinstance(catalog, dict) or catalog.get('schema_version') != 1
            or not isinstance(catalog.get('resources'), list)):
        raise ValueError('Invalid rights catalog; processing is blocked.')
    admitted = {}
    for resource_id in resource_ids:
        matches = [r for r in catalog['resources']
                   if isinstance(r, dict) and r.get('id') == resource_id]
        if len(matches) != 1:
            raise ValueError(f'Rights catalog must contain exactly one {resource_id} record; processing is blocked.')
        resource = matches[0]
        rights = resource.get('rights')
        rights_ready = (isinstance(rights, dict)
                        and all(rights.get(field) == 'conditional' for field in
                                ('research_use', 'commercial_use', 'redistribution')))
        dataset_ready = (resource.get('kind') == 'dataset'
                         and resource.get('analysis_admission') == 'approved'
                         and resource.get('acquisition') == 'sample_approved')
        code_ready = (rights_ready
                      and resource.get('kind') == 'code'
                      and resource.get('acquisition') == 'sample_approved'
                      and isinstance(rights.get('license'), str)
                      and bool(rights['license'].strip()))
        if not rights_ready or not (dataset_ready or code_ready):
            raise ValueError(
                f'Processing is not admitted for {resource_id}; confirm the required acquisition, analysis-admission and rights fields in the catalog first.')
        admitted[resource_id] = resource
    return admitted


def plan(catalog, identifiers, max_bytes=MAX_BATCH_BYTES):
    validate(catalog)
    if type(max_bytes) is not int or not 0 < max_bytes <= MAX_BATCH_BYTES:
        raise ValueError('Batch limit must be between 1 and 20 MiB.')
    if not identifiers or len(identifiers) != len(set(identifiers)):
        raise ValueError('Select unique resource IDs explicitly.')
    by_id = {r['id']: r for r in catalog['resources']}
    selected = []
    for identifier in identifiers:
        if identifier not in by_id:
            raise ValueError(f'Unknown resource: {identifier}')
        resource = by_id[identifier]
        if resource['acquisition'] != 'sample_approved':
            raise ValueError(f'Not admitted for acquisition: {identifier}')
        selected.append(resource)
    total = sum(f['bytes'] for r in selected for f in r['files'])
    if total > max_bytes:
        raise ValueError('Planned acquisition exceeds batch byte limit.')
    return selected, total


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('Redirect refused; review and pin the final source URL.')


class FigshareRedirect(urllib.request.HTTPRedirectHandler):
    """Allow one Figshare redirect to a provider-specific, reviewed S3 path."""
    def __init__(self, artifact):
        super().__init__()
        self.artifact = artifact

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        source = urlsplit(req.full_url)
        target = urlsplit(newurl)
        file_id = self.artifact['figshare_file_id']
        expected_source = f'https://ndownloader.figshare.com/files/{file_id}'
        prefix = self.artifact.get(
            'figshare_storage_prefix', FIGSHARE_STORAGE_PREFIXES['figshare_springernature'])
        if prefix not in FIGSHARE_STORAGE_PREFIXES.values():
            raise ValueError('Figshare storage prefix is not approved.')
        expected_path = f"/{prefix}/{file_id}/{self.artifact['name']}"
        if (code != 302 or req.full_url != expected_source
                or source.scheme != 'https' or source.hostname != 'ndownloader.figshare.com'
                or source.query or source.fragment
                or target.scheme != 'https' or target.hostname != 's3-eu-west-1.amazonaws.com'
                or target.port not in (None, 443) or target.username or target.password
                or target.path != expected_path or target.fragment or not target.query):
            raise ValueError('Figshare redirect did not match a reviewed provider S3 object.')
        # A second redirect is refused because req.full_url will no longer be the
        # exact ndownloader URL checked above.
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def verify_zenodo_record(resource, opener):
    """Match the pinned Zenodo record, declared license and each file checksum."""
    record_id = resource['zenodo_record_id']
    api_url = f'{ZENODO_ORIGIN}/api/records/{record_id}'
    request = urllib.request.Request(api_url, headers={
        'User-Agent': 'Talk2Nature-research-collection/1',
        'Accept': 'application/json', 'Accept-Encoding': 'identity'})
    with opener.open(request, timeout=30) as response:
        final_url = urlsplit(response.geturl())
        if (response.status != 200 or response.geturl() != api_url
                or final_url.scheme != 'https' or final_url.hostname != 'zenodo.org'
                or final_url.port not in (None, 443) or final_url.query or final_url.fragment):
            raise ValueError('Zenodo API response did not match the pinned record URL.')
        if response.headers.get('Content-Encoding', 'identity') != 'identity':
            raise ValueError('Encoded Zenodo API response refused.')
        if 'json' not in response.headers.get('Content-Type', '').lower():
            raise ValueError('Zenodo API response is not JSON.')
        payload = response.read(MAX_FILE_BYTES + 1)
    if len(payload) > MAX_FILE_BYTES:
        raise ValueError('Zenodo API manifest exceeds the metadata size limit.')
    try:
        record = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError('Zenodo API manifest is invalid JSON.') from exc
    metadata = record.get('metadata', {})
    license_entry = metadata.get('license') if isinstance(metadata, dict) else None
    if (record.get('id') != record_id or record.get('doi') != resource['zenodo_doi']
            or not isinstance(license_entry, dict) or license_entry.get('id') != 'cc-by-4.0'):
        raise ValueError('Zenodo record identity, DOI or license changed.')
    record_files = record.get('files')
    if not isinstance(record_files, list):
        raise ValueError('Zenodo record file manifest is missing.')
    for artifact in resource['files']:
        key = artifact['zenodo_file_key']
        matches = [entry for entry in record_files
                   if isinstance(entry, dict) and entry.get('key') == key]
        if len(matches) != 1:
            raise ValueError('Zenodo record does not contain exactly one pinned file.')
        entry = matches[0]
        expected_link = f'{ZENODO_ORIGIN}/api/records/{record_id}/files/{key}/content'
        if (entry.get('size') != artifact['bytes']
                or entry.get('checksum') != f'md5:{artifact["md5"]}'
                or entry.get('links', {}).get('self') != expected_link):
            raise ValueError('Zenodo file manifest changed from the pinned catalog record.')


def read_artifact(artifact, opener):
    request = urllib.request.Request(artifact['url'], headers={
        'User-Agent': 'Talk2Nature-research-collection/1', 'Accept-Encoding': 'identity'})
    with opener.open(request, timeout=30) as response:
        final_url = urlsplit(response.geturl())
        if response.status != 200:
            raise ValueError('Unexpected response status.')
        if 'figshare_file_id' in artifact:
            prefix = artifact.get(
                'figshare_storage_prefix', FIGSHARE_STORAGE_PREFIXES['figshare_springernature'])
            if prefix not in FIGSHARE_STORAGE_PREFIXES.values():
                raise ValueError('Unapproved Figshare storage prefix.')
            expected_path = f"/{prefix}/{artifact['figshare_file_id']}/{artifact['name']}"
            if (final_url.scheme != 'https' or final_url.hostname != 's3-eu-west-1.amazonaws.com'
                    or final_url.port not in (None, 443) or final_url.username or final_url.password
                    or final_url.path != expected_path or final_url.fragment or not final_url.query):
                raise ValueError('Unexpected final Figshare object URL.')
        elif response.geturl() != artifact['url']:
            raise ValueError('Unexpected response URL.')
        if response.headers.get('Content-Encoding', 'identity') != 'identity':
            raise ValueError('Encoded response refused.')
        if 'text/html' in response.headers.get('Content-Type', '').lower():
            raise ValueError('HTML is not the reviewed artifact.')
        declared = response.headers.get('Content-Length')
        if declared is not None and int(declared) != artifact['bytes']:
            raise ValueError('Source size changed.')
        # One sentinel byte detects an oversized response even without a header.
        data = response.read(artifact['bytes'] + 1)
    if len(data) != artifact['bytes']:
        raise ValueError('Downloaded size does not match reviewed size.')
    if 'sha256' in artifact:
        if hashlib.sha256(data).hexdigest() != artifact['sha256']:
            raise ValueError('Downloaded deposit SHA-256 mismatch.')
    elif 'zenodo_record_id' in artifact:
        if hashlib.md5(data, usedforsecurity=False).hexdigest() != artifact['md5']:
            raise ValueError('Downloaded Zenodo MD5 mismatch.')
    elif 'figshare_file_id' in artifact:
        if artifact.get('md5') is not None and hashlib.md5(data, usedforsecurity=False).hexdigest() != artifact['md5']:
            raise ValueError('Downloaded Figshare MD5 mismatch.')
    else:
        blob = b'blob ' + str(len(data)).encode() + b'\0' + data
        if hashlib.sha1(blob).hexdigest() != artifact['git_blob_sha1']:
            raise ValueError('Downloaded Git blob checksum mismatch.')
    return data


def acquire(catalog, identifiers, destination=DESTINATION, max_bytes=MAX_BATCH_BYTES,
            ca_file=None, opener=None):
    selected, total = plan(catalog, identifiers, max_bytes)
    destination = Path(destination)
    if any(p.is_symlink() for p in (destination, *destination.parents)):
        raise ValueError('Destination must not traverse symlinks.')
    destination.mkdir(parents=True, exist_ok=True, mode=0o700)
    catalog_hash = hashlib.sha256(json.dumps(catalog, sort_keys=True,
        separators=(',', ':')).encode()).hexdigest()
    # Fail rather than overwrite a previous collection or reuse an unchecked cache.
    for resource in selected:
        if (destination / resource['id']).exists():
            raise ValueError(f'Existing sample: {resource["id"]}; inspect its receipt before collecting again.')
    https_handler = urllib.request.HTTPSHandler(context=ssl.create_default_context(cafile=ca_file))
    receipts = []
    # Stage the whole batch. A failed fetch/check publishes no partial sample.
    with tempfile.TemporaryDirectory(prefix='.collect-', dir=destination) as staging:
        for resource in selected:
            resource_opener = opener
            if resource_opener is None:
                resource_opener = urllib.request.build_opener(NoRedirect(), https_handler)
            if resource.get('adapter') == 'zenodo_record':
                verify_zenodo_record(resource, resource_opener)
            folder = Path(staging) / resource['id']
            folder.mkdir(mode=0o700)
            entries = []
            for artifact in resource['files']:
                artifact_opener = opener
                if artifact_opener is None:
                    redirect_handler = (FigshareRedirect(artifact)
                        if 'figshare_file_id' in artifact else NoRedirect())
                    artifact_opener = urllib.request.build_opener(redirect_handler, https_handler)
                data = read_artifact(artifact, artifact_opener)
                target = folder / artifact['name']
                target.write_bytes(data)
                target.chmod(0o600)
                entry = {**artifact, 'sha256': hashlib.sha256(data).hexdigest()}
                entry['source_checksum_verified'] = (
                    'git_blob_sha1' in artifact or 'sha256' in artifact
                    or ('zenodo_record_id' in artifact and 'md5' in artifact)
                    or ('figshare_file_id' in artifact and artifact.get('md5') is not None))
                entries.append(entry)
            receipt = {'schema_version': 1, 'resource_id': resource['id'],
                'retrieved_at': datetime.now(timezone.utc).isoformat(),
                'catalog_sha256': catalog_hash, 'resource': resource, 'files': entries,
                'training_admitted': False,
                'note': 'Source sample only. No code execution, model evaluation or scientific admission.'}
            (folder / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
            receipts.append(receipt)
        for resource in selected:
            (Path(staging) / resource['id']).rename(destination / resource['id'])
    return {'resources': len(receipts), 'bytes': total,
            'receipts': [str(destination / r['resource_id'] / 'receipt.json') for r in receipts]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['validate', 'plan', 'fetch'])
    parser.add_argument('ids', nargs='*')
    parser.add_argument('--catalog', type=Path, default=CATALOG)
    parser.add_argument('--max-bytes', type=int, default=MAX_BATCH_BYTES)
    parser.add_argument('--ca-file', help='Optional trusted CA bundle; TLS verification stays enabled.')
    args = parser.parse_args()
    try:
        catalog = validate(json.loads(args.catalog.read_text()))
        if args.command == 'validate':
            result = {'valid': True, 'resources': len(catalog['resources'])}
        elif args.command == 'plan':
            selected, total = plan(catalog, args.ids, args.max_bytes)
            result = {'resources': [r['id'] for r in selected], 'bytes': total,
                      'destination': str(DESTINATION), 'network_used': False}
        else:
            result = acquire(catalog, args.ids, max_bytes=args.max_bytes, ca_file=args.ca_file)
        print(json.dumps(result, indent=2))
    except (ValueError, OSError) as exc:
        parser.exit(1, f'Collection stopped: {exc}\n')


if __name__ == '__main__':
    main()
