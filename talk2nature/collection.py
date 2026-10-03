"""Catalog and acquire small reviewed research samples, without executing them.

License/admission fields are human-reviewed declarations, not legal or scientific
verification. Adapters support immutable GitHub files and reviewed Mendeley files
with deposit SHA-256 checksums and a pinned public S3 URL. Downloads
are not training releases and never enter the private admin or website build.
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
        if resource.get('kind') not in {'paper', 'code', 'dataset', 'model'}:
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
                else:
                    uuid = r'[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}'
                    if (parsed.hostname != 'prod-dcd-datasets-public-files-eu-west-1.s3.eu-west-1.amazonaws.com'
                            or parsed.query or parsed.fragment or not re.fullmatch('/' + uuid, parsed.path)):
                        raise ValueError('Mendeley artifact must pin the reviewed public S3 object.')
                    if not re.fullmatch('[a-f0-9]{64}', require_text(artifact, 'sha256')) or 'git_blob_sha1' in artifact:
                        raise ValueError('Missing or ambiguous deposit SHA-256.')
                    if not re.fullmatch(re.escape(f'https://data.mendeley.com/public-files/datasets/{deposit[1]}/files/') + uuid + '/file_downloaded', require_text(artifact, 'source_url')):
                        raise ValueError('Artifact provenance must match the named deposit.')
                if type(artifact.get('bytes')) is not int or not 0 < artifact['bytes'] <= MAX_FILE_BYTES:
                    raise ValueError('Artifact exceeds file limit or has invalid size.')
            if adapter == 'github' and resource.get('license_file') not in names:
                raise ValueError('Every sample must retain a license file.')
    return catalog


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


def read_artifact(artifact, opener):
    request = urllib.request.Request(artifact['url'], headers={
        'User-Agent': 'Talk2Nature-research-collection/1', 'Accept-Encoding': 'identity'})
    with opener.open(request, timeout=30) as response:
        if response.status != 200 or response.geturl() != artifact['url']:
            raise ValueError('Unexpected response status or URL.')
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
    if opener is None:
        opener = urllib.request.build_opener(NoRedirect(),
            urllib.request.HTTPSHandler(context=ssl.create_default_context(cafile=ca_file)))
    receipts = []
    # Stage the whole batch. A failed fetch/check publishes no partial sample.
    with tempfile.TemporaryDirectory(prefix='.collect-', dir=destination) as staging:
        for resource in selected:
            folder = Path(staging) / resource['id']
            folder.mkdir(mode=0o700)
            entries = []
            for artifact in resource['files']:
                data = read_artifact(artifact, opener)
                target = folder / artifact['name']
                target.write_bytes(data)
                target.chmod(0o600)
                entries.append({**artifact, 'sha256': hashlib.sha256(data).hexdigest()})
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
