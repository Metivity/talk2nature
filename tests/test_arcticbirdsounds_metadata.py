import json
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlencode, urlsplit

from scripts import inspect_arcticbirdsounds as audit


def item(name, kind='file'):
    return {'attributes': {'name': name, 'kind': kind}}


class FakeResponse:
    status = 200
    headers = {
        'Content-Type': 'application/vnd.api+json',
        'Content-Length': '1',
        'Content-Encoding': 'identity',
    }

    def __init__(self, payload, url):
        self.payload = json.dumps(payload).encode()
        self.url = url

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def geturl(self):
        return self.url

    def read(self, maximum):
        return self.payload[:maximum]


class FakePaginatedOpener:
    def __init__(self, total_pages=3, bad_next=None):
        self.total_pages = total_pages
        self.bad_next = bad_next
        self.pages = []

    def open(self, request, timeout=None):
        parsed = urlsplit(request.full_url)
        query = parse_qs(parsed.query)
        page = int(query.get('page', ['1'])[0])
        self.pages.append(page)
        make_url = lambda number: (
            f'{parsed.scheme}://{parsed.netloc}{parsed.path}?'
            + urlencode({'page': number, 'page[size]': 100})
        )
        next_url = make_url(page + 1) if page < self.total_pages else None
        if self.bad_next is not None and page == 1:
            next_url = self.bad_next
        payload = {
            'data': [{'id': f'page-{page}', 'attributes': {'kind': 'file'}}],
            'links': {
                'next': next_url,
                'last': make_url(self.total_pages),
            },
        }
        return FakeResponse(payload, request.full_url)


class ArcticBirdSoundsMetadataTests(unittest.TestCase):
    def setUp(self):
        self.rows = audit._site_rows(
            b'plot,year,site,recorder_id,decimal_latitude,decimal_longitude\n'
            b'P1,2018,SiteA,REC001,70.123456,-40.123456\n'
            b'P2,2019,SiteB,REC002,71.123456,-41.123456\n'
        )
        self.audio = [
            item('2018_P1_20180621-133000_1.wav'),
            item('2019_P2_20190709-080000_2.wav'),
        ]
        self.annotations = [
            item('2018_P1_20180621-133000_1-tags.csv'),
            item('2018_P1_20180621-133000_1.flac'),
            item('2019_P2_20190709-080000_2-tags.csv'),
            item('2019_P2_20190709-080000_2.flac'),
        ]

    def test_partial_manifest_sample_never_becomes_a_holdout_claim(self):
        report = audit.summarize(
            self.rows, self.audio, self.annotations, 'a' * 64,
            {'pages_inspected': 1, 'total_pages': 16, 'complete': False},
            {'pages_inspected': 1, 'total_pages': 46, 'complete': False},
        )

        self.assertEqual(report['deployment_table']['distinct_sites'], 2)
        self.assertEqual(report['full_audio_manifest']['wav_files_in_inspected_pages'], 2)
        self.assertEqual(report['publisher_schema']['site_join_key'], 'year plus plot')
        self.assertEqual(report['full_audio_manifest']['unambiguous_plot_year_to_site_matches'], 2)
        self.assertEqual(report['annotation_file_manifest']['exact_csv_flac_schema_key_pairs'], 2)
        self.assertEqual(report['annotation_file_manifest']['distinct_plot_year_groups'], 2)
        self.assertEqual(report['annotation_file_manifest']['five_minute_recording_timestamp_groups'], 2)
        self.assertFalse(report['assessment']['complete_audio_corpus_file_to_site_mapping_verified'])
        self.assertFalse(report['assessment']['complete_annotation_corpus_to_site_mapping_verified'])
        self.assertFalse(report['assessment']['site_grouped_holdout_candidate'])

        serialized = json.dumps(report)
        for value in ('70.123456', '-40.123456', 'SiteA', 'REC001', '20180621-133000'):
            self.assertNotIn(value, serialized)

    def test_complete_join_is_only_a_candidate_not_model_readiness(self):
        report = audit.summarize(
            self.rows, self.audio, self.annotations, 'b' * 64,
            {'pages_inspected': 1, 'total_pages': 1, 'complete': True},
            {'pages_inspected': 1, 'total_pages': 1, 'complete': True},
        )

        self.assertTrue(report['assessment']['site_grouped_holdout_candidate'])
        self.assertFalse(report['assessment']['benchmark_ready'])
        self.assertFalse(report['payloads']['wav_bytes_downloaded_or_opened'])
        self.assertFalse(report['payloads']['annotation_rows_read'])

    def test_flac_audio_supports_complete_grouping_when_uncompressed_wav_is_partial(self):
        report = audit.summarize(
            self.rows,
            [item('2018_P1_20180621-133000_1.wav')],
            self.annotations,
            'e' * 64,
            {'pages_inspected': 1, 'total_pages': 1, 'complete': True},
            {'pages_inspected': 1, 'total_pages': 1, 'complete': True},
        )
        self.assertTrue(report['assessment']['site_grouped_holdout_candidate'])
        self.assertFalse(report['assessment']['uncompressed_wav_directory_covers_all_annotated_audio'])
        self.assertFalse(report['assessment']['benchmark_ready'])
        self.assertEqual(report['published_count_comparison']['paper_reported_plot_year_groups'], 20)
        self.assertEqual(report['published_count_comparison']['manifest_plot_year_groups'], 2)
        self.assertFalse(report['published_count_comparison']['source_count_discrepancy_resolved'])

    def test_publisher_key_parser_handles_tags_and_rejects_bad_timestamp(self):
        key = ('2018', 'p1', '20180621-133000', 10)
        self.assertEqual(audit._dataset_key('2018_P1_20180621-133000_10.flac'), key)
        self.assertEqual(audit._dataset_key('2018_P1_20180621-133000_10-tags.csv'), key)
        self.assertEqual(audit._dataset_key('2018 P1 20180621-133000 10.flac'), key)
        self.assertIsNone(audit._dataset_key('2018_P1_20180231-133000_10.flac'))
        self.assertIsNone(audit._dataset_key('2018_P1_20180621-133000_10.csv'))

    def test_ambiguous_plot_year_deployment_does_not_join_to_site(self):
        rows = self.rows + [dict(self.rows[0])]
        report = audit.summarize(
            rows, self.audio, self.annotations, 'c' * 64,
            {'pages_inspected': 1, 'total_pages': 1, 'complete': False},
            {'pages_inspected': 1, 'total_pages': 1, 'complete': False},
        )
        self.assertEqual(report['deployment_table']['ambiguous_year_plot_keys'], 1)
        self.assertEqual(report['full_audio_manifest']['unambiguous_plot_year_to_site_matches'], 1)

    def test_unpaired_flac_key_blocks_complete_annotation_mapping(self):
        annotations = self.annotations + [item('2018_P1_20180621-133000_3.flac')]
        report = audit.summarize(
            self.rows, self.audio, annotations, 'd' * 64,
            {'pages_inspected': 1, 'total_pages': 1, 'complete': True},
            {'pages_inspected': 1, 'total_pages': 1, 'complete': True},
        )
        self.assertEqual(report['annotation_file_manifest']['flac_keys_missing_matching_csv'], 1)
        self.assertFalse(report['assessment']['complete_annotation_corpus_to_site_mapping_verified'])

    def test_pagination_fetches_full_bounded_manifest_concurrently(self):
        opener = FakePaginatedOpener(total_pages=3)
        entries, manifest = audit._children(opener, audit.EXPECTED_AUDIO_FOLDER_ID)
        self.assertEqual(manifest, {
            'pages_inspected': 3,
            'total_pages': 3,
            'complete': True,
        })
        self.assertEqual({entry['id'] for entry in entries}, {
            'page-1', 'page-2', 'page-3',
        })

    def test_pagination_page_cap_stays_explicitly_incomplete(self):
        opener = FakePaginatedOpener(total_pages=3)
        with patch.object(audit, 'MAX_PAGES', 2):
            entries, manifest = audit._children(opener, audit.EXPECTED_AUDIO_FOLDER_ID)
        self.assertEqual(len(entries), 2)
        self.assertEqual(manifest['pages_inspected'], 2)
        self.assertEqual(manifest['total_pages'], 3)
        self.assertFalse(manifest['complete'])

    def test_pagination_host_and_folder_are_pinned(self):
        with self.assertRaises(ValueError):
            audit._validate_page_url(
                'https://example.com/v2/nodes/b9trx/files/osfstorage/folder/?page=2&page%5Bsize%5D=100',
                f'/v2/nodes/{audit.NODE_ID}/files/osfstorage/{audit.EXPECTED_AUDIO_FOLDER_ID}/',
                2,
            )

    def test_only_the_pinned_osf_object_storage_region_is_trusted(self):
        self.assertTrue(audit._trusted_host('api.osf.io'))
        self.assertTrue(audit._trusted_host(
            'bucket.compat.objectstorage.us-ashburn-1.oraclecloud.com'))
        self.assertFalse(audit._trusted_host(
            'bucket.compat.objectstorage.eu-frankfurt-1.oraclecloud.com'))
        self.assertFalse(audit._trusted_host('example.com'))


if __name__ == '__main__':
    unittest.main()
