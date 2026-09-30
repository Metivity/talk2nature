import json
import tempfile
import unittest
from pathlib import Path
from web.build import build, load
from scripts.check_site import check_site


class SiteTests(unittest.TestCase):
    def test_local_preview_is_complete_and_noindex(self):
        with tempfile.TemporaryDirectory() as d:
            build(Path(d))
            result=check_site(d)
            self.assertFalse(result['public'])
            self.assertGreaterEqual(result['html_pages'],20)

    def test_project_subpath_keeps_links_and_canonicals_intact(self):
        with tempfile.TemporaryDirectory() as d:
            build(Path(d),'https://fixture.github.io/talk2nature',True,'https://github.com/fixture/talk2nature')
            self.assertTrue(check_site(d)['public'])
            self.assertIn('https://fixture.github.io/talk2nature/research/',(Path(d)/'sitemap.xml').read_text())

    def test_public_build_requires_real_origin(self):
        with tempfile.TemporaryDirectory() as d:
            for origin in ('','http://localhost:4173','https://example.com','https://good.test/?a=b','https://user:secret@good.test'):
                with self.subTest(origin=origin),self.assertRaises(ValueError): build(Path(d),origin,True)

    def test_checker_catches_missing_asset_and_accidental_private_file(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); build(root)
            (root/'assets/mark.svg').unlink()
            with self.assertRaisesRegex(ValueError,'broken link'): check_site(root)
            build(root)
            (root/'AGENTS.md').write_text('private instructions')
            with self.assertRaisesRegex(ValueError,'Unexpected'): check_site(root)

    def test_notes_cite_existing_sources_and_show_review_limits(self):
        source_ids={s['id'] for s in load('sources')}
        for note in load('research'):
            with self.subTest(note=note['slug']):
                self.assertTrue(set(note['source_ids']) <= source_ids)
                for field in ('limitations','review_depth','review_stage','reviewed','expert_review','next_review','year_label'):
                    self.assertTrue(note[field])
                if note['review_stage']=='Methods reviewed':
                    self.assertTrue(note['study_snapshot'])
                    self.assertTrue(note['review_locator'])


if __name__=='__main__': unittest.main()
