import copy
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from talk2nature.collection import (CATALOG, MAX_BATCH_BYTES, NoRedirect,
                                    acquire, plan, read_artifact, validate)
from scripts.inspect_parrot_annotations import inspect


class Response(io.BytesIO):
    status = 200

    def __init__(self, data, url, headers=None):
        super().__init__(data)
        self.url = url
        self.headers = headers or {}

    def geturl(self):
        return self.url


class CollectionTests(unittest.TestCase):
    def setUp(self):
        self.catalog = json.loads(CATALOG.read_text())
        resource = copy.deepcopy(next(r for r in self.catalog['resources']
                                      if r['id'] == 'monk-parakeet-code'))
        resource['files'] = [resource['files'][0]]
        self.data = b'Synthetic test license bytes; never executed.\n'
        self.artifact = resource['files'][0]
        self.artifact['bytes'] = len(self.data)
        self.artifact['git_blob_sha1'] = hashlib.sha1(
            b'blob ' + str(len(self.data)).encode() + b'\0' + self.data).hexdigest()
        self.sample = {'schema_version': 1, 'resources': [resource]}
        self.identifier = resource['id']

    def opener(self, data=None, headers=None):
        result = Mock()
        result.open.side_effect = lambda request, timeout: Response(
            self.data if data is None else data, request.full_url, headers)
        return result

    def test_repository_catalog_and_offline_plan(self):
        validate(self.catalog)
        ids = [r['id'] for r in self.catalog['resources'] if r['acquisition'] == 'sample_approved']
        selected, size = plan(self.catalog, ids)
        self.assertEqual({r['id'] for r in selected}, {
            'monk-parakeet-code', 'monk-parakeet-annotations',
            'perch-hoplite-code', 'anuraset-code'})
        self.assertLess(size, 150_000)

    def test_unresolved_licenses_and_metadata_cannot_download(self):
        with self.assertRaisesRegex(ValueError, 'Not admitted'):
            plan(self.catalog, ['beans-next'])
        for field, value in [('license', 'unknown'), ('commercial_use', 'unresolved')]:
            with self.subTest(field=field):
                c = copy.deepcopy(self.sample)
                c['resources'][0]['rights'][field] = value
                with self.assertRaises(ValueError):
                    validate(c)

    def test_version_urls_and_local_names_are_constrained(self):
        invalid = [
            ('url', self.artifact['url'].replace('raw.githubusercontent.com', 'localhost')),
            ('url', self.artifact['url'].replace('https:', 'file:')),
            ('url', self.artifact['url'].replace('https://', 'https://user:secret@')),
            ('url', self.artifact['url'].replace(self.sample['resources'][0]['version'], 'main')),
            ('url', self.artifact['url'] + '?token=secret'),
            ('name', '../outside'), ('name', 'receipt.json'),
        ]
        for field, value in invalid:
            with self.subTest(field=field, value=value):
                c = copy.deepcopy(self.sample)
                c['resources'][0]['files'][0][field] = value
                with self.assertRaises(ValueError):
                    validate(c)

    def test_duplicate_ids_files_and_missing_notice_rejected(self):
        changes = ('id', 'file', 'license')
        for change in changes:
            c = copy.deepcopy(self.sample)
            if change == 'id':
                c['resources'].append(c['resources'][0])
            elif change == 'file':
                c['resources'][0]['files'].append(c['resources'][0]['files'][0])
            else:
                c['resources'][0]['license_file'] = 'missing'
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate(c)

    def test_acquisition_limits_checked_before_network(self):
        for limit in (0, -1, True, MAX_BATCH_BYTES + 1, len(self.data) - 1):
            with self.subTest(limit=limit), self.assertRaises(ValueError):
                plan(self.sample, [self.identifier], limit)
        with self.assertRaises(ValueError):
            plan(self.sample, [self.identifier, self.identifier])
        with self.assertRaises(ValueError):
            plan(self.sample, ['absent'])

    def test_success_retains_attribution_hashes_and_no_training_claim(self):
        with tempfile.TemporaryDirectory(dir=Path(tempfile.gettempdir()).resolve()) as temp:
            result = acquire(self.sample, [self.identifier], temp, opener=self.opener())
            receipt = json.loads(Path(result['receipts'][0]).read_text())
            self.assertEqual(receipt['files'][0]['sha256'], hashlib.sha256(self.data).hexdigest())
            self.assertEqual(receipt['resource']['rights'], self.sample['resources'][0]['rights'])
            self.assertTrue(receipt['resource']['attribution'])
            self.assertTrue(receipt['catalog_sha256'])
            self.assertFalse(receipt['training_admitted'])
            self.assertEqual((Path(temp) / self.identifier / self.artifact['name']).read_bytes(), self.data)
            with self.assertRaisesRegex(ValueError, 'Existing sample'):
                acquire(self.sample, [self.identifier], temp, opener=self.opener())

    def test_tamper_short_and_oversize_responses_publish_nothing(self):
        for data in (b'x' * len(self.data), self.data[:-1], self.data + b'x'):
            with self.subTest(length=len(data)), tempfile.TemporaryDirectory(dir=Path(tempfile.gettempdir()).resolve()) as temp:
                with self.assertRaises(ValueError):
                    acquire(self.sample, [self.identifier], temp, opener=self.opener(data))
                self.assertEqual(list(Path(temp).iterdir()), [])

    def test_second_file_failure_does_not_publish_first_file(self):
        c = copy.deepcopy(self.sample)
        second = dict(self.artifact, name='second.txt')
        c['resources'][0]['files'].append(second)
        opener = self.opener()
        opener.open.side_effect = [Response(self.data, self.artifact['url']), OSError('network failed')]
        with tempfile.TemporaryDirectory(dir=Path(tempfile.gettempdir()).resolve()) as temp:
            with self.assertRaises(OSError):
                acquire(c, [self.identifier], temp, opener=opener)
            self.assertEqual(list(Path(temp).iterdir()), [])

    def test_response_headers_and_url_cannot_change_artifact(self):
        for headers in ({'Content-Length': '999'}, {'Content-Encoding': 'gzip'},
                        {'Content-Type': 'text/html; charset=UTF-8'}):
            with self.subTest(headers=headers), self.assertRaises(ValueError):
                read_artifact(self.artifact, self.opener(headers=headers))
        opener = Mock()
        opener.open.return_value = Response(self.data, 'https://other.example/file')
        with self.assertRaisesRegex(ValueError, 'URL'):
            read_artifact(self.artifact, opener)

    def test_redirects_and_symlink_destination_refused(self):
        with self.assertRaisesRegex(ValueError, 'Redirect'):
            NoRedirect().redirect_request(None, None, 302, '', {}, 'https://other.example')
        with tempfile.TemporaryDirectory(dir=Path(tempfile.gettempdir()).resolve()) as temp:
            target = Path(temp) / 'target'
            target.mkdir()
            link = Path(temp) / 'link'
            link.symlink_to(target, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, 'symlink'):
                acquire(self.sample, [self.identifier], link, opener=self.opener())
            self.assertEqual(list(target.iterdir()), [])

    def test_annotation_report_is_aggregate_and_checks_its_source(self):
        data = ('annotation_ref;uncertain;bird;behaviour;location;others;association;notes\n'
                'fixture-1;1;synthetic-bird;moving;private-place;;;private-note\n'
                'fixture-2;;;;;;;\n').encode()
        with tempfile.TemporaryDirectory(dir=Path(tempfile.gettempdir()).resolve()) as temp:
            root = Path(temp)
            (root / 'annotations-2020.csv').write_bytes(data)
            receipt = {'resource_id': 'synthetic-fixture', 'resource': {'version': 'test'},
                       'files': [{'name': 'annotations-2020.csv', 'sha256': hashlib.sha256(data).hexdigest(),
                                  'url': 'https://example.test/synthetic'}]}
            (root / 'receipt.json').write_text(json.dumps(receipt))
            report = inspect(root)
            self.assertEqual(report['rows'], 2)
            self.assertEqual(report['nonempty']['behaviour'], 1)
            self.assertEqual(report['uncertainty_flag_1'], 1)
            self.assertEqual(report['unique_nonempty_behavior_strings'], 1)
            self.assertNotIn('private-place', json.dumps(report))
            self.assertNotIn('private-note', json.dumps(report))
            self.assertNotIn('synthetic-bird', json.dumps(report))
            (root / 'annotations-2020.csv').write_bytes(data + b'changed')
            with self.assertRaisesRegex(ValueError, 'differs'):
                inspect(root)


if __name__ == '__main__':
    unittest.main()
