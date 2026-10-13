import html
import json
import re
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
from web.build import build, load
from scripts.check_site import check_site


class SearchDescriptionParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.description=''

    def handle_starttag(self, tag, attrs):
        values=dict(attrs)
        if tag=='meta' and values.get('name')=='description':
            self.description=values.get('content','')


class SiteTests(unittest.TestCase):
    def test_contributor_first_steps_link_to_existing_issue_forms(self):
        project_root=Path(__file__).resolve().parents[1]
        guide=(project_root/'CONTRIBUTING.md').read_text()
        form_links={filename:label for label,filename in re.findall(
            r'\[([^\]]+)\]\(https://github\.com/Metivity/talk2nature/issues/new\?template=([A-Za-z0-9_.-]+)\)',
            guide,
        )}
        expected={
            'mobile-check.yml':'mobile-check form',
            'reproduction.yml':'reproduction form',
            'research-source.yml':'source-review form',
            'scientific-review.yml':'scientific review form',
        }
        self.assertEqual(form_links,expected)
        for filename in expected:
            with self.subTest(template=filename):
                self.assertTrue((project_root/'.github'/'ISSUE_TEMPLATE'/filename).is_file())

    def test_reproduction_form_defaults_to_unverified_and_defines_counting_boundary(self):
        project_root=Path(__file__).resolve().parents[1]
        form=(project_root/'.github'/'ISSUE_TEMPLATE'/'reproduction.yml').read_text()
        guide=(project_root/'CONTRIBUTING.md').read_text()
        unverified='- Not sure / not independently verified'
        independent='- Independent evaluator (no project or maintainer assistance)'
        self.assertLess(form.index(unverified),form.index(independent))
        self.assertIn('maintainers review reports',form)
        self.assertIn('only a maintainer-reviewed run of the documented software commands counts toward independent reproduction',guide)

    def test_bat_methods_review_is_visible_and_preserves_evidence_boundaries(self):
        project_root=Path(__file__).resolve().parents[1]
        note=next(n for n in load('research') if n['slug']=='fruit-bat-context-ml-2024')
        self.assertEqual(len(note['review_request']['questions']),4)
        guide=(project_root/'docs'/'BAT_CONTEXT_REVIEW.md').read_text()
        self.assertIn('The exact paper partitions',guide)
        self.assertIn("not the paper's filtered 35,074-call subset",guide)
        self.assertIn('No independent specialist review has been received',guide)
        with tempfile.TemporaryDirectory() as d:
            build(Path(d),'https://fixture.github.io/talk2nature',True,'https://github.com/Metivity/talk2nature')
            page=(Path(d)/'research'/'fruit-bat-context-ml-2024'/'index.html').read_text()
            self.assertIn('OPEN METHODS QUESTION',page)
            self.assertIn('Submit a public methods review',page)
            self.assertIn('No independent specialist review has been received',page)
            self.assertIn('https://github.com/Metivity/talk2nature/blob/main/docs/BAT_CONTEXT_REVIEW.md',page)
            self.assertIn('scientific-review.yml',page)

    def test_local_preview_is_complete_and_noindex(self):
        with tempfile.TemporaryDirectory() as d:
            build(Path(d))
            result=check_site(d)
            self.assertFalse(result['public'])
            self.assertGreaterEqual(result['html_pages'],20)

    def test_project_subpath_keeps_links_and_canonicals_intact(self):
        with tempfile.TemporaryDirectory() as d:
            build(Path(d),'https://fixture.github.io/talk2nature',True,'https://github.com/fixture/talk2nature')
            result=check_site(d)
            self.assertTrue(result['public'])
            self.assertEqual(result['reachable_public_pages'],result['html_pages']-1)
            self.assertIn('https://fixture.github.io/talk2nature/research/',(Path(d)/'sitemap.xml').read_text())

    def test_public_html_page_must_be_discoverable_from_homepage(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/fixture/talk2nature')
            target=root/'research/atlas/index.html'
            target_path=target.resolve()
            public_prefix='/talk2nature/research/atlas/'
            absolute='https://fixture.github.io/talk2nature/research/atlas/'
            for page in root.rglob('*.html'):
                if page.resolve()==target_path:
                    continue
                content=page.read_text().replace(f'href="{public_prefix}"','href="#"')
                content=content.replace(f'href="{absolute}"','href="#"')
                page.write_text(content)
            with self.assertRaisesRegex(ValueError,'Public page is not reachable from homepage: research/atlas/index.html'):
                check_site(root)

    def test_public_robots_names_the_exact_sitemap_url(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/fixture/talk2nature')
            robots=root/'robots.txt'
            self.assertIn('Sitemap: https://fixture.github.io/talk2nature/sitemap.xml',robots.read_text().splitlines())
            robots.write_text('User-agent: *\nAllow: /\nSitemap: https://fixture.github.io/sitemap.xml\n')
            with self.assertRaisesRegex(ValueError,'Public robots.txt does not name the exact sitemap URL'):
                check_site(root)

    def test_resource_directory_lists_records_and_separates_rights_from_acquisition(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/fixture/talk2nature')
            self.assertTrue(check_site(root)['public'])
            page=(root/'research/resources/index.html').read_text()
            resources=json.loads((Path(__file__).parents[1]/'research/resources.json').read_text())['resources']
            self.assertEqual(page.count('<article class="resource-entry"'),len(resources))
            for resource in resources:
                self.assertIn(html.escape(resource['title']),page)
            self.assertIn('rel="canonical" href="https://fixture.github.io/talk2nature/research/resources/"',page)
            self.assertIn('<meta name="robots" content="index,follow">',page)
            self.assertIn('Conditional; check the license, scope and stated conditions',page)
            self.assertIn('Unresolved; treat as not cleared.',page)
            self.assertIn('Not admitted for this project.',page)
            self.assertIn('Metadata only; no files are included in this public directory.',page)
            self.assertIn('A bounded sample path is approved by the collection rules',page)
            self.assertIn('<span class="resource-status">Metadata only</span>',page)
            self.assertIn('<span class="resource-status">Limited sample route</span>',page)
            self.assertNotIn('metadata_only</span>',page)
            self.assertNotIn('sample_approved</span>',page)
            self.assertIn('not a systematic review or legal clearance',page)
            self.assertIn('version not stated',page)
            self.assertNotIn('data/external/',page)
            self.assertNotIn('"files":',page)
            leakage_resource=next(r for r in resources if r['id']=='animal-audio-identity-site-leakage-audit')
            self.assertIn('workshop paper/write-up is still in progress',leakage_resource['limitations'])
            self.assertIn('bat behavior benchmark',leakage_resource['decision'])
            self.assertIn('linked LICENSE file was not verified',leakage_resource['rights']['license'])
            self.assertIn(html.escape(leakage_resource['limitations']),page)
            self.assertIn(html.escape(leakage_resource['rights']['license']),page)
            autoresearch=next(r for r in resources if r['id']=='karpathy-autoresearch')
            self.assertEqual(autoresearch['source_ids'],[214])
            self.assertEqual(autoresearch['version'],'228791fb499afffb54b46200aca536f79142f117')
            self.assertEqual(autoresearch['acquisition'],'metadata_only')
            self.assertTrue(all(autoresearch['rights'][key]=='unresolved' for key in ('research_use','commercial_use','redistribution')))
            self.assertIn('no LICENSE file',autoresearch['rights']['license'])
            self.assertIn('reproducible research',page)
            self.assertIn(html.escape(autoresearch['rights']['license']),page)
            graph=json.loads((root/'research/map/catalog.json').read_text())
            nodes={node['key']:node for node in graph['nodes']}
            self.assertIn('resource:karpathy-autoresearch',nodes)
            self.assertIn('source:214',nodes)
            self.assertTrue(any(edge['from']==nodes['resource:karpathy-autoresearch']['id']
                                and edge['relation']=='cataloged_from'
                                and edge['to']==nodes['source:214']['id'] for edge in graph['edges']))
            parrot_data=next(r for r in resources if r['id']=='monk-parakeet-annotations')
            self.assertIn('exact identity within the Edmond archives is not verified',parrot_data['rights']['scope'])
            self.assertIn('keep training admission false',parrot_data['decision'])
            self.assertIn(html.escape(parrot_data['rights']['scope']),page)
            self.assertIn(html.escape(parrot_data['limitations']),page)
            research_index=(root/'research/index.html').read_text()
            self.assertIn('/talk2nature/research/resources/',research_index)
            self.assertIn('https://fixture.github.io/talk2nature/research/resources/',(root/'sitemap.xml').read_text())

    def test_parrot_playback_note_separates_receiver_response_from_translation(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/Metivity/talk2nature')
            self.assertTrue(check_site(root)['public'])
            note=root/'research/parrot-vocal-imitation-addressing-2012/index.html'
            page=note.read_text()
            self.assertIn('36 temporarily captive wild conures from 27 flocks',page)
            self.assertIn('44 of 72 trial periods',page)
            self.assertIn('Animal Behaviour Society guidelines',page)
            self.assertIn('not decoding of sentence meaning',page)
            self.assertIn('index,follow',page)
            self.assertIn('https://fixture.github.io/talk2nature/research/parrot-vocal-imitation-addressing-2012/',page)
            self.assertIn('https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0049747',page)
            reading=(root/'research/starting-points/index.html').read_text()
            self.assertIn('/research/parrot-vocal-imitation-addressing-2012/',reading)
            atlas=json.loads((root/'research/atlas/catalog.json').read_text())
            mapped=next(r for r in atlas['records'] if r['id']=='parrot-vocal-imitation-addressing-2012')
            self.assertEqual(mapped['locations'][0]['place_id'],'costa-rica')
            self.assertEqual(mapped['observation_period']['start_year'],2007)

    def test_all_pages_have_unique_concise_search_descriptions(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root)
            descriptions=[]
            for path in root.rglob('index.html'):
                parser=SearchDescriptionParser()
                parser.feed(path.read_text())
                self.assertTrue(parser.description.strip(),path)
                self.assertLessEqual(len(parser.description),160,path)
                descriptions.append(parser.description)
            self.assertGreaterEqual(len(descriptions),60)
            self.assertEqual(len(descriptions),len(set(descriptions)))

    def test_research_page_structured_data_matches_visible_sources_and_review_date(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/fixture/talk2nature')
            slug='tree-fungal-networks-evidence'
            note=next(n for n in load('research') if n['slug']==slug)
            sources={s['id']:s for s in load('sources')}
            page=(root/'research'/slug/'index.html').read_text()
            raw=re.search(r'<script type="application/ld\+json">(.*?)</script>',page).group(1)
            structured=json.loads(raw)
            self.assertEqual(structured['@type'],'WebPage')
            self.assertEqual(structured['about'],{'@type':'Thing','name':note['taxon']})
            self.assertEqual(structured['lastReviewed'],note['reviewed'])
            citations=structured['citation']
            self.assertEqual([item['url'] for item in citations],[sources[i]['url'] for i in note['source_ids']])
            for source_id in note['source_ids']:
                self.assertIn(sources[source_id]['url'],page)

    def test_bat_dataset_review_is_a_discoverable_source_linked_page(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/fixture/talk2nature')
            self.assertTrue(check_site(root)['public'])
            note=root/'research/egyptian-fruit-bat-data/index.html'
            html=note.read_text()
            description=re.search(r'<meta name="description" content="([^"]*)">',html).group(1)
            self.assertLessEqual(len(description),160)
            self.assertIn('Animal/session splits remain unverified.',description)
            self.assertIn('Fruit-bat calls and context',html)
            self.assertIn('Prat et al. 2017',html)
            self.assertIn('Mendeley Data version 3',html)
            self.assertIn('official version 1/2 and 2/3 comparisons',html)
            self.assertIn('https://data.mendeley.com/datasets/compare/mjfv43zgtv?old=2&amp;new=3',html)
            self.assertIn('Mendeley Data version 1/2 comparison',html)
            self.assertIn('https://data.mendeley.com/datasets/compare/mjfv43zgtv?new=2&amp;old=1',html)
            self.assertIn('version 1 contained metadata only',html)
            self.assertIn('https://data.mendeley.com/api/docs/',html)
            self.assertIn('Mendeley Data public dataset file-list API documentation',html)
            self.assertIn('HTTP 401',html)
            self.assertIn('Figshare item 4556074 public API metadata',html)
            self.assertIn('https://api.figshare.com/v2/articles/4556074',html)
            self.assertIn('files210.zip',html)
            self.assertIn('3,049,199,327 bytes',html)
            self.assertIn('Egyptian fruit bat annotation table, Figshare item 4555903 metadata',html)
            self.assertIn('https://api.figshare.com/v2/articles/4555903',html)
            self.assertIn('3,286,405 bytes',html)
            self.assertIn('FileInfo.csv',html)
            self.assertIn('https://api.figshare.com/v2/articles/4555897',html)
            self.assertIn('Metadata.pdf',html)
            self.assertIn('https://api.figshare.com/v2/articles/4555900',html)
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

    def test_companion_parrot_name_use_note_is_indexable_and_preserves_correction(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/fixture/talk2nature')
            self.assertTrue(check_site(root)['public'])
            note=root/'research/companion-parrot-name-use-2026/index.html'
            html=note.read_text()
            self.assertIn('When companion parrots use names',html)
            self.assertIn('1,202 companion parrots across 89 species',html)
            self.assertIn('802 example phrases',html)
            self.assertIn('Results section says 801',html)
            self.assertIn('correction adds ORCID identifiers only',html)
            self.assertIn('respondent and parrot names',html)
            self.assertIn('describes its S2 phrase dataset as de-identified',html)
            self.assertIn('index,follow',html)
            self.assertIn('https://fixture.github.io/talk2nature/research/companion-parrot-name-use-2026/',html)
            self.assertIn('https://doi.org/10.1371/journal.pone.0349699',html)
            self.assertIn('https://fixture.github.io/talk2nature/research/companion-parrot-name-use-2026/',(root/'sitemap.xml').read_text())
            first_animal=(root/'research/first-animal/index.html').read_text()
            self.assertIn('2026 companion-parrot survey',first_animal)
            reading_path=(root/'research/starting-points/index.html').read_text()
            self.assertIn('/research/companion-parrot-name-use-2026/',reading_path)

    def test_animal_name_criteria_review_is_abstract_limited_and_discoverable(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/Metivity/talk2nature')
            self.assertTrue(check_site(root)['public'])
            page=(root/'research/animal-name-criteria-2026/index.html').read_text()
            self.assertIn('Do animal calls function as names?',page)
            self.assertIn('individual reference',page)
            self.assertIn('symbolic representation',page)
            self.assertIn('shared meaning',page)
            self.assertIn('spectacled parrotlets',page)
            self.assertIn('Abstract and publisher-highlights review',page)
            self.assertIn('not a new experiment or an ML result',page)
            self.assertIn('has not received independent review',page)
            self.assertIn('Creative Commons license',page)
            self.assertIn('much of the presented evidence is equivocal',page)
            self.assertIn('The PubMed abstract and ScienceDirect publisher highlights/metadata were available',page)
            self.assertIn('all rights reserved',page)
            self.assertIn('https://pubmed.ncbi.nlm.nih.gov/42486753/',page)
            self.assertIn('https://doi.org/10.1016/j.tics.2026.06.008',page)
            canonical='https://fixture.github.io/talk2nature/research/animal-name-criteria-2026/'
            self.assertIn(canonical,page)
            self.assertIn(canonical,(root/'sitemap.xml').read_text())
            resource=next(r for r in json.loads((Path(__file__).parents[1]/'research/resources.json').read_text())['resources'] if r['id']=='animal-name-criteria-2026')
            self.assertEqual(resource['acquisition'],'metadata_only')
            self.assertEqual(resource['source_ids'],[180])
            path=(root/'research/starting-points/index.html').read_text()
            self.assertIn('/research/animal-name-criteria-2026/',path)
            self.assertIn('/research/companion-parrot-name-use-2026/',path)
            self.assertIn('natural conspecific signals proposed as names',path)
            self.assertIn('A caregiver report about a human-created name differs',path)

    def test_animal_spot_note_distinguishes_recording_holdout_from_animal_holdout(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            base='https://fixture.github.io/talk2nature'
            build(root,base,True,'https://github.com/Metivity/talk2nature')
            self.assertTrue(check_site(root)['public'])
            page=root/'research'/'animal-spot-parrot-detection-2022'/'index.html'
            rendered=page.read_text()
            self.assertIn('samples from a recording stay within one split',rendered)
            self.assertIn('does not establish individual-animal holdout',rendered)
            self.assertIn('70/15/15 train/validation/test split',rendered)
            self.assertIn('97.9%',rendered)
            self.assertIn('95.9%',rendered)
            self.assertIn('animal-held-out claim',rendered)
            self.assertIn('index,follow',rendered)
            canonical=base+'/research/animal-spot-parrot-detection-2022/'
            self.assertIn(canonical,rendered)
            self.assertIn(canonical,(root/'sitemap.xml').read_text())

    def test_dupont_lark_note_is_discoverable_and_keeps_data_rights_separate(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/Metivity/talk2nature')
            self.assertTrue(check_site(root)['public'])
            page=(root/'research/duponts-lark-vocal-types-2026/index.html').read_text()
            self.assertIn("Dupont's lark songs and calls",page)
            self.assertIn('4,297 annotated songs from 191 singing males',page)
            self.assertIn('795 calls from 97 calling males',page)
            self.assertIn('not independently observed behaviors',page)
            self.assertIn('CC BY-NC-ND 4.0',page)
            self.assertIn('Datos.gob.es declares CC BY 4.0 for the specific CSIC archive and README distributions',page)
            self.assertIn('3,711,242,291 bytes',page)
            self.assertIn('concept DOI 17264916, which Zenodo redirects to version DOI 17264917',page)
            self.assertIn('Digital.CSIC README and distribution headers for the Dupont',page)
            self.assertIn('separate Zenodo R script',page)
            self.assertIn('17264916',page)
            self.assertIn('17264917',page)
            canonical='https://fixture.github.io/talk2nature/research/duponts-lark-vocal-types-2026/'
            self.assertIn(canonical,page)
            self.assertIn(canonical,(root/'sitemap.xml').read_text())
            record=json.loads((root/'research/atlas/catalog.json').read_text())
            lark=next(r for r in record['records'] if r['id']=='duponts-lark-vocal-types-2026')
            self.assertEqual(lark['place_labels'],['Spain · 20 study populations (country-level locator)'])
            self.assertIn('no individual site pins are shown',lark['location_note'])
            path=(root/'research/starting-points/index.html').read_text()
            self.assertIn('/research/duponts-lark-vocal-types-2026/',path)

    def test_great_green_macaw_note_preserves_evidence_rights_and_map_precision(self):
        note=next(n for n in load('research') if n['slug']=='great-green-macaw-vocal-development-2026')
        resources={r['id']:r for r in json.loads((Path(__file__).parents[1]/'research/resources.json').read_text())['resources']}
        paper=resources['great-green-macaw-vocal-development-paper-2026']
        data=resources['great-green-macaw-vocal-development-data-2026']
        code=resources['great-green-macaw-vocal-development-code-2026']
        self.assertEqual(set(note['source_ids']),{215,216,217})
        for resource in (paper,data,code):
            self.assertEqual(resource['acquisition'],'metadata_only')
            self.assertEqual(resource['files'],[])
        self.assertEqual(paper['rights']['license'],'Not established in this review.')
        self.assertIn('CC0',data['rights']['license'])
        self.assertIn('Dryad policy',code['rights']['license'])
        self.assertEqual(code['rights']['research_use'],'conditional')
        self.assertIn('RDS objects combine selected calls',note['limitations'])
        self.assertIn('whether audio samples are embedded or referenced',note['limitations'])
        self.assertIn('not a demonstrated call meaning',note['finding'])
        self.assertEqual([place['place_id'] for place in note['atlas']['locations']],['costa-rica'])
        self.assertIn('country-level',note['atlas']['location_note'])
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/Metivity/talk2nature')
            self.assertTrue(check_site(root)['public'])
            page=(root/'research/great-green-macaw-vocal-development-2026/index.html').read_text()
            self.assertIn('Macaw calls change with age and population',page)
            self.assertIn('not a demonstrated call meaning',page)
            self.assertIn('whether audio samples are embedded or referenced',page)
            canonical='https://fixture.github.io/talk2nature/research/great-green-macaw-vocal-development-2026/'
            self.assertIn(canonical,page)
            self.assertIn(canonical,(root/'sitemap.xml').read_text())
            atlas=json.loads((root/'research/atlas/catalog.json').read_text())
            mapped=next(row for row in atlas['records'] if row['id']==note['slug'])
            self.assertEqual(len(mapped['locations']),1)
            self.assertEqual(mapped['locations'][0]['place_id'],'costa-rica')
            path=(root/'research/starting-points/index.html').read_text()
            self.assertIn('/research/great-green-macaw-vocal-development-2026/',path)
            resource_page=(root/'research/resources/index.html').read_text()
            self.assertIn(paper['title'],resource_page)
            self.assertIn(data['title'],resource_page)
            self.assertIn(code['title'],resource_page)

    def test_wild_parrot_duet_study_is_indexable_and_coarsely_mapped(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/fixture/talk2nature')
            self.assertTrue(check_site(root)['public'])
            page=root/'research/wild-parrot-duet-structure-2026/index.html'
            html=page.read_text()
            self.assertIn('Wild parrot duet structure: sequence patterns, not decoded meaning',html)
            self.assertIn('52 high-quality warble duets from 12 pairs',html)
            self.assertIn('19 positive and four negative',html)
            self.assertIn('cannot confidently assign meanings',html)
            self.assertIn('https://doi.org/10.1002/jav.03552',html)
            self.assertIn('https://datadryad.org/dataset/doi:10.5061/dryad.rn8pk0prb',html)
            self.assertIn('https://datadryad.org/help/guides/reuse',html)
            self.assertIn('specific article reuse license was not established',html)
            self.assertIn('index,follow',html)
            self.assertIn('https://fixture.github.io/talk2nature/research/wild-parrot-duet-structure-2026/',html)
            self.assertNotIn('Ahogados',html)
            self.assertIn('https://fixture.github.io/talk2nature/research/wild-parrot-duet-structure-2026/',(root/'sitemap.xml').read_text())

    def test_fungal_electrophysiology_note_is_discoverable_without_language_claims(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); build(root,'https://fixture.github.io/talk2nature',True)
            page=root/'research/fungal-electrophysiology-stimuli-2025/index.html'
            html=page.read_text()
            self.assertIn('Fungal electrical activity: a sensor study, not a decoded language',html)
            self.assertIn('significant 1,604% power-spectral-density increase',html)
            self.assertIn('not significant',html)
            self.assertIn('DMSO',html)
            self.assertIn('Method S1',html)
            self.assertIn('CC BY 4.0',html)
            self.assertIn('semantic code',html)
            self.assertIn('content="index,follow"',html)
            self.assertIn('https://fixture.github.io/talk2nature/research/fungal-electrophysiology-stimuli-2025/',html)
            self.assertIn('https://doi.org/10.1016/j.isci.2025.113484',html)
            self.assertIn('https://doi.org/10.17632/srkxbkh6sp.1',html)
            self.assertIn('https://fixture.github.io/talk2nature/research/fungal-electrophysiology-stimuli-2025/',(root/'sitemap.xml').read_text())
            reading_path=(root/'research/starting-points/index.html').read_text()
            self.assertIn('/research/fungal-electrophysiology-stimuli-2025/',reading_path)
            atlas=json.loads((root/'research/atlas/catalog.json').read_text())
            record=next(r for r in atlas['records'] if r['id']=='wild-parrot-duet-structure-2026')
            self.assertEqual(record['locations'][0]['place_id'],'costa-rica')
            place=next(p for p in atlas['places'] if p['id']=='costa-rica')
            self.assertEqual(place['precision'],'country')
            first_animal=(root/'research/first-animal/index.html').read_text()
            self.assertIn('/research/wild-parrot-duet-structure-2026/',first_animal)
            reading_path=(root/'research/starting-points/index.html').read_text()
            self.assertIn('/research/wild-parrot-duet-structure-2026/',reading_path)

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
            self.assertIn('A browser-only review of invented observation sessions',university)
            self.assertIn('no animal recording',university)
            self.assertIn('href="/talk2nature/app/compare/"',university)
            self.assertIn('href="/talk2nature/tools/interop/"',university)
            self.assertIn('Start the browser review',university)
            self.assertIn('Optional: test the Audacity handoff',university)
            self.assertIn('Neither tests what an animal means',university)
            self.assertIn('No Talk2Nature animal-communication model',university)
            self.assertIn('without permission',university)
            self.assertIn('id="evaluation-boundary"',university)
            self.assertNotIn('blob/main/docs/UNIVERSITY_EVALUATION.md',university)
            self.assertTrue((root/'assets/university.css').is_file())
            project_root=Path(__file__).resolve().parents[1]
            brief=(project_root/'docs/UNIVERSITY_EVALUATION.md').read_text()
            self.assertIn('not a partnership announcement',brief)
            self.assertIn('not an ethics determination',brief)
            self.assertIn('browser-only comparison of two invented observation sessions',brief)
            self.assertIn('https://metivity.github.io/talk2nature/app/compare/',brief)
            self.assertIn('optional, deeper Listen-to-Audacity check',brief)
            self.assertNotIn('try a short synthetic Listen-to-Audacity workflow',brief)
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
            self.assertIn('Official track rules ↗',page)
            self.assertIn('Official open-source procedure ↗',page)
            self.assertIn('https://innovationisrael.org.il/wp-content/uploads/2024/06/%D7%9E%D7%A1%D7%9C%D7%95%D7%9C-%D7%94%D7%98%D7%91%D7%94-%D7%9E%D7%A1-7-%D7%A7%D7%A8%D7%9F-%D7%94%D7%94%D7%96%D7%A0%D7%A7-15.07.2026.pdf',page)
            self.assertIn('https://innovationisrael.org.il/rules/%D7%A0%D7%95%D7%94%D7%9C-%D7%A7%D7%95%D7%93-%D7%A4%D7%AA%D7%95%D7%97/',page)
            self.assertIn('Deadline 2026-11-03 · 12:00 CET',page)
            self.assertIn('explicitly excludes AI-related projects',page)
            self.assertIn('software supply-chain datasets',page)
            for source_id in (150,151,152,154,155,158,159):
                self.assertEqual(sum(source['id']==source_id for source in load('sources')),1)

    def test_biodivfuture_call_links_rules_and_discloses_deadline_conflict(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/Metivity/talk2nature')
            self.assertTrue(check_site(root)['public'])
            page=(root/'opportunities/index.html').read_text()
            self.assertIn('Biodiversa+ · BiodivFuture 2026–2027',page)
            self.assertIn('Deadline 2026-11-10 · 12:00 CET · 11:00 UTC',page)
            self.assertIn('The Biodiversa+ call page and formal PDF give November 10; the Commission portal lists November 2',page)
            self.assertIn('National funding rules ↗',page)
            self.assertIn('Call partner search ↗',page)
            self.assertIn('Other official listing (date differs) ↗',page)
            self.assertIn('ISF-recognized Israeli research institution',page)
            self.assertIn('No application is prepared',page)
            for source_id in (181,182,183,184,185):
                self.assertEqual(sum(source['id']==source_id for source in load('sources')),1)

    def test_horizon_biodiversity_monitoring_call_states_policy_fit_and_consortium_gates(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True)
            page=(root/'opportunities/index.html').read_text()
            self.assertIn('Horizon Europe · HORIZON-NATURE-2027-02-05: Cost-effective biodiversity monitoring',page)
            self.assertIn('HORIZON-NATURE-2027-02-05',page)
            self.assertIn('Deadline 2027-01-14 · 17:00 Brussels time',page)
            self.assertIn('€16 million topic budget',page)
            self.assertIn('€5–6 million per project for three projects',page)
            self.assertIn('pollinator monitoring under the Nature Restoration Regulation',page)
            self.assertIn('soil biodiversity under the Soil Monitoring Law',page)
            self.assertIn('Water Framework Directive',page)
            self.assertIn('no validated species-identification or counting capability',page)
            self.assertIn('not a stand-alone animal-communication or general software grant',page)
            self.assertIn('Official topic details ↗',page)
            self.assertIn('Applicant eligibility ↗',page)
            for source_id in (201,202,203):
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
            self.assertIn('/talk2nature/app/practice/',assets)
            self.assertIn('/talk2nature/app/check/',assets)
            self.assertTrue(any('/assets/session-import.mjs?' in a for a in assets))
            self.assertTrue(any('/assets/audacity-export.mjs?' in a for a in assets))
            self.assertTrue(any('/assets/aoef-export.mjs?' in a for a in assets))
            self.assertTrue(any('/assets/practice.js?' in a for a in assets))
            self.assertTrue(any('/assets/practice-model.mjs?' in a for a in assets))
            for name in ('device-check.css','device-check.js','device-check-model.mjs'):
                self.assertTrue(any('/assets/'+name+'?' in a for a in assets))
            for asset in assets:
                self.assertTrue(asset.startswith(('/talk2nature/app/','/talk2nature/assets/')))
                path=root/urlsplit(asset).path.removeprefix('/talk2nature/')
                self.assertTrue((path/'index.html' if asset.endswith('/') else path).is_file())
            self.assertNotIn('__REVISION__',source)
            self.assertIn('class="app-body"',(root/'app/index.html').read_text())

    def test_android_source_preview_is_discoverable_and_not_claimed_as_a_release(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); build(root,'https://fixture.github.io/talk2nature',True)
            mobile=(root/'mobile/index.html').read_text()
            station=(root/'tools/station/index.html').read_text()
            source_url='https://github.com/Metivity/talk2nature/tree/main/native-android'
            self.assertIn('experimental Android Station source preview',mobile)
            self.assertIn('there is no signed APK or store release',mobile)
            self.assertIn('physical-phone and field validation are still open',mobile)
            self.assertIn(source_url,mobile)
            self.assertIn('Android source preview',station)
            self.assertIn('1-, 4- and 8-hour limits',station)
            self.assertIn('not a signed APK or field-tested release',station)
            self.assertIn(source_url,station)

    def test_phone_rehearsal_is_discoverable_and_truthful_about_temporary_measurements(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/fixture/talk2nature')
            page=(root/'app/check/index.html').read_text()
            home=(root/'app/index.html').read_text()
            station=(root/'app/station/index.html').read_text()
            self.assertIn('https://fixture.github.io/talk2nature/app/check/',page)
            self.assertIn('content="index,follow"',page)
            self.assertIn('away from animals',page)
            self.assertIn('No raw audio, device identifier, result or location is saved or uploaded.',page)
            self.assertIn('not calibrated sound-pressure measurements',page)
            self.assertIn('id="check-permission" type="checkbox"',page)
            self.assertNotIn('id="check-permission" checked',page)
            self.assertIn('id="check-start"',page)
            self.assertIn('id="check-stop"',page)
            self.assertIn('id="check-result" class="device-check-result" hidden',page)
            self.assertNotIn('<audio',page)
            self.assertIn('Check your phone at home.',home)
            self.assertIn('Check your phone at home, away from animals',station)
            self.assertIn('https://fixture.github.io/talk2nature/app/check/',(root/'sitemap.xml').read_text())
            css=(root/'assets/device-check.css').read_text()
            self.assertIn('@media(max-width:700px)',css)
            self.assertIn('position:fixed',css)
            script=(root/'assets/device-check.js').read_text()
            self.assertIn("./station-audio.mjs?v=",script)
            self.assertIn("./device-check-model.mjs?v=",script)
            self.assertIn("./station-capture.mjs?v=",script)
            about=(root/'about/index.html').read_text()
            self.assertIn('temporary aggregate readings, never saves or uploads sound',about)

    def test_field_companion_explains_multi_animal_scope_and_sensor_limits(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True)
            home=(root/'app/index.html').read_text()
            self.assertIn('MORE THAN PARROTS',home)
            self.assertIn('amphibian, reptile, fish, invertebrate',home)
            self.assertIn('or leave it unknown',home)
            self.assertIn('the app does not identify the sound source',home)
            self.assertIn('Plants and fungi need different sensing tools.',home)
            self.assertIn('/talk2nature/app/station/?mode=companion#station-console',home)
            self.assertIn('/talk2nature/research/frontiers/',home)
            css=(root/'assets/app.css').read_text()
            self.assertIn('.animal-range-card{',css)
            self.assertIn('@media(max-width:620px){.animal-range',css)

    def test_companion_explains_temporary_audio_and_notes_before_recording(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True)
            home=(root/'app/index.html').read_text()
            station=(root/'app/station/index.html').read_text()
            guidance='Nothing uploads or auto-saves. Export before closing to keep your audio and notes.'
            self.assertIn(guidance,home)
            self.assertIn(guidance,station)
            self.assertLess(station.index('id="station-retention-guidance"'),station.index('id="station-start"'))
            self.assertIn('aria-describedby="station-retention-guidance"',station)

    def test_recording_stop_bar_leaves_phone_scroll_space_for_observation_notes(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True)
            css=(root/'assets/app.css').read_text()
            self.assertIn(
                '.app-body:has(.station-console:is([data-phase=starting],[data-phase=recording]))'
                '{padding-bottom:calc(112px + env(safe-area-inset-bottom))}',
                css,
            )

    def test_sound_desk_explains_station_zip_review_and_annotation_paths(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True)
            sound_desk=(root/'app/review/index.html').read_text()
            compare=(root/'app/compare/index.html').read_text()
            self.assertIn('href="/talk2nature/app/compare/"',sound_desk)
            self.assertIn('open the original ZIP in Compare',sound_desk)
            self.assertIn('no unzipping needed',sound_desk)
            self.assertIn('Annotate a clip from a saved session',sound_desk)
            self.assertIn('accept=".zip,application/zip"',sound_desk)
            self.assertIn('We check the saved sound hashes',sound_desk)
            self.assertIn('carry a copy of the session journal',sound_desk)
            self.assertIn('accept=".zip,application/zip"',compare)
            self.assertIn('No unzipping needed.',compare)

    def test_observation_practice_is_discoverable_and_declares_its_synthetic_scope(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); build(root,'https://fixture.github.io/talk2nature',True)
            page=(root/'app/practice/index.html').read_text()
            home=(root/'app/index.html').read_text()
            self.assertIn('https://fixture.github.io/talk2nature/app/practice/',page)
            self.assertIn('content="index,follow"',page)
            self.assertIn('three invented scenes',page)
            self.assertIn('No points, no data collection',page)
            self.assertIn('id="practice-title" tabindex="-1"',page)
            self.assertIn('share a note about the wording',page)
            self.assertIn('href="/talk2nature/app/practice/"',home)
            self.assertIn('https://fixture.github.io/talk2nature/app/practice/',(root/'sitemap.xml').read_text())

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

    def test_whombat_aoef_bridge_is_indexable_with_verified_scope_and_limits(self):
        note=next(n for n in load('research') if n['slug']=='whombat-annotation-workbench')
        self.assertEqual(note['source_ids'],[229,230,231,232])
        self.assertIn('imported through Whombat 0.9.0 desktop UI',note['review_stage'])
        self.assertIn('other dependency versions',note['limitations'])
        self.assertIn('independent bioacoustics or research-software specialist',note['next_review'])
        self.assertIn('not a decoder',note['limitations'])
        resources=json.loads((Path(__file__).parents[1]/'research/resources.json').read_text())['resources']
        soundevent=next(r for r in resources if r['id']=='soundevent-aoef-2-10-0')
        self.assertEqual(soundevent['rights']['license'],'MIT')
        self.assertEqual(soundevent['acquisition'],'metadata_only')
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True)
            page=(root/'research/whombat-annotation-workbench/index.html').read_text()
            self.assertIn('content="index,follow"',page)
            self.assertIn('https://fixture.github.io/talk2nature/research/whombat-annotation-workbench/',page)
            self.assertIn('https://mbsantiago.github.io/whombat/user_guide/guides/import/',page)
            self.assertIn('https://pypi.org/project/soundevent/2.10.0/',page)
            self.assertIn('format interoperability only',page)
            self.assertIn('whombat-annotation-workbench/',(root/'sitemap.xml').read_text())
            review=(root/'app/review/index.html').read_text()
            self.assertIn('id="export-aoef"',review)
            self.assertIn('sidecar',review)
            listen=(root/'tools/listen/index.html').read_text()
            self.assertIn('passed a synthetic Whombat 0.9.0 desktop-UI import',listen)
            self.assertIn('scientific suitability remain untested',listen)
            self.assertNotIn('import into the Whombat app itself has not been tested',listen)

    def test_community_bioacoustic_dataset_directory_stays_a_metadata_only_lead(self):
        note=next(n for n in load('research') if n['slug']=='community-bioacoustic-dataset-directory')
        self.assertEqual(note['source_ids'],[239])
        self.assertIn('not a dataset',note['limitations'])
        self.assertIn('primary deposit',note['next_review'])
        resources=json.loads((Path(__file__).parents[1]/'research/resources.json').read_text())['resources']
        resource=next(r for r in resources if r['id']=='bioacoustic-ai-dataset-directory')
        self.assertEqual(resource['version'],'c412c5c3fd65552d17e492dac35f2be2c30349a4; commit dated 2026-05-26')
        self.assertEqual(resource['acquisition'],'metadata_only')
        self.assertTrue(all(resource['rights'][key]=='unresolved' for key in ('research_use','commercial_use','redistribution')))
        self.assertIn('no LICENSE file',resource['rights']['license'])
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/fixture/talk2nature')
            page=(root/'research/community-bioacoustic-dataset-directory/index.html').read_text()
            self.assertIn('rel="canonical" href="https://fixture.github.io/talk2nature/research/community-bioacoustic-dataset-directory/"',page)
            self.assertIn('<meta name="robots" content="index,follow">',page)
            self.assertIn('community-bioacoustic-dataset-directory/',(root/'sitemap.xml').read_text())

    def test_parrot_annotation_note_links_current_edmond_terms(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/fixture/talk2nature')
            note=(root/'research/parrot-data-feasibility/index.html').read_text()
            sources=(root/'sources/index.html').read_text()
            self.assertIn('href="https://www.edmond.mpg.de/Terms_of_Use/"',note)
            self.assertIn('href="https://www.edmond.mpg.de/"',note)
            self.assertIn('id="source-225"',sources)
            self.assertIn('id="source-226"',sources)
            self.assertIn('fileAccessRequest flag does not resolve any individual file',note)

    def test_parrot_video_interface_note_preserves_reporting_and_rights_gates(self):
        note=next(n for n in load('research') if n['slug']=='parrot-video')
        self.assertIn('65 parrot-triggered live calls',note['finding'])
        self.assertIn('Table 3',note['limitations'])
        self.assertIn('P3 and P5',note['limitations'])
        self.assertIn('caregiver then placed the call',dict(note['study_snapshot'])['Interface'])
        resources=json.loads((Path(__file__).parents[1]/'research/resources.json').read_text())['resources']
        resource=next(r for r in resources if r['id']=='parrot-live-playback-study-2024')
        self.assertEqual(resource['source_ids'],[49])
        self.assertEqual(resource['acquisition'],'metadata_only')
        self.assertIn('CC BY-NC-ND 4.0',resource['rights']['license'])
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True)
            note_page=(root/'research/parrot-video/index.html').read_text()
            resource_page=(root/'research/resources/index.html').read_text()
            self.assertIn('duration magnitude remains unresolved',note_page)
            self.assertIn('P3 and P5 entries also conflict',note_page)
            self.assertIn('Parrot choice in live and playback video calls',resource_page)
            self.assertIn('No study dataset, code or media were acquired',resource_page)

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
