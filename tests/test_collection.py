import copy
import hashlib
import csv
import io
import json
import tempfile
import urllib.request
import unittest
from pathlib import Path
from unittest.mock import Mock

from talk2nature.collection import (CATALOG, MAX_BATCH_BYTES,
                                    FigshareRedirect, NoRedirect,
                                    acquire, plan, read_artifact, validate,
                                    verify_zenodo_record)
from scripts.inspect_bat_annotations import inspect as inspect_bat
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
            'perch-hoplite-code', 'anuraset-code', 'budgerigar-vocal-signature-data',
            'egyptian-fruit-bat-annotations', 'egyptian-fruit-bat-metadata-pdf',
            'japanese-tit-core-merge-2022-data', 'japanese-tit-core-merge-2022-code',
            'northeastern-forest-bird-metadata-sample-v2', 'moth-plant-oviposition-data'})
        self.assertLess(size, MAX_BATCH_BYTES)

    def test_zenodo_metadata_sample_checks_record_license_manifest_and_file_md5(self):
        resource = copy.deepcopy(next(r for r in self.catalog['resources']
                                      if r['id'] == 'northeastern-forest-bird-metadata-sample-v2'))
        artifact = resource['files'][0]
        data = b'Park_ID,siteID\nACAD,ACAD1000\n'
        artifact['bytes'] = len(data)
        artifact['md5'] = hashlib.md5(data, usedforsecurity=False).hexdigest()
        resource['files'] = [artifact]
        catalog = {'schema_version': 1, 'resources': [resource]}
        api_url = 'https://zenodo.org/api/records/20038954'
        manifest = {
            'id': 20038954,
            'doi': '10.5281/zenodo.20038954',
            'metadata': {'license': {'id': 'cc-by-4.0'}},
            'files': [{'key': artifact['name'], 'size': len(data),
                       'checksum': f'md5:{artifact["md5"]}',
                       'links': {'self': artifact['url']}}],
        }
        api_bytes = json.dumps(manifest).encode()
        opener = Mock()
        opener.open.side_effect = [
            Response(api_bytes, api_url, {'Content-Type': 'application/json',
                                          'Content-Length': str(len(api_bytes))}),
            Response(data, artifact['url'], {'Content-Type': 'text/csv',
                                             'Content-Length': str(len(data))}),
        ]
        with tempfile.TemporaryDirectory() as temp:
            result = acquire(catalog, [resource['id']], Path(temp).resolve() / 'external', opener=opener)
            receipt = json.loads(Path(result['receipts'][0]).read_text())
            collected = Path(temp) / 'external' / resource['id'] / artifact['name']
            self.assertEqual(collected.read_bytes(), data)
            self.assertEqual(receipt['files'][0]['sha256'], hashlib.sha256(data).hexdigest())
            self.assertTrue(receipt['files'][0]['source_checksum_verified'])
            self.assertFalse(receipt['training_admitted'])

        for bad_record in [
            {**manifest, 'id': 99},
            {**manifest, 'metadata': {'license': {'id': 'cc-by-nc-4.0'}}},
            {**manifest, 'files': [{**manifest['files'][0], 'checksum': 'md5:' + '0' * 32}]},
        ]:
            with self.subTest(record=bad_record):
                bad_opener = Mock()
                bad_bytes = json.dumps(bad_record).encode()
                bad_opener.open.return_value = Response(
                    bad_bytes, api_url, {'Content-Type': 'application/json'})
                with self.assertRaises(ValueError):
                    verify_zenodo_record(resource, bad_opener)

    def test_coremerge_data_and_code_keep_component_rights_separate(self):
        by_id = {r['id']: r for r in self.catalog['resources']}
        data = by_id['japanese-tit-core-merge-2022-data']
        code = by_id['japanese-tit-core-merge-2022-code']
        self.assertEqual(data['kind'], 'dataset')
        self.assertEqual(code['kind'], 'code')
        self.assertEqual(data['source_ids'], [263])
        self.assertEqual(code['source_ids'], [263])
        self.assertEqual(data['rights']['license'], 'CC-BY-4.0')
        self.assertEqual(code['rights']['license'], 'CC-BY-4.0')
        self.assertIn('data files only', data['rights']['scope'])
        self.assertIn('analysis scripts only', code['rights']['scope'])
        self.assertEqual(
            [f['name'] for f in data['files']],
            ['merge_proportion.txt', 'merge_binary.txt'])
        self.assertEqual(
            [f['name'] for f in code['files']],
            ['merge_binary.R', 'merge_proportion.R'])
        self.assertEqual(
            {f['name']: f['md5'] for f in data['files']},
            {
                'merge_proportion.txt': '9166f5fe7f7f2b07ec9f86bd2ba8abe0',
                'merge_binary.txt': '0836e50688ef120cbfda07b3bfd1c839',
            })
        self.assertEqual(
            {f['name']: f['md5'] for f in code['files']},
            {
                'merge_binary.R': '8f68296f905ec2edf11d1751f92d4869',
                'merge_proportion.R': 'faa26e9876bf1dee7839ed7108b80885',
            })
        self.assertEqual(plan(self.catalog, [data['id'], code['id']])[1], 7064)

    def test_dog_bark_paper_data_and_code_keep_conflicting_or_missing_rights_unadmitted(self):
        records={r['id']:r for r in self.catalog['resources']}
        expected={
            'dog-bark-decoding-paper-2024': 'paper',
            'dog-bark-decoding-data-2024': 'dataset',
            'dog-bark-decoding-code-2024': 'code',
        }
        for identifier,kind in expected.items():
            resource=records[identifier]
            with self.subTest(resource=identifier):
                self.assertEqual(resource['kind'],kind)
                self.assertEqual(resource['source_ids'],[21])
                self.assertEqual(resource['acquisition'],'metadata_only')
                self.assertEqual(resource['files'],[])
                self.assertTrue(all(resource['rights'][field]=='unresolved'
                                    for field in ('research_use','commercial_use','redistribution')))
                with self.assertRaisesRegex(ValueError,'Not admitted'):
                    plan(self.catalog,[identifier])
        self.assertIn('PDF states CC BY-NC 4.0',records['dog-bark-decoding-paper-2024']['rights']['license'])
        self.assertIn('page-level notice states CC BY 4.0',records['dog-bark-decoding-paper-2024']['rights']['license'])
        self.assertIn('by-request availability is not a reuse license',records['dog-bark-decoding-data-2024']['rights']['license'])
        self.assertIn('by-request availability is not a code license',records['dog-bark-decoding-code-2024']['rights']['license'])

    def test_metadata_only_data_standards_are_catalogable_but_not_acquired(self):
        records = {r['id']: r for r in self.catalog['resources']}
        for identifier in ('darwin-core-data-package-standard', 'audubon-core-media-standard'):
            with self.subTest(resource=identifier):
                record = records[identifier]
                self.assertEqual(record['kind'], 'standard')
                self.assertEqual(record['acquisition'], 'metadata_only')
                self.assertEqual(record['files'], [])
                self.assertTrue(record['source_ids'])
                self.assertTrue(all(record['rights'][field] == 'unresolved'
                                    for field in ('research_use', 'commercial_use', 'redistribution')))
                with self.assertRaisesRegex(ValueError, 'Not admitted'):
                    plan(self.catalog, [identifier])

    def test_beans_zero_stays_a_metadata_only_comparison_not_commercial_input(self):
        records = {r['id']: r for r in self.catalog['resources']}
        dataset = records['beans-zero-benchmark-data']
        code = records['beans-zero-evaluation-code']
        self.assertEqual(dataset['rights']['commercial_use'], 'not_admitted')
        self.assertIn('91,965 examples', dataset['review_depth'])
        self.assertIn('50.5 GB', dataset['limitations'])
        self.assertIn('about 100 GB', dataset['limitations'])
        self.assertIn('Unresolved', code['rights']['license'])
        self.assertIn('no LICENSE', code['rights']['license'])
        self.assertIn('pyproject.toml declares no license', code['rights']['license'])
        for record in (dataset, code):
            with self.subTest(resource=record['id']):
                self.assertEqual(record['acquisition'], 'metadata_only')
                self.assertEqual(record['files'], [])
                with self.assertRaisesRegex(ValueError, 'Not admitted'):
                    plan(self.catalog, [record['id']])

    def test_bat_fileinfo_stays_metadata_only_and_pdf_has_explicit_missing_digest(self):
        by_id = {r['id']: r for r in self.catalog['resources']}
        fileinfo = by_id['egyptian-fruit-bat-fileinfo']
        metadata = by_id['egyptian-fruit-bat-metadata-pdf']
        self.assertEqual(fileinfo['acquisition'], 'metadata_only')
        self.assertEqual(fileinfo['files'], [])
        self.assertEqual(fileinfo['figshare_item_id'], 4555897)
        self.assertEqual(metadata['acquisition'], 'sample_approved')
        artifact = metadata['files'][0]
        self.assertEqual(artifact['figshare_file_id'], 8900800)
        self.assertIsNone(artifact['md5'])
        self.assertIn('md5=null', artifact['md5_unavailable_reason'])
        self.assertEqual(plan(self.catalog, [metadata['id']])[1], 367257)

    def test_fungal_electrophysiology_components_keep_rights_separate_and_unacquired(self):
        records = {r['id']: r for r in self.catalog['resources']}
        paper = records['fungal-electrophysiology-stimuli-2025-paper']
        dataset = records['fungal-electrophysiology-stimuli-2025-data']
        code = records['fungal-electrophysiology-stimuli-2025-method-s1']
        self.assertEqual(paper['rights']['license'], 'CC-BY-4.0 for the article as stated in the published paper')
        self.assertEqual(dataset['rights']['license'], 'CC-BY-4.0 as displayed on the Mendeley Data v1 record')
        self.assertIn('Unresolved', code['rights']['license'])
        self.assertIn('Method S1', code['version'])
        self.assertIn('Document S2', code['version'])
        self.assertIn('not inspected or executed', code['review_depth'])
        for record in (paper, dataset, code):
            with self.subTest(resource=record['id']):
                self.assertEqual(record['acquisition'], 'metadata_only')
                self.assertEqual(record['files'], [])
        self.assertEqual(dataset['kind'], 'dataset')
        self.assertEqual(code['kind'], 'code')

    def test_mendeley_sample_is_versioned_hash_pinned_and_not_training_admitted(self):
        r = copy.deepcopy(next(r for r in self.catalog['resources'] if r['id'] == 'budgerigar-vocal-signature-data'))
        a = r['files'][0]
        a['bytes'] = len(self.data)
        a['sha256'] = hashlib.sha256(self.data).hexdigest()
        c = {'schema_version': 1, 'resources': [r]}
        with tempfile.TemporaryDirectory() as temp:
            result = acquire(c, [r['id']], Path(temp).resolve(), opener=self.opener())
            receipt = json.loads(Path(result['receipts'][0]).read_text())
            self.assertFalse(receipt['training_admitted'])
            self.assertEqual(receipt['resource']['license_notice'], r['license_notice'])
        for key, value in [('sha256', '0'*64), ('bytes', len(self.data)+1)]:
            changed = {**a, key:value}
            with self.assertRaises(ValueError):
                read_artifact(changed, self.opener())
        for key, value in [('url', a['url']+'?x=1'), ('url', a['url'].replace('https:', 'http:')), ('sha256','bad'), ('source_url',a['source_url'].replace('j8rpy4dc6c','different0')), ('git_blob_sha1','a'*40)]:
            bad = copy.deepcopy(c);bad['resources'][0]['files'][0][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError): validate(bad)
        for key, value in [('adapter','unknown'), ('version','latest'), ('license_notice','')]:
            bad = copy.deepcopy(c);bad['resources'][0][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError): validate(bad)

    def test_figshare_sample_pins_item_redirect_size_md5_and_stays_out_of_training(self):
        data = b'Annotation metadata fixture; no biological rows.\n'
        item_url = 'https://api.figshare.com/v2/articles/42'
        artifact = {
            'name': 'Annotations.csv',
            'url': 'https://ndownloader.figshare.com/files/7379008',
            'source_url': item_url,
            'figshare_file_id': 7379008,
            'bytes': len(data),
            'md5': hashlib.md5(data, usedforsecurity=False).hexdigest(),
        }
        resource = {
            'id': 'figshare-test', 'kind': 'dataset', 'title': 'Synthetic Figshare test item',
            'url': item_url, 'figshare_item_id': 42, 'version': 'Figshare item 42 v1',
            'reviewed': '2026-10-11', 'priority': 1, 'review_depth': 'Synthetic metadata fixture.',
            'task': 'Test item and file pinning.', 'access': 'Synthetic only.',
            'decision': 'Test only.', 'limitations': 'No real data.', 'attribution': 'Fixture.',
            'rights': {'license': 'CC0-1.0', 'scope': 'Synthetic item.',
                       'evidence_url': item_url, 'conditions': 'Fixture.',
                       'research_use': 'conditional', 'commercial_use': 'conditional',
                       'redistribution': 'conditional'},
            'license_notice': 'Synthetic CC0 metadata notice.',
            'acquisition': 'sample_approved', 'adapter': 'figshare_springernature',
            'admission_reason': 'Synthetic checksum and path verification only.', 'files': [artifact],
        }
        catalog = {'schema_version': 1, 'resources': [resource]}
        validate(catalog)
        selected, size = plan(catalog, ['figshare-test'])
        self.assertEqual(size, len(data))

        target = ('https://s3-eu-west-1.amazonaws.com/pstorage-npg-968563215/'
                  '7379008/Annotations.csv?X-Amz-Signature=fixture')
        handler = FigshareRedirect(artifact)
        request = urllib.request.Request(artifact['url'])
        redirected = handler.redirect_request(request, None, 302, 'Found', {}, target)
        self.assertEqual(redirected.full_url, target)
        for bad_target in (
            target.replace('s3-eu-west-1.amazonaws.com', 'evil.example'),
            target.replace('/7379008/Annotations.csv', '/7379008/Other.csv'),
            target.replace('https://', 'http://'),
        ):
            with self.subTest(target=bad_target), self.assertRaisesRegex(ValueError, 'redirect'):
                handler.redirect_request(request, None, 302, 'Found', {}, bad_target)
        with self.assertRaisesRegex(ValueError, 'redirect'):
            handler.redirect_request(urllib.request.Request(target), None, 302, 'Found', {}, target)

        opener = Mock()
        opener.open.side_effect = lambda request, timeout: Response(
            data, target, {'Content-Length': str(len(data))})
        self.assertEqual(read_artifact(artifact, opener), data)
        for key, value in [('md5', '0' * 32), ('bytes', len(data) + 1)]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                read_artifact({**artifact, key: value}, opener)
        wrong_target_opener = Mock()
        wrong_target_opener.open.side_effect = lambda request, timeout: Response(
            data, target.replace('s3-eu-west-1.amazonaws.com', 'evil.example'))
        with self.assertRaisesRegex(ValueError, 'final Figshare'):
            read_artifact(artifact, wrong_target_opener)

        with tempfile.TemporaryDirectory() as temp:
            result = acquire(catalog, ['figshare-test'], Path(temp).resolve(), opener=opener)
            receipt = json.loads(Path(result['receipts'][0]).read_text())
            self.assertFalse(receipt['training_admitted'])
            self.assertEqual(receipt['files'][0]['md5'], artifact['md5'])
            self.assertEqual(receipt['files'][0]['sha256'], hashlib.sha256(data).hexdigest())
            self.assertNotIn('X-Amz-Signature', json.dumps(receipt))

    def test_public_figshare_sample_pins_its_provider_path_without_upstream_md5(self):
        data = b'flock\torder\tresponse\n1\talert-recruitment\tmobbing\n'
        item_url = 'https://api.figshare.com/v2/articles/18007046'
        artifact = {
            'name': 'merge_binary.txt',
            'url': 'https://ndownloader.figshare.com/files/35870855',
            'source_url': item_url,
            'figshare_file_id': 35870855,
            'figshare_storage_prefix': 'pfigshare-u-files',
            'bytes': len(data),
            'md5': None,
            'md5_unavailable_reason': 'The official Figshare API returned md5=null.',
        }
        resource = {
            'id': 'figshare-public-test', 'kind': 'dataset', 'title': 'Synthetic Figshare public item',
            'url': item_url, 'figshare_item_id': 18007046,
            'version': 'Figshare item 18007046 v1',
            'reviewed': '2026-10-13', 'priority': 1,
            'review_depth': 'Synthetic public-Figshare path fixture.',
            'task': 'Test an explicitly reviewed provider path.', 'access': 'Synthetic only.',
            'decision': 'Test only.', 'limitations': 'No real data.', 'attribution': 'Fixture.',
            'rights': {'license': 'CC-BY-4.0', 'scope': 'Synthetic item.',
                       'evidence_url': item_url, 'conditions': 'Fixture.',
                       'research_use': 'conditional', 'commercial_use': 'conditional',
                       'redistribution': 'conditional'},
            'license_notice': 'Synthetic item metadata declares CC BY 4.0.',
            'acquisition': 'sample_approved', 'adapter': 'figshare_public',
            'admission_reason': 'Synthetic path, size and local-hash verification only.',
            'files': [artifact],
        }
        catalog = {'schema_version': 1, 'resources': [resource]}
        validate(catalog)
        self.assertEqual(plan(catalog, ['figshare-public-test'])[1], len(data))

        target = ('https://s3-eu-west-1.amazonaws.com/pfigshare-u-files/'
                  '35870855/merge_binary.txt?X-Amz-Signature=fixture')
        handler = FigshareRedirect(artifact)
        request = urllib.request.Request(artifact['url'])
        self.assertEqual(
            handler.redirect_request(request, None, 302, 'Found', {}, target).full_url,
            target)
        with self.assertRaisesRegex(ValueError, 'redirect'):
            handler.redirect_request(
                request, None, 302, 'Found', {},
                target.replace('pfigshare-u-files', 'pstorage-npg-968563215'))

        opener = Mock()
        opener.open.side_effect = lambda request, timeout: Response(
            data, target, {'Content-Length': str(len(data))})
        self.assertEqual(read_artifact(artifact, opener), data)
        with tempfile.TemporaryDirectory() as temp:
            result = acquire(catalog, ['figshare-public-test'], Path(temp).resolve(), opener=opener)
            receipt = json.loads(Path(result['receipts'][0]).read_text())
            file_receipt = receipt['files'][0]
            self.assertFalse(receipt['training_admitted'])
            self.assertIsNone(file_receipt['md5'])
            self.assertFalse(file_receipt['source_checksum_verified'])
            self.assertEqual(file_receipt['sha256'], hashlib.sha256(data).hexdigest())
            self.assertNotIn('X-Amz-Signature', json.dumps(receipt))

    def test_figshare_missing_upstream_md5_is_explicit_and_receipt_does_not_overclaim(self):
        data = b'%PDF-1.7\nsynthetic metadata fixture\n'
        item_url = 'https://api.figshare.com/v2/articles/4555900'
        artifact = {
            'name': 'Metadata.pdf',
            'url': 'https://ndownloader.figshare.com/files/8900800',
            'source_url': item_url,
            'figshare_file_id': 8900800,
            'bytes': len(data),
            'md5': None,
            'md5_unavailable_reason': 'The public Figshare item API returned md5=null.',
        }
        resource = {
            'id': 'figshare-pdf-test', 'kind': 'dataset', 'title': 'Synthetic Figshare PDF item',
            'url': item_url, 'figshare_item_id': 4555900, 'version': 'Figshare item 4555900 v1',
            'reviewed': '2026-10-12', 'priority': 1, 'review_depth': 'Synthetic metadata fixture.',
            'task': 'Test bounded retrieval without an upstream digest.', 'access': 'Synthetic only.',
            'decision': 'Test only.', 'limitations': 'No real data.', 'attribution': 'Fixture.',
            'rights': {'license': 'CC0-1.0', 'scope': 'Synthetic item.',
                       'evidence_url': item_url, 'conditions': 'Fixture.',
                       'research_use': 'conditional', 'commercial_use': 'conditional',
                       'redistribution': 'conditional'},
            'license_notice': 'Synthetic CC0 metadata notice.',
            'acquisition': 'sample_approved', 'adapter': 'figshare_springernature',
            'admission_reason': 'Test size/TLS provenance and local checksum only.', 'files': [artifact],
        }
        catalog = {'schema_version': 1, 'resources': [resource]}
        validate(catalog)
        target = ('https://s3-eu-west-1.amazonaws.com/pstorage-npg-968563215/'
                  '8900800/Metadata.pdf?X-Amz-Signature=fixture')
        opener = Mock()
        opener.open.side_effect = lambda request, timeout: Response(
            data, target, {'Content-Length': str(len(data)), 'Content-Type': 'application/pdf'})

        with tempfile.TemporaryDirectory() as temp:
            result = acquire(catalog, [resource['id']], Path(temp).resolve(), opener=opener)
            receipt = json.loads(Path(result['receipts'][0]).read_text())
            file_receipt = receipt['files'][0]
            self.assertFalse(receipt['training_admitted'])
            self.assertIsNone(file_receipt['md5'])
            self.assertFalse(file_receipt['source_checksum_verified'])
            self.assertEqual(file_receipt['sha256'], hashlib.sha256(data).hexdigest())
            self.assertNotIn('X-Amz-Signature', json.dumps(receipt))

        invalid = copy.deepcopy(catalog)
        del invalid['resources'][0]['files'][0]['md5_unavailable_reason']
        with self.assertRaisesRegex(ValueError, 'md5_unavailable_reason'):
            validate(invalid)

    def test_declared_cc0_dataset_license_does_not_admit_unreviewed_archive(self):
        with self.assertRaisesRegex(ValueError, 'Not admitted'):
            plan(self.catalog, ['beans-next'])
        parrotlet=next(r for r in self.catalog['resources'] if r['id']=='parrotlet-vocal-babbling-data')
        self.assertEqual(parrotlet['acquisition'],'metadata_only')
        self.assertEqual(parrotlet['files'],[])
        self.assertIn('CC0',parrotlet['rights']['license'])
        self.assertEqual(parrotlet['rights']['research_use'],'conditional')
        self.assertEqual(parrotlet['rights']['commercial_use'],'conditional')
        self.assertEqual(parrotlet['rights']['redistribution'],'conditional')
        self.assertEqual(parrotlet['api_version_record']['version_number'],6)
        self.assertEqual(sum(item['bytes'] for item in parrotlet['api_file_inventory']),2600218232)
        readme=next(item for item in parrotlet['api_file_inventory'] if item['name']=='README20220326.csv')
        self.assertEqual(readme['sha256'],'ae6e5cdf1067de3a11a5561a304a4bea47ba816b2c7f4063fdc98a1f417daf50')
        with self.assertRaisesRegex(ValueError, 'Not admitted'):
            plan(self.catalog,[parrotlet['id']])
        retrieval=next(r for r in self.catalog['resources'] if r['id']=='prompting-mammalps-s2-retrieval-data')
        self.assertEqual(retrieval['acquisition'],'metadata_only')
        self.assertEqual(retrieval['rights']['license'],'CC-BY-NC-4.0')
        self.assertEqual(retrieval['rights']['commercial_use'],'not_admitted')
        self.assertEqual(retrieval['files'],[])
        with self.assertRaisesRegex(ValueError, 'Not admitted'):
            plan(self.catalog,[retrieval['id']])
        retrieval_code=next(r for r in self.catalog['resources'] if r['id']=='prompting-mammalps-retrieval-code')
        self.assertIn('unresolved',retrieval_code['rights']['license'])
        self.assertEqual(retrieval_code['files'],[])
        with self.assertRaisesRegex(ValueError, 'Not admitted'):
            plan(self.catalog,[retrieval_code['id']])
        bat_archive=next(r for r in self.catalog['resources'] if r['id']=='egyptian-fruit-bat-audiovisual-archive')
        self.assertEqual(bat_archive['acquisition'],'metadata_only')
        self.assertIn('CC0-1.0 declared at the Figshare item level',bat_archive['rights']['license'])
        self.assertIn('3,049,199,327-byte file',bat_archive['rights']['conditions'])
        self.assertEqual(bat_archive['rights']['research_use'],'conditional')
        self.assertEqual(bat_archive['files'],[])
        with self.assertRaisesRegex(ValueError, 'Not admitted'):
            plan(self.catalog,[bat_archive['id']])
        bat_encodings=next(r for r in self.catalog['resources'] if r['id']=='fruit-bat-sequence-encodings')
        self.assertEqual(bat_encodings['acquisition'],'metadata_only')
        self.assertIn('CC-BY-4.0',bat_encodings['rights']['license'])
        self.assertIn('separate 2017 archive',bat_encodings['decision'])
        self.assertIn('old=2&new=3',bat_encodings['rights']['evidence_url'])
        self.assertIn('v1 contained metadata only',bat_encodings['review_depth'])
        self.assertIn('OAuth2',bat_encodings['review_depth'])
        self.assertIn('HTTP 401',bat_encodings['review_depth'])
        self.assertIn('Versions 2 and 3',bat_encodings['access'])
        self.assertEqual(bat_encodings['files'],[])
        with self.assertRaisesRegex(ValueError, 'Not admitted'):
            plan(self.catalog,[bat_encodings['id']])
        for field, value in [('license', 'unknown'), ('commercial_use', 'unresolved')]:
            with self.subTest(field=field):
                c = copy.deepcopy(self.sample)
                c['resources'][0]['rights'][field] = value
                with self.assertRaises(ValueError):
                    validate(c)

    def test_meerkat_components_keep_separate_rights_and_stay_metadata_only(self):
        by_id = {r['id']: r for r in self.catalog['resources']}
        expected = {
            'animal2vec-meerkat-paper-final': 'paper',
            'meerkat-audio-label-dataset': 'dataset',
            'animal2vec-code': 'code',
            'animal2vec-model-weights': 'model',
        }
        for identifier, kind in expected.items():
            with self.subTest(resource=identifier):
                resource = by_id[identifier]
                self.assertEqual(resource['kind'], kind)
                self.assertEqual(resource['acquisition'], 'metadata_only')
                self.assertEqual(resource['files'], [])
                with self.assertRaisesRegex(ValueError, 'Not admitted'):
                    plan(self.catalog, [identifier])
        self.assertEqual(by_id['meerkat-audio-label-dataset']['rights']['license'],
                         'CC-BY-NC-4.0 as stated in the peer-reviewed paper')
        self.assertEqual(by_id['meerkat-audio-label-dataset']['rights']['commercial_use'],
                         'not_admitted')
        self.assertIn('MIT', by_id['animal2vec-code']['rights']['license'])
        self.assertIn('CC-BY-NC-4.0', by_id['animal2vec-model-weights']['rights']['license'])

    def test_dupont_lark_dataset_rights_and_acquisition_gate_are_separate(self):
        resource = next(r for r in self.catalog['resources'] if r['id'] == 'duponts-lark-vocal-types-2026')
        self.assertEqual(resource['kind'], 'dataset')
        self.assertEqual(resource['source_ids'], [194, 195, 196, 212])
        self.assertEqual(resource['acquisition'], 'metadata_only')
        self.assertEqual(resource['files'], [])
        self.assertIn('CC BY 4.0 is declared', resource['rights']['license'])
        self.assertIn('CC BY-NC-ND 4.0', resource['rights']['scope'])
        self.assertEqual(resource['rights']['commercial_use'], 'conditional')
        with self.assertRaisesRegex(ValueError, 'Not admitted'):
            plan(self.catalog, [resource['id']])

        code = next(r for r in self.catalog['resources'] if r['id'] == 'duponts-lark-technical-validation-r-2026')
        self.assertEqual(code['kind'], 'code')
        self.assertEqual(code['acquisition'], 'metadata_only')
        self.assertEqual(code['files'], [])
        self.assertIn('record-level license metadata declares CC BY 4.0', code['rights']['license'])
        self.assertEqual(code['rights']['research_use'], 'conditional')
        with self.assertRaisesRegex(ValueError, 'Not admitted'):
            plan(self.catalog, [code['id']])

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

    def test_bat_annotation_report_is_aggregate_and_checks_receipt(self):
        columns = ['FileID', 'Emitter', 'Addressee', 'Context',
                   'Emitter pre-vocalization action', 'Addressee pre-vocalization action',
                   'Emitter post-vocalization action', 'Addressee post-vocalization action',
                   'Start sample', 'End sample']
        rows = [
            ['private-file-key', '-101', '102', '0', '1', '2', '3', '4', '10', '20'],
            ['private-file-key', '101', '102', '12', '0', '0', '0', '0', '10', '20'],
            ['private-file-key-2', '103', '104', '3', '1', '2', '3', '4', '30', '40'],
            ['private-file-key-3', '102', '103', '4', '1', '2', '3', '4', '50', '60'],
            ['private-file-key-4', '0', '104', '0', '0', '0', '0', '0', '70', '80'],
        ]
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(columns)
        writer.writerows(rows)
        data = output.getvalue().encode()
        with tempfile.TemporaryDirectory(dir=Path(tempfile.gettempdir()).resolve()) as temp:
            folder = Path(temp)
            (folder / 'Annotations.csv').write_bytes(data)
            receipt = {
                'resource_id': 'egyptian-fruit-bat-annotations',
                'resource': {'version': 'Figshare item 4555903 v1; DOI fixture'},
                'training_admitted': False,
                'files': [{'name': 'Annotations.csv', 'bytes': len(data),
                           'md5': hashlib.md5(data, usedforsecurity=False).hexdigest(),
                           'sha256': hashlib.sha256(data).hexdigest(),
                           'url': 'https://example.test/Annotations.csv'}],
            }
            (folder / 'receipt.json').write_text(json.dumps(receipt))
            report = inspect_bat(folder)
            serialized = json.dumps(report)
            self.assertEqual(report['rows'], 5)
            self.assertEqual(report['unique_file_ids'], 4)
            self.assertEqual(report['rows_beyond_unique_file_ids'], 1)
            self.assertEqual(report['duplicate_file_interval_rows'], 1)
            self.assertEqual(report['negative_ambiguous_identity_rows']['emitter'], 1)
            self.assertEqual(report['participant_pair_structure'], {
                'unique_known_ids_across_both_roles': 4,
                'unique_ids_in_emitter_field': 3,
                'unique_ids_in_addressee_field': 3,
                'rows_with_two_identified_participants': 4,
                'unique_interacting_pairs': 3,
                'connected_components_among_pair_linked_ids': 1,
                'largest_pair_component_ids': 4,
                'known_ids_without_a_pair_edge': 0,
            })
            self.assertFalse(report['training_admitted'])
            self.assertNotIn('private-file-key', serialized)
            self.assertNotIn('-101', serialized)
            for identity in ('101', '102', '103', '104'):
                self.assertNotIn(identity, serialized)
            (folder / 'Annotations.csv').write_bytes(data + b'changed')
            with self.assertRaisesRegex(ValueError, 'differs'):
                inspect_bat(folder)


if __name__ == '__main__':
    unittest.main()
