import json
import tempfile
import unittest
from pathlib import Path
from urllib.parse import urlsplit
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

    def test_bat_dataset_review_is_a_discoverable_source_linked_page(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/fixture/talk2nature')
            self.assertTrue(check_site(root)['public'])
            note=root/'research/egyptian-fruit-bat-data/index.html'
            html=note.read_text()
            self.assertIn('Fruit-bat calls and context',html)
            self.assertIn('Prat et al. 2017',html)
            self.assertIn('Mendeley Data version 3',html)
            self.assertIn('official version 1/2 and 2/3 comparisons',html)
            self.assertIn('https://data.mendeley.com/datasets/compare/mjfv43zgtv?old=2&amp;new=3',html)
            self.assertIn('Mendeley Data version 1/2 comparison',html)
            self.assertIn('https://data.mendeley.com/datasets/compare/mjfv43zgtv?new=2&amp;old=1',html)
            self.assertIn('version 1 contained metadata only',html)
            self.assertIn('https://data.mendeley.com/api/docs/',html)
            self.assertIn('held-out-animal',html)
            self.assertIn('index,follow',html)
            self.assertIn('https://fixture.github.io/talk2nature/research/egyptian-fruit-bat-data/',html)
            self.assertIn('https://fixture.github.io/talk2nature/research/egyptian-fruit-bat-data/',(root/'sitemap.xml').read_text())

    def test_meerkat_review_exposes_final_evidence_component_rights_and_canonical(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/fixture/talk2nature')
            self.assertTrue(check_site(root)['public'])
            note=root/'research/animal2vec-meerkat/index.html'
            html=note.read_text()
            self.assertIn('animal2vec and MeerKAT',html)
            self.assertIn('Methods in Ecology and Evolution',html)
            self.assertIn('CC BY-NC 4.0',html)
            self.assertIn('MIT',html)
            self.assertIn('receiver comprehension',html)
            self.assertIn('index,follow',html)
            self.assertIn('https://fixture.github.io/talk2nature/research/animal2vec-meerkat/',html)
            self.assertIn('https://fixture.github.io/talk2nature/research/animal2vec-meerkat/',(root/'sitemap.xml').read_text())

    def test_public_sitemap_does_not_claim_unverified_page_modification_dates(self):
        with tempfile.TemporaryDirectory() as d:
            build(Path(d),'https://fixture.github.io/talk2nature',True,'https://github.com/fixture/talk2nature')
            sitemap=(Path(d)/'sitemap.xml').read_text()
            self.assertNotIn('<lastmod>',sitemap)
            self.assertGreater(sitemap.count('<loc>'),20)

    def test_public_sitemap_rejects_urls_without_a_matching_canonical_page(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/fixture/talk2nature')
            sitemap=root/'sitemap.xml'
            content=sitemap.read_text()
            content=content.replace('<loc>https://fixture.github.io/talk2nature/</loc>','<loc>https://fixture.github.io/talk2nature/missing/</loc>',1)
            sitemap.write_text(content)
            with self.assertRaisesRegex(ValueError,'Sitemap URLs do not match canonical public HTML pages'):
                check_site(root)

    def test_audacity_handoff_lab_is_mobile_site_content_with_bounded_claims(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/fixture/talk2nature')
            self.assertTrue(check_site(root)['public'])
            lab=(root/'tools/interop/index.html').read_text()
            tools=(root/'tools/index.html').read_text()
            listen=(root/'tools/listen/index.html').read_text()
            self.assertIn('A FIVE-MINUTE FORMAT CHECK',lab)
            self.assertIn('Try an example',lab)
            self.assertIn('1–2 s',lab)
            self.assertIn('4–5 s',lab)
            self.assertIn('Audacity 4.0.1',lab)
            self.assertIn('does not validate detection accuracy',lab)
            self.assertIn('/talk2nature/tools/interop/',tools)
            self.assertIn('/talk2nature/tools/interop/',listen)
            self.assertIn('audacity-compatibility.yml',lab)
            self.assertTrue((root/'assets/interop.css').is_file())

    def test_community_invites_bounded_university_evaluation(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/fixture/talk2nature')
            self.assertTrue(check_site(root)['public'])
            community=(root/'community/index.html').read_text()
            university=(root/'community/university/index.html').read_text()
            self.assertIn('Universities: start with a small evaluation',community)
            self.assertIn('/talk2nature/community/university/',community)
            self.assertIn('No animal recordings, lab data, endorsement or partnership are requested.',community)
            self.assertIn('has not validated ultrasonic or synchronized audio-video workflows',community)
            self.assertIn('One small test.',university)
            self.assertIn('no animal recording',university)
            self.assertIn('No Talk2Nature animal-communication model',university)
            self.assertIn('without permission',university)
            self.assertIn('href="#evaluation-boundary"',university)
            self.assertIn('id="evaluation-boundary"',university)
            self.assertNotIn('blob/main/docs/UNIVERSITY_EVALUATION.md',university)
            self.assertTrue((root/'assets/university.css').is_file())
            project_root=Path(__file__).resolve().parents[1]
            brief=(project_root/'docs/UNIVERSITY_EVALUATION.md').read_text()
            self.assertIn('not a partnership announcement',brief)
            self.assertIn('not an ethics determination',brief)
            self.assertIn('SUPPORT.md', (project_root/'README.md').read_text())

    def test_public_build_requires_real_origin(self):
        with tempfile.TemporaryDirectory() as d:
            for origin in ('','http://localhost:4173','https://example.com','https://good.test/?a=b','https://user:secret@good.test'):
                with self.subTest(origin=origin),self.assertRaises(ValueError): build(Path(d),origin,True)

    def test_funding_deadlines_show_fresh_check_and_official_cutoff_source(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True)
            self.assertTrue(check_site(root)['public'])
            page=(root/'opportunities/index.html').read_text()
            self.assertEqual(sum(source['id']==121 for source in load('sources')),1)
            self.assertIn('Deadline 2026-10-08 · 12:00',page)
            self.assertIn('official date details',page)
            self.assertIn('Checked 2026-10-11 · Not submitted; not recommended for current scope',page)
            self.assertIn('No company or investor facts are confirmed',page)
            self.assertIn('Deadline 2026-11-09 · 12:00 Israel time',page)
            self.assertIn('Deadline 2026-11-03 · 12:00 CET',page)
            self.assertIn('explicitly excludes AI-related projects',page)
            self.assertIn('software supply-chain datasets',page)
            for source_id in (150,151,152,154,155):
                self.assertEqual(sum(source['id']==source_id for source in load('sources')),1)

    def test_mobile_manifest_icons_and_worker_stay_in_the_public_app_boundary(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); build(root,'https://fixture.github.io/talk2nature',True)
            manifest=json.loads((root/'app/manifest.webmanifest').read_text())
            self.assertEqual(manifest['scope'],'/talk2nature/app/')
            self.assertEqual(manifest['start_url'],manifest['scope'])
            self.assertEqual(manifest['display'],'standalone')
            for icon in manifest['icons']:
                self.assertTrue((root/icon['src'].removeprefix('/talk2nature/')).read_bytes().startswith(b'\x89PNG'))
            source=(root/'app/sw.js').read_text()
            assets=json.loads(source.split('const ASSETS = ',1)[1].split(';',1)[0])
            self.assertNotIn('/talk2nature/about/',assets)
            self.assertIn('/talk2nature/app/compare/',assets)
            self.assertTrue(any('/assets/session-import.mjs?' in a for a in assets))
            self.assertTrue(any('/assets/audacity-export.mjs?' in a for a in assets))
            for asset in assets:
                self.assertTrue(asset.startswith(('/talk2nature/app/','/talk2nature/assets/')))
                path=root/urlsplit(asset).path.removeprefix('/talk2nature/')
                self.assertTrue((path/'index.html' if asset.endswith('/') else path).is_file())
            self.assertNotIn('__REVISION__',source)
            self.assertIn('class="app-body"',(root/'app/index.html').read_text())

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

    def test_learning_paths_have_actionable_reviewable_dependencies(self):
        notes={n['slug']:n for n in load('research')}
        paths=load('learning-paths')['paths']
        self.assertEqual(len({p['id'] for p in paths}),len(paths))
        for path in paths:
            self.assertTrue(set(path['notes']) <= notes.keys())
            for field in ('question','decision','next_step','gate'):
                self.assertTrue(path[field])
        for note in notes.values():
            self.assertIn(note['purpose'],('Models & evaluation','Data & annotation','Behavior & communication','Plants & fungi','Animal-computer interaction','Vocal development'))
            if 'reuse' in note:
                for field in ('status','asset','rights','experiment'):
                    self.assertTrue(note['reuse'][field])
        with tempfile.TemporaryDirectory() as d:
            build(Path(d))
            self.assertTrue(check_site(d))
            page=(Path(d)/'research/starting-points/index.html').read_text()
            for path in paths:
                for slug in path['notes']:
                    self.assertIn(f'/research/{slug}/',page)

    def test_video_sources_have_identity_context_fallbacks_and_no_initial_embeds(self):
        from html import escape
        sources=load('sources')
        videos=[s for s in sources if 'media' in s]
        self.assertEqual(len({s['url'] for s in videos}),len(videos))
        with tempfile.TemporaryDirectory() as d:
            build(Path(d))
            page=(Path(d)/'watch/index.html').read_text()
            self.assertNotIn('<iframe',page)
            self.assertNotIn('i.ytimg.com',page)
            for video in videos:
                m=video['media']
                self.assertTrue(m['review_depth'])
                self.assertTrue(m['creator'])
                self.assertIn(escape(video['url'],quote=True),page)
                self.assertIn(escape(m['creator'],quote=True),page)
                if m['provider']=='youtube':
                    self.assertRegex(m['video_id'],r'^[A-Za-z0-9_-]{11}$')
                    self.assertEqual(video['url'],'https://www.youtube.com/watch?v='+m['video_id'])


if __name__=='__main__': unittest.main()
