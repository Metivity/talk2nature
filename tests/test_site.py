Warning: truncated output (original token count: 60841)
Total output lines: 3496

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
    def test_homepage_offers_clear_first_steps(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True)
            home=(root/'index.html').read_text()
        self.assertIn('/talk2nature/app/station/?mode=demo#station-console',home)
        self.assertIn('Try an example · no microphone',home)
        self.assertIn('/talk2nature/community/university/',home)
        self.assertIn('Choose a first contribution',home)

    def test_compare_explains_detection_generalization_and_receiver_evidence(self):
        project_root=Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True)
            page=(root/'app'/'compare'/'index.html').read_text()
        for phrase in (
            'Is a bird sound present?',
            'Detection is not translation.',
            'Does it generalize?',
            'Unmarked time is not automatically a verified quiet example.',
            'What did a receiver do?',
            'Timing alone cannot establish understanding.',
            'It does not run these research analyses or infer animal meaning.',
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase,page)
        for route in (
            '/research/dcase2018-bird-presence-benchmark/',
            '/research/birdset-powdermill-first-compute-candidate/',
            '/research/honeybee-dance-following-2023/',
        ):
            with self.subTest(route=route):
                self.assertIn(f'href="/talk2nature{route}"',page)

    def test_pipeline_comparison_research_is_applied_without_claiming_translation(self):
        project_root=Path(__file__).resolve().parents[1]
        notes=json.loads((project_root/'content'/'research.json').read_text())
        note=next(item for item in notes if item['slug']=='same-data-different-results-bioacoustics-2025')
        self.assertEqual(note['source_ids'],[616,617])
        self.assertIn('known identity classes',note['limitations'])
        self.assertIn('does not test open-set or unseen-caller',note['limitations'])
        self.assertIn('does not justify making it our universal baseline',note['lesson'])
        model_decision=(project_root/'docs'/'MODEL_DATA_DECISION.md').read_text()
        run_card=(project_root/'docs'/'BENCHMARK_CANDIDATE_RUN_CARD.md').read_text()
        self.assertIn('same frozen, question-appropriate split',model_decision)
        self.assertIn('signal-processing/feature/model path',run_card)
        resources=json.loads((project_root/'research'/'resources.json').read_text())['resources']
        deposit=next(item for item in resources if item['id']=='wierucka-bioacoustics-methods-data-code-2025')
        self.assertEqual(deposit['acquisition'],'metadata_only')
        self.assertEqual(deposit['rights']['research_use'],'unresolved')
        with tempfile.TemporaryDirectory() as d:
            output=Path(d)
            build(output,'https://fixture.github.io/talk2nature',True,'https://github.com/Metivity/talk2nature')
            page=(output/'research'/'same-data-different-results-bioacoustics-2025'/'index.html').read_text()
            self.assertIn('name="robots" content="index,follow"',page)
            self.assertIn('https://doi.org/10.1111/2041-210X.70091',page)
            self.assertIn('/research/same-data-different-results-bioacoustics-2025/',(output/'sitemap.xml').read_text())

    def test_passerine_methods_are_applied_without_claiming_full_text_or_meaning(self):
        project_root=Path(__file__).resolve().parents[1]
        notes=json.loads((project_root/'content'/'research.json').read_text())
        note=next(item for item in notes if item.get('slug')=='global-passerine-song-biogeography-2026')
        model_decision=(project_root/'docs'/'MODEL_DATA_DECISION.md').read_text()
        plan=(project_root/'docs'/'FIRST_ANIMAL_PLAN.md').read_text()
        self.assertIn('500 ms modulation-power-spectrum windows',note['review_depth'])
        self.assertIn('HTTP 403',note['review_depth'])
        self.assertIn('not a sound-presence, receiver-response or meaning benchmark',model_decision)
        self.assertIn('Do not continue filename-to-record joins by scraping',plan)

    def test_benchmark_candidate_card_count_and_birdpark_gate_are_consistent(self):
        project_root=Path(__file__).resolve().parents[1]
        card=(project_root/'docs'/'BENCHMARK_CANDIDATE_RUN_CARD.md').read_text()
        candidates=re.findall(r'^## Candidate ([A-G]) —',card,re.M)
        self.assertEqual(candidates,list('ABCDEFG'))
        self.assertIn('This card compares seven distinct research exercises',card)
        self.assertIn('No first communication-adjacent ML benchmark is selected or training-ready.',card)
        birdpark=card.split('## Candidate G —',1)[1].split('## Shared readiness gates',1)[0]
        self.assertIn('2,677 vocalizations in a 28-minute',birdpark)
        self.assertIn('Some microphone-only caller labels were guessed',birdpark)
        self.assertIn('Zenodo v1 and v2 pages display no dataset license',birdpark)
        self.assertIn('not receiver understanding, behavior meaning or communication',birdpark)

    def test_researcher_start_guide_puts_quick_routes_before_verification_history(self):
        project_root=Path(__file__).resolve().parents[1]
        guide=(project_root/'docs'/'RESEARCHER_START.md').read_text()
        history=(project_root/'docs'/'RESEARCHER_START_HISTORY.md').read_text()
        start=guide.index('## Start here')
        browser=guide.index('**Try the browser workflow',start)
        code=guide.index('**Run the research-code example',browser)
        evidence=guide.index('**Current public-main quickstart verification')
        self.assertLess(start,browser)
        self.assertLess(browser,code)
        self.assertLess(code,evidence)
        self.assertIn('b715fe3ce38ee4fb8b35f30e12a38ee482df92fd',guide[evidence:])
        self.assertIn('No microphone, playback or upload is needed',guide[browser:code])
        self.assertIn('## Three useful first contributions',guide)
        self.assertIn('[verification history](RESEARCHER_START_HISTORY.md)',guide)
        self.assertNotIn('## October 24 current public-main clean-clone recheck',guide)
        self.assertIn('## October 24 current public-main clean-clone recheck — c8d4700',history)
        self.assertIn('historical snapshots, not independent reproductions or scientific results',history)

    def test_contributor_first_steps_link_to_existing_issue_forms(self):
        project_root=Path(__file__).resolve().parents[1]
        guide=(project_root/'CONTRIBUTING.md').read_text()
        form_links={filename:label for label,filename in re.findall(
            r'\[([^\]]+)\]\(https://github\.com/Metivity/talk2nature/issues/new\?template=([A-Za-z0-9_.-]+)\)',
            guide,
        )}
        expected={
            'first-use.yml':'short first-use form',
            'mobile-check.yml':'mobile-check form',
            'reproduction.yml':'detailed workflow report form',
            'research-source.yml':'source-review form',
            'scientific-review.yml':'scientific review form',
        }
        self.assertEqual(form_links,expected)
        for filename in expected:
            with self.subTest(template=filename):
                self.assertTrue((project_root/'.github'/'ISSUE_TEMPLATE'/filename).is_file())
        self.assertIn('No first communication-adjacent ML benchmark is selected or training-ready.',guide)
        for path in (
            'docs/BENCHMARK_CANDIDATE_RUN_CARD.md',
            'docs/BAT_CONTEXT_REVIEW.md',
            'docs/ZF_AIM_INDEPENDENT_REVIEW.md',
            'docs/V33DA_SAMPLE_RUN_CARD.md',
        ):
            with self.subTest(review_brief=path):
                self.assertIn(f']({path})',guide)
                self.assertTrue((project_root/path).is_file())
        self.assertIn('not a receiver-response or meaning benchmark',guide)

    def test_contributor_zero_command_steps_match_the_live_app(self):
        project_root=Path(__file__).resolve().parents[1]
        home=(project_root/'web'/'templates'/'app.html').read_text()
        intro=(project_root/'web'/'templates'/'app-station-intro.html').read_text()
        station=(project_root/'web'/'templates'/'station.html').read_text()
        station_script=(project_root/'web'/'assets'/'station.js').read_text()
        compare=(project_root/'web'/'templates'/'compare.html').read_text()
        contributor=(project_root/'CONTRIBUTING.md').read_text()
        self.assertIn('Try an example · no microphone',home)
        self.assertIn('**Finish and review**',contributor)
        self.assertNotIn('**Stop recording**',contributor)
        self.assertIn('Observe without prompting.',intro)
        self.assertIn('Talk2Nature sends no animal-directed sounds or prompts.',intro)
        self.assertIn('capture stops if you leave this page.',intro)
        self.assertIn('Playback is for human review only—never play it to animals;',intro)
        self.assertIn('use headphones or move well away.',intro)
        self.assertIn('You do not need to call, imitate or prompt an animal;',station)
        self.assertIn('no animal calls or prompts.',station)
        self.assertIn('Finish and review',station)
        self.assertIn("'End rehearsal'",station_script)
        live_labels=('Try invented example · no microphone','Mark an observation','Finish and review',
                     'Save this moment','I saved the file',
                     'Open Compare moments to review it','Open a session ZIP')
        for label in live_labels:
            with self.subTest(button=label):
                self.assertIn(label,station if label!='Open a session ZIP' else compare)
        expected_steps=('Try an example · no microphone',
                        'no-microphone practice button','one observation marker',
                        'End rehearsal','Finish and review','invented-session recap')
        for name in ('README.md','CONTRIBUTING.md'):
            with self.subTest(document=name):
                copy=(project_root/name).read_text()
                positions=[copy.index(step) for step in expected_steps]
                self.assertEqual(positions,sorted(positions))
        self.assertIn('Optional deeper file check',contributor)
        advanced_steps=('Save this moment','I saved the file',
                        'Open Compare moments to review it','Open a session ZIP',
                        'select the downloaded file')
        advanced_positions=[contributor.index(step) for step in advanced_steps]
        self.assertEqual(advanced_positions,sorted(advanced_positions))

    def test_approach_page_defines_zero_command_and_distinguishes_phone_modes(self):
        with tempfile.TemporaryDirectory() as d:
            build(Path(d))
            page=(Path(d)/'approach'/'index.html').read_text()
        self.assertIn('Zero command means',page)
        self.assertIn('You choose when to start and stop',page)
        self.assertIn('capture stops when you leave it',page)
        self.assertIn('ongoing Stop notification',page)
        self.assertIn('Named-phone behavior is still unverified',page)
        self.assertIn('Try the microphone-free example',page)
        self.assertIn('Read the full zero-command safeguards',page)
        self.assertIn('not evidence that an animal replied or what it means',page)

    def test_scientific_review_form_records_the_bounded_candidate(self):
        project_root=Path(__file__).resolve().parents[1]
        form=(project_root/'.github'/'ISSUE_TEMPLATE'/'scientific-review.yml').read_text()
        self.assertIn('id: review-target',form)
        self.assertIn('No first benchmark is selected.',form)
        for candidate in (
            'OpenWhistle dolphin whistle detection/type classification',
            'bat interaction-context prediction',
            'zebra-finch turn-taking',
            'zebra-finch call-perception comparison',
            'V33DA caller attribution',
            'Great Tit song structure',
            'honeybee dance/follower evaluation',
        ):
            with self.subTest(candidate=candidate):
                self.assertIn(candidate,form)
        packet=(project_root/'docs'/'FIRST_DATASET_REVIEW_PACKET.md').read_text()
        self.assertIn('Honeybee / waggle dance and follower data',packet)
        for evidence in (
            'Bottlenose dolphin / OpenWhistle',
            'session-disjoint, not animal-disjoint',
            'five months',
            'cetacean-bioacoustics',
            'LICENSE-DATA',
            'Claim class',
            'signal time, receiver availability, observed receiver presence/attention',
            'not a validated universal schema',
            'https://metivity.github.io/talk2nature/research/openwhistle-dolphin-benchmark/',
        ):
            with self.subTest(review_packet=evidence):
                self.assertIn(evidence,packet)
        target_field=form.split('id: review-target',1)[1].split('  - type:',1)[0]
        self.assertIn('required: true',target_field)
        conflict_field=form.split('id: conflict-disclosure',1)[1].split('  - type:',1)[0]
        self.assertIn('required: true',conflict_field)
        self.assertIn('authored a reviewed source',conflict_field)
        self.assertIn('none known',conflict_field)
        receiver_field=form.split('id: receiver-evidence',1)[1].split('  - type:',1)[0]
        self.assertIn('signal time/event',receiver_field)
        self.assertIn('natural observation from an intervention',receiver_field)
        self.assertIn('Pure detection/classification reviews may write “not applicable.”',receiver_field)
        self.assertIn('required: false',receiver_field)

    def test_contribute_page_surfaces_the_phone_first_task_without_data_intake(self):
        project_root=Path(__file__).resolve().parents[1]
        guide=(project_root/'CONTRIBUTING.md').read_text()
        self.assertIn('https://github.com/Metivity/talk2nature/issues/115',guide)
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/Metivity/talk2nature')
            page=(root/'contribute'/'index.html').read_text()
            self.assertIn('A PHONE-FRIENDLY FIRST TASK',page)
            self.assertIn('Try the Field Companion with the microphone off.',page)
            self.assertIn('no-microphone practice option',page)
            self.assertNotIn('“Try invented example · no microphone,”',page)
            self.assertIn('href="https://github.com/Metivity/talk2nature/issues/115"',page)
            self.assertIn('Trying the workflow requires no account.',page)
            self.assertIn('Public GitHub replies need GitHub sign-in.',page)
            style=(root/'assets'/'style.css').read_text()
            self.assertIn('.first-contribution .actions a{min-height:44px',style)

    def test_reproduction_form_defaults_to_unverified_and_defines_counting_boundary(self):
        project_root=Path(__file__).resolve().parents[1]
        form=(project_root/'.github'/'ISSUE_TEMPLATE'/'reproduction.yml').read_text()
        guide=(project_root/'CONTRIBUTING.md').read_text()
        unverified='- Not sure / not independently verified'
        independent='- Independent evaluator (no project or maintainer assistance)'
        self.assertLess(form.index(unverified),form.index(independent))
        self.assertIn('name: Workflow report (browser or code)',form)
        self.assertIn('maintainers review reports',form)
        self.assertIn("title: '[Workflow report] '",form)
        self.assertIn('https://metivity.github.io/talk2nature/app/compare/',form)
        self.assertIn('The browser route needs no code, account, recording or upload',form)
        self.assertIn('If unsure, write “unknown.”',form)
        self.assertIn('A blocked attempt is useful',form)
        self.assertIn('only a maintainer-reviewed run of the documented software commands counts toward independent reproduction',guide)

    def test_dog_bark_review_separates_context_association_split_and_component_rights(self):
        project_root=Path(__file__).resolve().parents[1]
        note=next(n for n in load('research') if n['slug']=='dog-barks')
        self.assertEqual(note['review_depth'].split(',')[0],'Full seven-page ACL Anthology paper reviewed on 2026-10-13')
        self.assertIn('manually assigned',note['limitations'])
        self.assertIn('session, stimulus-instance or recording-condition grouping',note['limitations'])
        self.assertIn('not proof that those groups leaked',note['limitations'])
        self.assertEqual(len(note['review_request']['questions']),4)
        guide=(project_root/'docs'/'DOG_BARK_REVIEW.md').read_text()
        self.assertIn('does not link a versioned deposit',note['study_snapshot'][-1][1])
        self.assertIn('The paper PDF states CC BY-NC 4.0',guide)
        self.assertIn('No data or code were requested, downloaded, executed',guide)
        resources=json.loads((project_root/'research'/'resources.json').read_text())['resources']
        selected={r['id']:r for r in resources if r['id'].startswith('dog-bark-decoding-')}
        self.assertEqual(set(selected),{
            'dog-bark-decoding-paper-2024',
            'dog-bark-decoding-data-2024',
            'dog-bark-decoding-code-2024',
        })
        self.assertEqual({r['kind'] for r in selected.values()},{'paper','dataset','code'})
        for resource in selected.values():
            with self.subTest(resource=resource['id']):
                self.assertEqual(resource['source_ids'],[21])
                self.assertEqual(resource['acquisition'],'metadata_only')
                self.assertEqual(resource['files'],[])
        self.assertIn('Conflicting notices',selected['dog-bark-decoding-paper-2024']['rights']['license'])
        self.assertIn('Not stated',selected['dog-bark-decoding-data-2024']['rights']['license'])
        self.assertIn('Not stated',selected['dog-bark-decoding-code-2024']['rights']['license'])
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/Metivity/talk2nature')
            self.assertTrue(check_site(root)['public'])
            page=(root/'research'/'dog-barks'/'index.html').read_text()
            description=SearchDescriptionParser()
            description.feed(page)
            self.assertIn('dog-held-out context classification predicts associations',description.description)
            self.assertIn('OPEN METHODS QUESTION',page)
            self.assertIn('dog-grouped evaluation',page)
            self.assertIn('Read the focused reviewer brief',page)
            self.assertIn('https://github.com/Metivity/talk2nature/blob/main/docs/DOG_BARK_REVIEW.md',page)
            self.assertIn('scientific-review.yml',page)
            self.assertIn('/research/dog-barks/',(root/'sitemap.xml').read_text())
            paths=(root/'research'/'starting-points'/'index.html').read_text()
            self.assertIn('/research/dog-barks/',paths)
            resource_page=(root/'research'/'resources'/'index.html').read_text()
            self.assertIn('Dog vocalization dataset described in the 2024 bark-classification paper',resource_page)
            self.assertIn('Dog-bark baseline implementations described in the 2024 paper',resource_page)

    def test_birdcode_note_keeps_detection_proposals_and_asset_rights_separate(self):
        project_root=Path(__file__).resolve().parents[1]
        note=next(n for n in load('research') if n['slug']=='birdcode-event-detection')
        self.assertEqual(note['source_ids'],[610,611,612,620])
        self.assertIn('full bioRxiv v1 article text',note['review_depth'])
        self.assertIn('shared environmental drivers',note['limitations'])
        self.assertIn('7.6 Hz',note['finding'])
        self.assertIn('five seconds',note['finding'])
        self.assertIn('separate proposal layer',note['lesson'])
        resources=json.loads((project_root/'research'/'resources.json').read_text())['resources']
        by_id={r['id']:r for r in resources}
        self.assertEqual(by_id['birdcode-sound-event-detection-code']['rights']['license'],'MIT')
        self.assertIn('MIT declared',by_id['birdcode-pretrained-checkpoint']['rights']['license'])
        self.assertEqual(by_id['birdcode-pretrained-checkpoint']['acquisition'],'metadata_only')

    def test_animal_audio_model_map_is_cited_bounded_and_publicly_discoverable(self):
        project_root=Path(__file__).resolve().parents[1]
        note=next(n for n in load('research') if n['slug']=='animal-audio-model-landscape-2026')
        self.assertEqual(len(note['source_ids']),12)
        self.assertIn('not an exhaustive survey',note['review_depth'])
        self.assertIn('not what an animal intends',note['finding'])
        self.assertIn('No household phone feasibility',note['limitations'])
        self.assertIn('Do not train a foundation model',note['lesson'])
        source_ids={source['id'] for source in load('sources')}
        self.assertTrue(set(note['source_ids']) <= source_ids)
        paths=json.loads((project_root/'content'/'learning-paths.json').read_text())['paths']
        model_path=next(path for path in paths if path['id']=='model')
        self.assertIn(note['slug'],model_path['notes'])
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/Metivity/talk2nature')
            page=(root/'research'/note['slug']/'index.html').read_text()
            self.assertIn('robots" content="index,follow',page)
            self.assertIn('https://fixture.github.io/talk2nature/research/'+note['slug']+'/',page)
            self.assertIn('AVEX offers a common interface',page)
            self.assertIn('Every paper, code package, checkpoint',page)
            self.assertIn('/research/'+note['slug']+'/',(root/'sitemap.xml').read_text())
            reading_path=(root/'research'/'starting-points'/'index.html').read_text()
            self.assertIn('/research/'+note['slug']+'/',reading_path)

    def test_elephant_chorus_note_keeps_overlap_context_and_permissions_bounded(self):
        project_root=Path(__file__).resolve().parents[1]
        note=next(n for n in load('research') if n['slug']=='elephant-chorus-context-convergence')
        self.assertEqual(note['source_ids'],[613,614])
        self.assertIn('92 exchanges',note['finding'])
        self.assertIn('200 iterations',note['limitations'])
        self.assertIn('No playback test',note['limitations'])
        self.assertEqual(note['atlas']['locations'][0]['place_id'],'amboseli')
        resources=json.loads((project_root/'research'/'resources.json').read_text())['resources']
        by_id={r['id']:r for r in resources}
        self.assertEqual(by_id['elephant-chorus-context-convergence-paper-2026']['rights']['license'],'CC-BY-4.0')
        self.assertEqual(by_id['elephant-chorus-context-convergence-code-2026']['rights']['license'],'Not stated')
        self.assertEqual(by_id['elephant-chorus-context-convergence-data-2026']['rights']['license'],'Not stated')
        self.assertEqual(by_id['elephant-chorus-context-convergence-data-2026']['acquisition'],'metadata_only')

    def test_cockatiel_receiver_response_note_preserves_mixed_results_and_passive_app_boundary(self):
        project_root=Path(__file__).resolve().parents[1]
        note=next(n for n in load('research') if n['slug']=='cockatiel-distress-call-affiliation-response')
        self.assertEqual(note['source_ids'],[462,463])
        self.assertIn('Ten captive cockatiels',note['finding'])
        self.assertIn('did not differ (p=.37)',note['finding'])
        self.assertIn('No audio, video, code or model was acquired',note['limitations'])
        resources=json.loads((project_root/'research'/'resources.json').read_text())['resources']
        selected={r['id']:r for r in resources if r['id'].startswith('cockatiel-distress-call-study-')}
        self.assertEqual(set(selected),{
            'cockatiel-distress-call-study-paper-2018',
            'cockatiel-distress-call-study-data-2018',
        })
        self.assertEqual(selected['cockatiel-distress-call-study-paper-2018']['rights']['research_use'],'conditional')
        data=selected['cockatiel-distress-call-study-data-2018']
        self.assertEqual(data['rights']['license'],'CC-BY-4.0')
        self.assertEqual(data['rights']['research_use'],'conditional')
        self.assertEqual(data['rights']['commercial_use'],'conditional')
        self.assertEqual(data['rights']['redistribution'],'conditional')
        self.assertEqual(data['acquisition'],'sample_approved')
        self.assertEqual(data['adapter'],'figshare_plos')
        self.assertEqual(data['files'][0]['figshare_file_id'],13219823)
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/fixture/talk2nature')
            self.assertTrue(check_site(root)['public'])
            page=(root/'research'/'cockatiel-distress-call-affiliation-response'/'index.html').read_text()
            self.assertIn('Cockatiels show mixed receiver responses',page)
            self.assertIn('not decoded call meaning',page)
            self.assertIn('The study elicited distress calls',page)
            resource_page=(root/'research'/'resources'/'index.html').read_text()
            self.assertIn('Supporting data for cockatiel distress-call receiver-response study',resource_page)
            self.assertNotIn('data/external/',resource_page)
            report=json.loads((project_root/'research'/'cockatiel_s1_report.json').read_text())
            self.assertFalse(report['interpretation']['training_admitted'])
            self.assertFalse(report['interpretation']['research_admission'])
            self.assertIn('/research/cockatiel-distress-call-affiliation-response/',
                          (root/'sitemap.xml').read_text())

    def test_barkopedia_context_note_is_discoverable_and_keeps_rights_and_meaning_separate(self):
        project_root=Path(__file__).resolve().parents[1]
        note=next(n for n in load('research') if n['slug']=='barkopedia-context-benchmark-2025')
        self.assertEqual(note['purpose'],'Models & evaluation')
        self.assertEqual(note['source_ids'],[316,317,326])
        self.assertIn('video-assisted',note['finding'])
        self.assertIn('does not show that an audio prediction represents',note['finding'])
        self.assertIn('per-recording source permissions',note['limitations'])
        self.assertIn('No archive, CSV, audio, code or model was downloaded or executed',note['review_depth'])
        model_path=next(path for path in load('learning-paths')['paths'] if path['id']=='model')
        self.assertIn('barkopedia-context-benchmark-2025',model_path['notes'])
        resources=json.loads((project_root/'research'/'resources.json').read_text())['resources']
        selected={r['id']:r for r in resources if r['id'].startswith('barkopedia-')}
        self.assertEqual(set(selected),{
            'barkopedia-challenge-2025',
            'barkopedia-challenge-site-code-2025',
            'barkopedia-dog-activity-environment-data-2025',
        })
        self.assertEqual(selected['barkopedia-challenge-2025']['rights']['license'],'MIT declared in the pinned GitHub repository LICENSE')
        self.assertEqual(selected['barkopedia-dog-activity-environment-data-2025']['rights']['research_use'],'unresolved')
        for resource in selected.values():
            with self.subTest(resource=resource['id']):
                self.assertEqual(resource['acquisition'],'metadata_only')
                self.assertEqual(resource['files'],[])
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/Metivity/talk2nature')
            self.assertTrue(check_site(root)['public'])
            page=(root/'research'/'barkopedia-context-benchmark-2025'/'index.html').read_text()
            self.assertIn('Barkopedia: context labels do not show call meaning',page)
            self.assertIn('name="robots" content="index,follow"',page)
            self.assertIn('https://fixture.github.io/talk2nature/research/barkopedia-context-benchmark-2025/',page)
            self.assertIn('video-assisted inference',page)
            self.assertIn('source recordings',page)
            self.assertIn('/research/barkopedia-context-benchmark-2025/',(root/'sitemap.xml').read_text())
            paths=(root/'research'/'starting-points'/'index.html').read_text()
            self.assertIn('/research/barkopedia-context-benchmark-2025/',paths)

    def test_emotionalcanines_review_separates_video_labels_from_animal_meaning(self):
        project_root=Path(__file__).resolve().parents[1]
        note=next(n for n in load('research') if n['slug']=='emotionalcanines-dog-arousal-valence-2025')
        self.assertEqual(note['source_ids'],[325,326,327])
      …45841 tokens truncated…ham-great-tit-song-structure-2024')
        self.assertEqual(note['source_ids'],[363,364,365,366,367,372,426,496,497])
        self.assertIn('109,963 annotated songs',note['finding'])
        self.assertIn('23 files totaling 12,184,678,510 bytes',note['finding'])
        self.assertIn('14 data files',note['finding'])
        self.assertIn('nine documentation files',note['finding'])
        self.assertIn('no independently observed interaction context',note['finding'])
        self.assertIn('2025 paper already trained a ViT metric-learning model',note['finding'])
        self.assertIn('earlier same-day 14-entry traversal',note['review_depth'])
        self.assertIn('malformed at 63 characters',note['review_depth'])
        self.assertIn('SHA-256 and MD5 match the current OSF API',note['review_depth'])
        self.assertNotIn('discrepancy remains unresolved',note['review_depth'])
        shared_package=next(value for label,value in note['study_snapshot'] if label=='Shared package')
        self.assertIn('complete OSF API root lists 23 files',shared_package)
        self.assertIn('nine documentation files',shared_package)
        self.assertNotIn('14 current file items',shared_package)
        rights_summary=next(value for label,value in note['study_snapshot'] if label=='Separate rights')
        self.assertIn('for its dataset record',rights_summary)
        self.assertIn('British National Grid',note['limitations'])
        self.assertIn('keep public geography coarse',note['limitations'])
        self.assertIn('as a held-out-individual baseline',note['limitations'])
        self.assertEqual(note['atlas']['location_status'],'mapped')
        self.assertEqual(note['atlas']['locations'][0]['place_id'],'wytham-woods')
        self.assertEqual(note['atlas']['locations'][0]['source_id'],367)
        self.assertEqual(note['atlas']['locations'][0]['role'],'study_region')
        resources=json.loads((project_root/'research'/'resources.json').read_text())['resources']
        selected={r['id']:r for r in resources if r['id'].startswith('wytham-great-tit-')}
        self.assertEqual(set(selected),{
            'wytham-great-tit-song-paper-2024',
            'wytham-great-tit-song-dataset-osf',
            'wytham-great-tit-song-setup-code',
            'wytham-great-tit-culture-paper-2025',
            'wytham-great-tit-source-data',
        })
        dataset=selected['wytham-great-tit-song-dataset-osf']
        self.assertEqual(dataset['source_ids'],[363,364,365,372,426])
        self.assertEqual(dataset['acquisition'],'metadata_only')
        self.assertIn('23 files totaling 12,184,678,510 bytes',dataset['access'])
        self.assertIn('One 6,426-byte documentation file',dataset['access'])
        self.assertIn('CC BY 4.0',dataset['rights']['license'])
        self.assertIn('British National Grid',dataset['limitations'])
        self.assertIn('Do not expose precise nestbox coordinates',dataset['rights']['conditions'])
        self.assertIn('match current OSF SHA-256 and MD5',dataset['rights']['conditions'])
        self.assertEqual(dataset['files'],[])
        verification=json.loads((project_root/'research'/'wytham_file_verification_2026-10-25.json').read_text())
        self.assertEqual(verification['verification']['actual_bytes'],6426)
        self.assertTrue(verification['verification']['sha256_matches_current_osf_api'])
        self.assertTrue(verification['verification']['md5_matches_current_osf_api'])
        self.assertFalse(verification['verification']['content_reviewed'])
        checksum_source=next(s for s in json.loads((project_root/'content'/'sources.json').read_text()) if s['id']==426)
        self.assertEqual(checksum_source['checked'],'2026-10-25')
        self.assertIn('not read or redistributed',checksum_source['origin'])
        manifest=json.loads((project_root/'research'/'wytham_osf_manifest_2026-10-24.json').read_text())
        summary=manifest['summary']
        self.assertEqual(summary['current_api_file_count'],23)
        self.assertEqual(summary['data_folder_file_count'],14)
        self.assertEqual(summary['docs_folder_file_count'],9)
        self.assertTrue(summary['prior_snapshot_path_size_match_after_leading_slash_normalization'])
        self.assertEqual(summary['prior_snapshot_provider_hash_differences'],['docs/metadata/main.md'])
        self.assertFalse(manifest['retrieval']['payload_bytes_downloaded'])
        self.assertEqual(selected['wytham-great-tit-song-setup-code']['rights']['license'],'MIT as declared by official GitHub repository.')
        demography_code=next(r for r in resources if r['id']=='wytham-song-demography-analysis-code-v1')
        self.assertEqual(demography_code['acquisition'],'metadata_only')
        self.assertEqual(demography_code['source_ids'],[367,496,497])
        self.assertIn('MIT',demography_code['rights']['license'])
        self.assertIn('CC BY 4.0',demography_code['rights']['license'])
        self.assertIn('as independent test truth',demography_code['decision'])
        self.assertEqual(demography_code['files'],[])
        meaning=next(p for p in json.loads((project_root/'content'/'learning-paths.json').read_text())['paths'] if p['id']=='meaning')
        self.assertIn(note['slug'],meaning['notes'])
        plan=(project_root/'docs'/'FIRST_ANIMAL_PLAN.md').read_text()
        self.assertIn('not a replacement for the bat context-prediction candidate',plan)
        self.assertIn('methods-reproduction exercise',plan)
        self.assertIn('conflicting data-license declarations',plan)
        sources=json.loads((project_root/'content'/'sources.json').read_text())
        author_docs=next(s for s in sources if s['id']==364)
        self.assertEqual(author_docs['checked'],'2026-10-24')
        self.assertIn('British National Grid coordinates',author_docs['origin'])
        self.assertEqual(author_docs['review_url'],'https://nilomr.github.io/great-tit-hits/site/metadata/nestboxes/')
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/Metivity/talk2nature')
            self.assertTrue(check_site(root)['public'])
            page=(root/'research'/note['slug']/'index.html').read_text()
            self.assertIn('109,963 annotated songs',page)
            self.assertIn('not a conversation model',page)
            self.assertIn('British National Grid coordinates',page)
            self.assertIn('do not expose precise coordinates',page)
            self.assertIn('Author documentation for nestbox location fields',page)
            self.assertIn('name="robots" content="index,follow"',page)
            self.assertIn(f'/research/{note["slug"]}/',(root/'sitemap.xml').read_text())
            paths=(root/'research'/'starting-points'/'index.html').read_text()
            self.assertIn(f'/research/{note["slug"]}/',paths)

    def test_birdpark_zebra_finch_records_keep_event_tasks_and_rights_bounded(self):
        project_root=Path(__file__).resolve().parents[1]
        note=next(n for n in load('research') if n['slug']=='zebra-finch-birdpark-multimodal-segmentation-2025')
        self.assertEqual(note['source_ids'],[390,391,392,393,517,518])
        self.assertIn('not what a call means',note['finding'])
        self.assertIn('28 minutes is the evaluated subset',note['finding'])
        self.assertIn('do not establish phone/home generalization',note['limitations'])
        self.assertIn('guessed caller identity from repertoire and noise levels',note['finding'])
        self.assertIn('exact file-level mapping',note['limitations'])
        resources=json.loads((project_root/'research'/'resources.json').read_text())['resources']
        selected={r['id']:r for r in resources if r['id'].startswith('birdpark-')}
        self.assertEqual(set(selected),{
            'birdpark-multimodal-songbird-paper-2025',
            'birdpark-zebra-finch-groups-zenodo-v2-2024',
            'birdpark-zebra-finch-pairs-zenodo-v1-2022',
            'birdpark-paired-zebra-finch-annotation-examples-zenodo-v2-2026',
            'birdpark-zebra-finch-pairs-eth-zurich-2025',
            'birdpark-birdradio-software',
        })
        for resource in selected.values():
            with self.subTest(resource=resource['id']):
                self.assertEqual(resource['acquisition'],'metadata_only')
                self.assertEqual(resource['files'],[])
        self.assertEqual(selected['birdpark-zebra-finch-groups-zenodo-v2-2024']['rights']['research_use'],'unresolved')
        self.assertEqual(selected['birdpark-zebra-finch-pairs-zenodo-v1-2022']['rights']['research_use'],'unresolved')
        self.assertEqual(selected['birdpark-paired-zebra-finch-annotation-examples-zenodo-v2-2026']['rights']['redistribution'],'unresolved')
        self.assertEqual(selected['birdpark-zebra-finch-pairs-eth-zurich-2025']['rights']['commercial_use'],'not_admitted')
        self.assertEqual(selected['birdpark-birdradio-software']['rights']['license'],'GNU GPL v3.0 or later, as stated by the BirdRadio subproject LICENSE page.')
        self.assertIn('not the full repository',selected['birdpark-birdradio-software']['rights']['scope'])
        self.assertEqual(selected['birdpark-zebra-finch-groups-zenodo-v2-2024']['source_ids'],[390,391,517])
        self.assertEqual(selected['birdpark-zebra-finch-pairs-zenodo-v1-2022']['source_ids'],[390,517])
        sources=json.loads((project_root/'content'/'sources.json').read_text())
        self.assertEqual([next(s for s in sources if s['id']==source_id)['checked'] for source_id in note['source_ids']],['2026-10-30','2026-10-30','2026-10-24','2026-10-24','2026-10-30','2026-10-30'])
        self.assertIn('peer-reviewed PMC full text',next(s for s in sources if s['id']==390)['origin'])
        self.assertIn('MP4/HDF5',next(s for s in sources if s['id']==391)['description'])
        self.assertIn('No dataset license',next(s for s in sources if s['id']==517)['description'])
        self.assertIn('not establish the license for the full GitLab collection',next(s for s in sources if s['id']==518)['description'])
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/Metivity/talk2nature')
            self.assertTrue(check_site(root)['public'])
            page=(root/'research'/note['slug']/'index.html').read_text()
            self.assertIn('not translate them',page)
            self.assertIn('do not establish phone/home generalization',page)
            self.assertIn('28 minutes is the evaluated subset',page)
            self.assertIn('caller labels need independence review',page)
            self.assertIn('name="robots" content="index,follow"',page)
            self.assertIn(f'/research/{note["slug"]}/',(root/'sitemap.xml').read_text())
            resource_page=(root/'research'/'resources'/'index.html').read_text()
            self.assertIn('BirdPark zebra-finch group recordings',resource_page)
            self.assertIn('BirdPark zebra-finch paired recordings and annotations, Zenodo v1',resource_page)
            self.assertIn('BirdPark BirdRadio synchronized audio and transmitter acquisition software',resource_page)
            self.assertIn('In Copyright - Non-Commercial Use Permitted',resource_page)

    def test_zebra_finch_human_guided_clustering_keeps_versions_and_asset_rights_separate(self):
        project_root=Path(__file__).resolve().parents[1]
        note=next(n for n in load('research') if n['slug']=='zebra-finch-human-guided-clustering-2026')
        self.assertEqual(note['source_ids'],[394,395,396,397,398,399])
        self.assertIn('does not test unseen-bird',note['limitations'])
        self.assertIn('acoustic clusters, not validated call meanings',note['finding'])
        resources=json.loads((project_root/'research'/'resources.json').read_text())['resources']
        selected={r['id']:r for r in resources if r['id'].startswith('zebra-finch-vocal-clustering') or r['id'] in {
            'zebra-finch-human-guided-clustering-paper-2026','semi-automated-clustering-tool-2026','whisperseg-animal-vad-ct2-weights'
        }}
        self.assertEqual(len(selected),6)
        for resource in selected.values():
            with self.subTest(resource=resource['id']):
                self.assertEqual(resource['acquisition'],'metadata_only')
                self.assertEqual(resource['files'],[])
        v1=selected['zebra-finch-vocal-clustering-data-zenodo-v1-18156254']
        v2=selected['zebra-finch-vocal-clustering-data-zenodo-v2-22657329']
        separate=selected['zebra-finch-vocal-clustering-data-zenodo-18100613']
        self.assertNotEqual(v1['id'],v2['id'])
        self.assertIn('conceptrecid 18156253',v2['version'])
        self.assertIn('different concept ID',v2['decision'])
        self.assertIn('CC BY 4.0',v2['rights']['license'])
        self.assertIn('18100612',separate['version'])
        self.assertEqual(selected['semi-automated-clustering-tool-2026']['rights']['license'].split()[0],'MIT')
        model=selected['whisperseg-animal-vad-ct2-weights']
        self.assertEqual(model['rights']['research_use'],'unresolved')
        self.assertIn('null license value',model['decision'])
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/Metivity/talk2nature')
            self.assertTrue(check_site(root)['public'])
            page=(root/'research'/note['slug']/'index.html').read_text()
            self.assertIn('Human-guided clustering helps label zebra-finch calls',page)
            self.assertIn('not decode meaning',page)
            self.assertIn('name="robots" content="index,follow"',page)
            self.assertIn(f'/research/{note["slug"]}/',(root/'sitemap.xml').read_text())
            resource_page=(root/'research'/'resources'/'index.html').read_text()
            self.assertIn('Zebra Finch Vocalization Dataset for Semi-Automated Clustering, Zenodo v2',resource_page)
            self.assertIn('MIT as declared by the pinned GitHub repository LICENSE file',resource_page)

    def test_zebra_finch_call_perception_names_paper_cited_zenodo_version(self):
        project_root=Path(__file__).resolve().parents[1]
        note=next(n for n in load('research') if n['slug']=='zebra-finch-call-categories-2025')
        sources={row['id']:row for row in load('sources')}
        resources=json.loads((project_root/'research'/'resources.json').read_text())['resources']
        archive=next(r for r in resources if r['id']=='zebra-finch-call-category-behavior-and-code-2025')
        self.assertIn(19,note['source_ids'])
        self.assertIn('Julie Elie received the 2026 Coller Dolittle annual prize',note['year_label'])
        self.assertEqual(sources[19]['checked'],'2026-10-28')
        self.assertIn('names zebra-finch researcher Julie Elie',sources[19]['description'])
        self.assertIn('versioned Zenodo record 13623969 (v1)',note['review_locator'])
        self.assertIn('concept DOI 13623968',note['review_locator'])
        self.assertIn('later v3 resubmission is record 15795568',note['review_locator'])
        self.assertEqual(archive['url'],'https://zenodo.org/records/13623969')
        self.assertIn('Paper-cited Zenodo version 1.0',archive['version'])
        self.assertIn('later version 3.0',archive['version'])
        self.assertEqual(archive['acquisition'],'metadata_only')
        self.assertEqual(archive['files'],[])
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/Metivity/talk2nature')
            self.assertTrue(check_site(root)['public'])
            page=(root/'research'/note['slug']/'index.html').read_text()
            self.assertIn('13623969',page)
            self.assertIn('15795568',page)
            self.assertIn('Julie Elie received the 2026 Coller Dolittle annual prize',page)
            resource_page=(root/'research'/'resources'/'index.html').read_text()
            self.assertIn('https://zenodo.org/records/13623969',resource_page)
            self.assertIn('later version 3.0',resource_page)

    def test_zebra_finch_birdaves_semantic_supervision_is_prior_art_not_receiver_alignment(self):
        project_root=Path(__file__).resolve().parents[1]
        notes=load('research')
        model_note=next(n for n in notes if n['slug']=='zebra-finch-call-classifier-multitask-2026')
        call_note=next(n for n in notes if n['slug']=='zebra-finch-call-categories-2025')
        sources=json.loads((project_root/'content'/'sources.json').read_text())
        source={row['id']:row for row in sources}
        self.assertIn('six behavior-derived functional/semantic categories',model_note['finding'])
        self.assertIn('does not report a direct item-level comparison',model_note['limitations'])
        self.assertIn('not a verified mapping to the 2025 stimulus set',call_note['limitations'])
        self.assertIn('ColColxxxx_yymmdd-VT-zz.wav',source[376]['description'])
        self.assertIn('known naming discrepancies',source[376]['description'])
        self.assertIn('provider MD5',source[377]['description'])
        self.assertEqual(source[376]['checked'],'2026-10-25')
        self.assertEqual(source[377]['checked'],'2026-10-25')
        resources=json.loads((project_root/'research'/'resources.json').read_text())['resources']
        article=next(r for r in resources if r['id']=='zebra-finch-call-classifier-paper-2026')
        self.assertEqual(article['acquisition'],'metadata_only')
        self.assertEqual(article['files'],[])
        self.assertIn('Behavior-derived semantic supervision is already implemented',article['decision'])


    def test_humpback_tag_sensor_note_keeps_caller_and_phone_claims_bounded(self):
        project_root=Path(__file__).resolve().parents[1]
        note=next(n for n in load('research') if n['slug']=='humpback-tag-accelerometer-caller-attribution-2026')
        self.assertEqual(note['source_ids'],[486,487,488])
        self.assertIn('56 of 1,090 known focal calls',note['finding'])
        self.assertIn('not a test of phone microphones',note['finding'])
        self.assertIn('did not reliably establish which whale produced a call',note['finding'])
        self.assertEqual(note['atlas']['location_status'],'mapped')
        self.assertIn('No animal-level location is mapped',note['atlas']['locations'][0]['basis'])
        self.assertIn('no third-party data or code was admitted',note['reuse']['status'])
        resources=json.loads((project_root/'research'/'resources.json').read_text())['resources']
        selected={r['id']:r for r in resources if r['id'].startswith('humpback-')}
        self.assertEqual(set(selected),{
            'humpback-accelerometer-caller-attribution-paper-2026',
            'humpback-focal-caller-data-zenodo-v1-2026',
            'humpback-caller-attribution-matlab-code-zenodo-v1-2026',
        })
        self.assertTrue(all(r['acquisition']=='metadata_only' and r['files']==[] for r in selected.values()))
        self.assertIn('CC BY 4.0 at the Zenodo record level',selected['humpback-focal-caller-data-zenodo-v1-2026']['rights']['license'])
        self.assertIn('not a separately verified software license',selected['humpback-caller-attribution-matlab-code-zenodo-v1-2026']['rights']['license'])
        learning=json.loads((project_root/'content'/'learning-paths.json').read_text())
        label_path=next(p for p in learning['paths'] if p['id']=='label')
        self.assertIn(note['slug'],label_path['notes'])
        with tempfile.TemporaryDirectory() as temp:
            build(Path(temp),'https://fixture.github.io/talk2nature',True)
            page=(Path(temp)/'research'/note['slug']/'index.html').read_text()
            self.assertIn('href="/talk2nature/research/atlas/"',page)
            self.assertIn('See this coarse literature location in the world atlas',page)

    def test_canary_home_archive_is_an_architecture_reference_not_model_data(self):
        project_root=Path(__file__).resolve().parents[1]
        note=next(n for n in load('research') if n['slug']=='canary-song-archive-home-recording-project')
        self.assertEqual(note['source_ids'],[498])
        self.assertIn('5,554 recordings',note['finding'])
        self.assertIn('CC BY-NC 4.0',note['limitations'])
        self.assertIn('linked privacy policy was not reviewed',note['limitations'])
        self.assertIn('not a parrot cohort',note['limitations'])
        self.assertEqual(note['reuse']['status'][:13],'Metadata-only')
        sources=json.loads((project_root/'content'/'sources.json').read_text())
        source=next(s for s in sources if s['id']==498)
        self.assertIn('Direct page retrieval timed out',source['origin'])
        resources=json.loads((project_root/'research'/'resources.json').read_text())['resources']
        resource=next(r for r in resources if r['id']=='canary-song-archive-community-project')
        self.assertEqual(resource['kind'],'project')
        self.assertEqual(resource['acquisition'],'metadata_only')
        self.assertEqual(resource['files'],[])
        self.assertEqual(resource['rights']['commercial_use'],'not_admitted')
        with tempfile.TemporaryDirectory() as temp:
            build(Path(temp),'https://fixture.github.io/talk2nature',True)
            page=(Path(temp)/'research'/note['slug']/'index.html').read_text()
            self.assertIn('CC BY-NC 4.0',page)
            self.assertIn('not a communication benchmark',page)

    def test_marm_audio_is_call_type_methods_resource_not_communication_benchmark(self):
        project_root=Path(__file__).resolve().parents[1]
        note=next(n for n in load('research') if n['slug']=='marmaudio-common-marmoset-vocalization-dataset-2025')
        self.assertEqual(note['source_ids'],[499,500,501])
        self.assertIn('871,044 segmented vocalizations',note['finding'])
        self.assertIn('sender identity and production context',note['finding'])
        self.assertIn('model-assisted',note['limitations'])
        self.assertIn('9.43% average error in its validation text but 8.71%',note['limitations'])
        self.assertIn('CC BY 4.0',note['reuse']['rights'])
        self.assertIn('CC BY-NC-ND 4.0',note['reuse']['rights'])
        self.assertEqual(note['reuse']['status'][:13],'Metadata-only')
        sources=json.loads((project_root/'content'/'sources.json').read_text())
        self.assertEqual({s['id'] for s in sources if s['id'] in {499,500,501}},{499,500,501})
        resources=json.loads((project_root/'research'/'resources.json').read_text())['resources']
        resource=next(r for r in resources if r['id']=='marmaudio-common-marmoset-v7')
        self.assertEqual(resource['acquisition'],'metadata_only')
        self.assertEqual(resource['files'],[])
        self.assertEqual(resource['rights']['license'],'CC BY 4.0 at Zenodo v7 dataset-record level.')
        with tempfile.TemporaryDirectory() as temp:
            build(Path(temp),'https://fixture.github.io/talk2nature',True)
            page=(Path(temp)/'research'/note['slug']/'index.html').read_text()
            self.assertIn('not a sender-context benchmark',page)
            self.assertIn('No third-party data, audio or model was used',page)


    def test_birdeep_is_a_file_disjoint_candidate_not_site_held_out_evidence(self):
        project_root=Path(__file__).resolve().parents[1]
        note=next(n for n in load('research') if n['slug']=='birdeep-donana-bird-vocalization-detection-2025')
        self.assertEqual(note['source_ids'],[643,644,645])
        self.assertIn('does not establish a site-',note['finding'])
        self.assertIn('morning chorus',note['limitations'])
        self.assertIn('10.57967/hf/4821',note['limitations'])
        self.assertEqual(note['atlas']['location_status'],'pending')
        self.assertEqual(note['atlas']['locations'],[])
        resources=json.loads((project_root/'research'/'resources.json').read_text())['resources']
        selected={r['id']:r for r in resources if r['id'].startswith('birdeep-donana-') or r['id'].startswith('birdeep-neural-') or r['id'].startswith('birdeep-trained-')}
        self.assertIn('birdeep-donana-audio-annotations-2025',selected)
        self.assertIn('birdeep-neural-network-code-2026',selected)
        self.assertIn('birdeep-trained-model-artifacts-unassessed-2026',selected)
        self.assertIn('not inferred from the repository MIT license',selected['birdeep-trained-model-artifacts-unassessed-2026']['rights']['license'])
        with tempfile.TemporaryDirectory() as temp:
            build(Path(temp),'https://fixture.github.io/talk2nature',True,'https://github.com/Metivity/talk2nature')
            page=(Path(temp)/'research'/note['slug']/'index.html').read_text()
        self.assertIn('BIRDeep tests regional bird-event detection, not site transfer',page)
        self.assertIn('does not establish a site-',page)
        self.assertIn('index,follow',page)

    def test_arcticbirdsounds_methods_review_is_visible_and_bounded(self):
        project_root=Path(__file__).resolve().parents[1]
        note=next(n for n in load('research') if n['slug']=='arcticbirdsounds-grouped-split-preflight')
        request=note['review_request']
        self.assertEqual(request['guide_path'],'docs/REVIEWER_SCOPE_BIRDEVENT.md')
        self.assertEqual(request['issue_url'],'https://github.com/Metivity/talk2nature/issues/721')
        self.assertIn('no reviewer response',request['status'])
        self.assertIn('class-by-site',note['limitations'])
        self.assertIn('not a verified negative',note['finding'])
        guide=(project_root/'docs'/'REVIEWER_SCOPE_BIRDEVENT.md').read_text()
        self.assertIn('does not authorize row-level inspection',guide)
        self.assertIn('No reviewer response has been received',guide)
        with tempfile.TemporaryDirectory() as temp:
            build(Path(temp),'https://fixture.github.io/talk2nature',True,
                  'https://github.com/Metivity/talk2nature')
            page=(Path(temp)/'research'/note['slug']/'index.html').read_text()
        self.assertIn('OPEN METHODS QUESTION',page)
        self.assertIn('Can ArcticBirdSounds support a site-grouped bird-event pilot?',page)
        self.assertIn(request['issue_url'],page)
        self.assertIn('docs/REVIEWER_SCOPE_BIRDEVENT.md',page)
        self.assertIn('A review is not an endorsement or partnership',page)
        self.assertIn('index,follow',page)

    def test_mygardenbird_is_positive_only_and_rights_unresolved(self):
        note=next(n for n in load('research') if n['slug']=='mygardenbird-source-splits-and-rights-2026')
        self.assertEqual(note['source_ids'],[646,647,648])
        self.assertIn('bird-present versus bird-absent',note['finding'])
        self.assertIn('cannot test bird absence',note['title'])
        self.assertIn('35.3% of source recordings',note['limitations'])
        self.assertIn('Zenodo metadata API returns a null record-level license',note['limitations'])
        sources={s['id']:s for s in load('sources')}
        self.assertIn('Unlicense',sources[648]['description'])
        catalog={r['id']:r for r in json.loads((Path(__file__).resolve().parents[1]/'research'/'resources.json').read_text())['resources']}
        self.assertEqual(catalog['mygardenbird-dataset-zenodo-2026']['acquisition'],'metadata_only')
        self.assertIn('Unspecified in official Zenodo record metadata',catalog['mygardenbird-dataset-zenodo-2026']['rights']['license'])
        self.assertIn('Conflicting repo declarations',catalog['mygardenbird-code-github-2026']['rights']['license'])
        with tempfile.TemporaryDirectory() as temp:
            build(Path(temp),'https://fixture.github.io/talk2nature',True)
            html=(Path(temp)/'research'/note['slug']/'index.html').read_text()
        self.assertIn('index,follow',html)
        self.assertIn('source-recording',html)
        self.assertIn('cannot test verified absence',html)

    def test_peadetect_has_a_bounded_public_review_request_without_data_access(self):
        project_root=Path(__file__).resolve().parents[1]
        note=next(n for n in load('research') if n['slug']=='peadetect-peafowl-vocalization-dataset-2026')
        request=note['review_request']
        self.assertEqual(request['guide_path'],'docs/PEADETECT_REVIEW_BRIEF.md')
        self.assertEqual(len(request['questions']),5)
        self.assertIn('invites a public methods review',request['status'])
        self.assertIn('asks for no archive, manifest, labels, audio or coordinate access',request['summary'])
        guide=(project_root/'docs'/'PEADETECT_REVIEW_BRIEF.md').read_text()
        self.assertIn('1,858/2,950 = 62.98%',guide)
        self.assertIn('No independent review has been received',guide)
        self.assertIn('does not authorize file access',guide)
        issue_template=(project_root/'.github'/'ISSUE_TEMPLATE'/'scientific-review.yml').read_text()
        self.assertIn('metadata-only PeaDetect five-second peafowl detector candidate',issue_template)
        with tempfile.TemporaryDirectory() as temp:
            build(Path(temp),'https://fixture.github.io/talk2nature',True,'https://github.com/Metivity/talk2nature')
            page=(Path(temp)/'research'/note['slug']/'index.html').read_text()
        self.assertIn('Independent review requested: PeaDetect folds and source shortcuts',page)
        self.assertIn('Review the open methods question',page)
        self.assertLess(page.index('href=\"#open-methods-review\"'),page.index('OPEN METHODS QUESTION'))
        self.assertIn('docs/PEADETECT_REVIEW_BRIEF.md',page)
        self.assertIn('template=scientific-review.yml',page)
        self.assertIn('A review is not an endorsement or partnership',page)


if __name__=='__main__': unittest.main()
