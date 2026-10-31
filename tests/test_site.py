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
        evidence=guide.index('**Latest focused code check')
        self.assertLess(start,browser)
        self.assertLess(browser,code)
        self.assertLess(code,evidence)
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
                     'Open Compare moments to review it','Choose saved moment')
        for label in live_labels:
            with self.subTest(button=label):
                self.assertIn(label,station if label!='Choose saved moment' else compare)
        expected_steps=('Try an example · no microphone','Try invented example · no microphone',
                        'Mark an observation','Finish and review','End rehearsal',
                        'Save this moment','I saved the file',
                        'Open Compare moments to review it','Choose saved moment')
        for name in ('README.md','CONTRIBUTING.md'):
            with self.subTest(document=name):
                copy=(project_root/name).read_text()
                positions=[copy.index(step) for step in expected_steps]
                self.assertEqual(positions,sorted(positions))
                self.assertIn('to reopen the download',copy)

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

    def test_contribute_page_surfaces_the_phone_first_task_without_data_intake(self):
        project_root=Path(__file__).resolve().parents[1]
        guide=(project_root/'CONTRIBUTING.md').read_text()
        self.assertIn('https://github.com/Metivity/talk2nature/issues/115',guide)
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/Metivity/talk2nature')
            page=(root/'contribute'/'index.html').read_text()
            self.assertIn('GOOD FIRST TASK / PHONE',page)
            self.assertIn('Try the Field Companion with the microphone off.',page)
            self.assertIn('href="https://github.com/Metivity/talk2nature/issues/115"',page)
            self.assertIn('No animal recording or upload is needed.',page)
            self.assertIn('posting a public reply requires GitHub sign-in',page)
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
        self.assertIn('human video-derived behavior/affect annotations',note['finding'])
        self.assertIn('not an animal-reported state',note['finding'])
        self.assertIn('Fleiss kappa 0.30',note['review_depth'])
        resources=json.loads((project_root/'research'/'resources.json').read_text())['resources']
        selected={r['id']:r for r in resources if r['id'].startswith('emotionalcanines-')}
        self.assertEqual(set(selected),{'emotionalcanines-paper-acmmm-2025','emotionalcanines-dataset-2025'})
        self.assertEqual(selected['emotionalcanines-paper-acmmm-2025']['rights']['scope'],'Article only; does not grant rights to datasets, source videos, code or model weights.')
        dataset=selected['emotionalcanines-dataset-2025']
        self.assertEqual(dataset['rights']['research_use'],'unresolved')
        self.assertEqual(dataset['rights']['commercial_use'],'not_admitted')
        self.assertEqual(dataset['acquisition'],'metadata_only')
        self.assertEqual(dataset['files'],[])
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/Metivity/talk2nature')
            self.assertTrue(check_site(root)['public'])
            page=(root/'research'/'emotionalcanines-dog-arousal-valence-2025'/'index.html').read_text()
            self.assertIn('EmotionalCanines: video-derived labels are not a dog-reported emotion',page)
            self.assertIn('name="robots" content="index,follow"',page)
            self.assertIn('https://fixture.github.io/talk2nature/research/emotionalcanines-dog-arousal-valence-2025/',page)
            self.assertIn('c0617b15562882b9eee4cc1bcb8e6aa80e51bd34',page)
            self.assertIn('/research/emotionalcanines-dog-arousal-valence-2025/',(root/'sitemap.xml').read_text())
            resources_page=(root/'research'/'resources'/'index.html').read_text()
            self.assertIn('EmotionalCanines dog-bark arousal and valence dataset',resources_page)

    def test_crowdbark_project_is_discoverable_without_claiming_a_dataset_release(self):
        project_root=Path(__file__).resolve().parents[1]
        sources=json.loads((project_root/'content'/'sources.json').read_text())
        source=next(item for item in sources if item['id']==300)
        resources=json.loads((project_root/'research'/'resources.json').read_text())['resources']
        resource=next(item for item in resources if item['id']=='crowdbark-project-page')
        self.assertEqual(resource['kind'],'project')
        self.assertEqual(resource['source_ids'],[source['id']])
        self.assertEqual(resource['acquisition'],'metadata_only')
        self.assertEqual(resource['rights']['research_use'],'unresolved')
        self.assertIn('no versioned data release linked',resource['version'])
        with tempfile.TemporaryDirectory() as d:
            build(Path(d),'https://fixture.github.io/talk2nature',True,'https://github.com/Metivity/talk2nature')
            page=(Path(d)/'research'/'resources'/'index.html').read_text()
        self.assertIn('<option value="project">Project</option>',page)
        self.assertIn('CrowdBark: crowdsourced multimodal dog-communication study',page)
        self.assertIn('future open research dataset',page)
        self.assertIn('Unresolved; treat as not cleared.',page)

    def test_bat_methods_review_is_visible_and_preserves_evidence_boundaries(self):
        project_root=Path(__file__).resolve().parents[1]
        note=next(n for n in load('research') if n['slug']=='fruit-bat-context-ml-2024')
        self.assertEqual(len(note['review_request']['questions']),5)
        self.assertIn(353,note['source_ids'])
        self.assertIn(354,note['source_ids'])
        self.assertIn(355,note['source_ids'])
        self.assertIn('Please disclose authorship of the source dataset or target result',note['review_request']['summary'])
        resources=json.loads((project_root/'research'/'resources.json').read_text())['resources']
        relationship=next(r for r in resources if r['id']=='bat-reviewer-collaboration-paper-2025')
        self.assertEqual(relationship['source_ids'],[354])
        self.assertEqual(relationship['acquisition'],'metadata_only')
        self.assertEqual(relationship['files'],[])
        self.assertEqual(relationship['rights']['research_use'],'conditional')
        self.assertEqual(relationship['rights']['commercial_use'],'unresolved')
        self.assertEqual(relationship['rights']['redistribution'],'not_admitted')
        guide=(project_root/'docs'/'BAT_CONTEXT_REVIEW.md').read_text()
        self.assertIn('The exact paper partitions',guide)
        self.assertIn("not the paper's filtered 35,074-call subset",guide)
        self.assertIn('Replies from authors of either work can clarify provenance, files or methods, but they do not count as independent review',guide)
        self.assertIn('a separate 2025 Bat1K genomics paper',guide)
        self.assertIn('No independent specialist review has been received',guide)
        network=(project_root/'docs'/'NETWORK_AND_OUTREACH.md').read_text()
        self.assertIn('Disclose and assess that collaboration before describing a review as independent',network)
        self.assertIn('This is not bat-specialist evidence',network)
        card=(project_root/'docs'/'BENCHMARK_CANDIDATE_RUN_CARD.md').read_text()
        self.assertIn('Source-author replies are useful clarifications but do not satisfy the independent-review gate',card)
        university=(project_root/'docs'/'UNIVERSITY_EVALUATION.md').read_text()
        self.assertIn('it cannot count as independent review of them',university)

    def test_fruit_bat_context_study_is_prior_art_not_a_novel_benchmark(self):
        project_root=Path(__file__).resolve().parents[1]
        note=next(n for n in load('research') if n['slug']=='fruit-bat-context-ml-2024')
        self.assertIn('subject-independent folds',note['seo_description'])
        self.assertIn('caller-held-out split is not a novel benchmark',note['finding'])
        self.assertIn('published subject-independent result as prior art',note['lesson'])
        self.assertIn('Keep this candidate deferred.',note['next_review'])
        resources=json.loads((project_root/'research'/'resources.json').read_text())['resources']
        paper=next(r for r in resources if r['id']=='egyptian-fruit-bat-context-paper-2024')
        self.assertEqual(paper['reviewed'],'2026-10-29')
        self.assertEqual(paper['acquisition'],'metadata_only')
        self.assertEqual(paper['files'],[])
        self.assertIn('not a novel benchmark',paper['decision'])
        sources=json.loads((project_root/'content'/'sources.json').read_text())
        proceedings=next(s for s in sources if s['url']=='https://doi.org/10.23919/EUSIPCO63174.2024.10715475')
        arxiv=next(s for s in sources if s['url']=='https://arxiv.org/abs/2406.06332v1')
        for source in (proceedings,arxiv):
            with self.subTest(source=source['title']):
                self.assertEqual(source['checked'],'2026-10-29')
                self.assertIn('subject-independent folds are reported',source['origin'])
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/Metivity/talk2nature')
            self.assertTrue(check_site(root)['public'])
            page=(root/'research'/'fruit-bat-context-ml-2024'/'index.html').read_text()
        self.assertIn('A 2024 study already predicts bat interaction context with subject-independent folds',page)
        self.assertIn('not a novel benchmark by itself',page)
        self.assertIn('Keep this candidate deferred',page)
        self.assertIn('not message meaning or receiver comprehension',page)

    def test_phone_recording_review_is_bounded_and_visible_from_evidence_page(self):
        project_root=Path(__file__).resolve().parents[1]
        note=next(n for n in load('research') if n['slug']=='smartphone-bioacoustics-device-variability')
        self.assertEqual(len(note['review_request']['questions']),5)
        self.assertIn('no-animal reference test',note['review_request']['summary'])
        self.assertIn('no physical-device test is claimed',note['review_request']['status'])
        guide=(project_root/'docs'/'PHONE_RECORDING_REVIEW.md').read_text()
        self.assertIn('This is not an approved protocol',guide)
        self.assertIn('smartphone gain was not standardized',guide)
        self.assertIn('no independent specialist review has been received',guide)
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/Metivity/talk2nature')
            self.assertTrue(check_site(root)['public'])
            page=(root/'research'/'smartphone-bioacoustics-device-variability'/'index.html').read_text()
            self.assertIn('OPEN METHODS QUESTION',page)
            self.assertIn('Independent review of smartphone recording checks',page)
            self.assertIn('docs/PHONE_RECORDING_REVIEW.md',page)
            self.assertIn('scientific-review.yml',page)
            self.assertIn('/research/smartphone-bioacoustics-device-variability/',(root/'sitemap.xml').read_text())

    def test_nlnet_funding_page_links_current_scope_and_ai_policy_gates(self):
        opportunities=load('opportunities')
        sources={item['id']:item for item in load('sources')}
        codesupply=next(item for item in opportunities if item['slug']=='nlnet-codesupply')
        self.assertEqual(codesupply['status'],'Open · not recommended this cycle')
        self.assertEqual(codesupply['deadline'],'2026-11-03')
        self.assertEqual(codesupply['terms_source_id'],272)
        self.assertEqual(sources[codesupply['genai_policy_source_id']]['url'],'https://nlnet.nl/foundation/policies/generativeAI/2.0/')
        self.assertEqual(sources[codesupply['genai_policy_faq_source_id']]['url'],'https://nlnet.nl/foundation/policies/generativeAI/faq/')
        self.assertIn('not been inventoried',codesupply['next_action'])
        self.assertIn('no user-validated package-metadata work package',codesupply['next_action'])
        self.assertIn('strong European dimension',codesupply['next_action'])
        self.assertIn('No proposal has been drafted or submitted.',codesupply['next_action'])
        restack=next(item for item in opportunities if item['slug']=='nlnet-restack')
        self.assertNotIn('one million active human users',restack['fit'])
        self.assertEqual(restack['eligibility_source_id'],475)
        self.assertEqual(restack['horizon_country_source_id'],476)
        self.assertIn('strong European dimension',restack['fit'])
        self.assertIn('authored by the applicant in their own words',restack['next_action'])
        self.assertEqual(sources[restack['call_notice_source_id']]['url'],'https://nlnet.nl/news/2026/20261020-AI-policy.html')
        self.assertEqual(sources[restack['horizon_country_source_id']]['url'],'https://ec.europa.eu/info/funding-tenders/opportunities/docs/2021-2027/horizon/wp-call/2026-2027/wp-15-general-annexes_horizon-2026-2027_en.pdf')
        with tempfile.TemporaryDirectory() as d:
            build(Path(d))
            page=(Path(d)/'opportunities'/'index.html').read_text()
            self.assertIn('Official GenAI policy ↗',page)
            self.assertIn('https://nlnet.nl/foundation/policies/generativeAI/2.0/',page)
            self.assertIn('GenAI policy FAQ ↗',page)
            self.assertIn('not recommended this cycle',page)
            self.assertIn('Current application form ↗',page)
            self.assertIn('Horizon Europe country list ↗',page)

    def test_elfa_future_subgrant_is_labeled_as_planned_and_terms_pending(self):
        opportunities=load('opportunities')
        sources={item['id']:item for item in load('sources')}
        elfa=next(item for item in opportunities if item['slug']=='elfa-subgranting')
        self.assertIsNone(elfa['deadline'])
        self.assertEqual(elfa['opening_date'],'2027-01-01')
        self.assertIn('terms pending',elfa['status'])
        self.assertIn('Talk2Nature is eligible',elfa['fit'])
        self.assertIn('No contact',elfa['next_action'])
        self.assertEqual(sources[elfa['opening_source_id']]['url'],'https://elfaconsortium.eu/')
        self.assertEqual(sources[elfa['program_status_source_id']]['url'],'https://nlnet.nl/ELFA/')
        with tempfile.TemporaryDirectory() as d:
            build(Path(d))
            page=(Path(d)/'opportunities'/'index.html').read_text()
            self.assertIn('Expected opening <time datetime="2027-01-01">January 1, 2027</time>',page)
            self.assertIn('official opening notice',page)
            self.assertIn('Program operator update ↗',page)
            self.assertIn('terms and operator unverified',page)

    def test_ai_assistance_statement_is_published_and_linked_from_about(self):
        project_root=Path(__file__).resolve().parents[1]
        readme=(project_root/'README.md').read_text()
        contributing=(project_root/'CONTRIBUTING.md').read_text()
        self.assertIn('docs/AI_ASSISTANCE.md',readme)
        self.assertIn('docs/AI_ASSISTANCE.md',contributing)
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/Metivity/talk2nature')
            statement=(root/'about'/'ai-assistance'/'index.html').read_text()
            about=(root/'about'/'index.html').read_text()
            self.assertIn('<title>AI assistance and accountability at Talk2Nature · Talk2Nature</title>',statement)
            self.assertIn('<link rel="canonical" href="https://fixture.github.io/talk2nature/about/ai-assistance/">',statement)
            self.assertIn('<meta name="robots" content="index,follow">',statement)
            self.assertIn('Historical model, version and per-contribution records are incomplete',statement)
            self.assertIn('Human contributors remain responsible',statement)
            self.assertIn('https://nlnet.nl/foundation/policies/generativeAI/2.0/',statement)
            self.assertIn('https://nlnet.nl/foundation/policies/generativeAI/faq/',statement)
            self.assertIn('/talk2nature/opportunities/',statement)
            self.assertIn('/talk2nature/about/ai-assistance/',about)
            self.assertIn('/talk2nature/about/ai-assistance/',(root/'sitemap.xml').read_text())
            self.assertTrue(check_site(root)['public'])

    def test_local_preview_is_complete_and_noindex(self):
        with tempfile.TemporaryDirectory() as d:
            build(Path(d))
            result=check_site(d)
            self.assertFalse(result['public'])
            self.assertGreaterEqual(result['html_pages'],20)

    def test_reused_build_output_removes_stale_public_html_before_local_preview(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/fixture/talk2nature')
            stale=root/'research'/'retired-public-page'/'index.html'
            stale.parent.mkdir(parents=True)
            stale.write_text('<html><head><meta name="robots" content="index,follow"></head></html>')

            build(root)

            result=check_site(root)
            self.assertFalse(result['public'])
            self.assertFalse(stale.exists())

    def test_project_subpath_keeps_links_and_canonicals_intact(self):
        with tempfile.TemporaryDirectory() as d:
            build(Path(d),'https://fixture.github.io/talk2nature',True,'https://github.com/fixture/talk2nature')
            result=check_site(d)
            self.assertTrue(result['public'])
            self.assertEqual(result['reachable_public_pages'],result['html_pages']-1)
            self.assertIn('https://fixture.github.io/talk2nature/research/',(Path(d)/'sitemap.xml').read_text())

    def test_public_pages_require_unique_search_descriptions(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/fixture/talk2nature')
            self.assertTrue(check_site(root)['public'])
            home=(root/'index.html').read_text()
            match=re.search(r'<meta name="description" content="[^"]*">',home)
            self.assertIsNotNone(match)
            target=root/'about'/'index.html'
            page=target.read_text()
            page=re.sub(r'<meta name="description" content="[^"]*">',match.group(0),page,count=1)
            target.write_text(page)
            with self.assertRaisesRegex(ValueError,'Duplicate public meta descriptions'):
                check_site(root)

    def test_public_social_cards_use_shareable_png_and_complete_metadata(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/fixture/talk2nature')
            self.assertTrue(check_site(root)['public'])
            preview=(root/'assets'/'social.png').read_bytes()
            self.assertTrue(preview.startswith(b'\x89PNG\r\n\x1a\n'))
            self.assertEqual(int.from_bytes(preview[16:20],'big'),1200)
            self.assertEqual(int.from_bytes(preview[20:24],'big'),627)
            about=root/'about'/'index.html'
            page=about.read_text()
            self.assertIn('property="og:image:type" content="image/png"',page)
            self.assertIn('property="og:image:alt"',page)
            self.assertIn('name="twitter:card" content="summary_large_image"',page)
            self.assertIn('name="twitter:image" content="https://fixture.github.io/talk2nature/assets/social.png"',page)
            page=page.replace('<meta name="twitter:card" content="summary_large_image">','',1)
            about.write_text(page)
            with self.assertRaisesRegex(ValueError,'social preview requires exactly one non-empty twitter:card'):
                check_site(root)

    def test_public_structured_metadata_must_be_valid_json(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/fixture/talk2nature')
            target=root/'research'/'index.html'
            page=target.read_text()
            page=re.sub(r'(<script type="application/ld\+json">).*?(</script>)',r'\1{broken-json}\2',page,count=1)
            target.write_text(page)
            with self.assertRaisesRegex(ValueError,'invalid JSON-LD structured metadata'):
                check_site(root)

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

    def test_magpie_robin_review_keeps_paper_data_and_location_evidence_separate(self):
        project_root=Path(__file__).resolve().parents[1]
        note=next(n for n in load('research') if n['slug']=='oriental-magpie-robin-urban-noise-2025')
        self.assertEqual(note['source_ids'],[471,472,473])
        self.assertIn('Dryad abstract assigns a positive minimum-frequency/noise association',note['finding'])
        self.assertIn('paper Results report 27 and 30',note['finding'])
        self.assertEqual(note['atlas']['locations'][0]['place_id'],'kathmandu-valley-nepal')
        self.assertNotIn('27.7',json.dumps(note['atlas']))
        resources=json.loads((project_root/'research'/'resources.json').read_text())['resources']
        selected={r['id']:r for r in resources if r['id'].startswith('oriental-magpie-robin-')}
        self.assertEqual(set(selected),{
            'oriental-magpie-robin-urban-noise-paper-2025',
            'oriental-magpie-robin-vocalization-tables-dryad-v8',
        })
        self.assertEqual(selected['oriental-magpie-robin-urban-noise-paper-2025']['rights']['license'],'CC BY-NC-ND 4.0')
        dataset=selected['oriental-magpie-robin-vocalization-tables-dryad-v8']
        self.assertEqual(dataset['rights']['license'],'CC0-1.0')
        self.assertEqual(dataset['acquisition'],'metadata_only')
        self.assertEqual(dataset['files'],[])
        self.assertIn('not an audio dataset',dataset['decision'])

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
            self.assertIn('<title>Animal communication papers, datasets and methods · Talk2Nature</title>',page)
            self.assertIn('name="description" content="Browse papers, datasets, code, models and standards for reproducible research on animal communication, with review depth, limits and reuse-rights notes."',page)
            self.assertIn('rel="canonical" href="https://fixture.github.io/talk2nature/research/resources/"',page)
            self.assertIn('<meta name="robots" content="index,follow">',page)
            self.assertIn('Conditional; check the license, scope and stated conditions',page)
            self.assertIn('Unresolved; treat as not cleared.',page)
            self.assertIn('Not admitted for this project.',page)
            self.assertIn('Metadata only; no files are included in this public directory.',page)
            self.assertIn('A bounded sample path is approved by the collection rules',page)
            self.assertIn('<span class="resource-status">Metadata only</span>',page)
            self.assertIn('<span class="resource-status">Limited sample route</span>',page)
            self.assertIn('<option value="standard">Standard</option>',page)
            self.assertIn('<option value="project">Project</option>',page)
            self.assertIn('id="resource-research-use"',page)
            self.assertIn('<option value="conditional">Conditional</option>',page)
            self.assertIn('<option value="unresolved">Unresolved · not cleared</option>',page)
            self.assertIn('These are catalog notes, not permission.',page)
            self.assertIn('data-kind="standard"',page)
            self.assertIn('data-research-use="conditional"',page)
            self.assertIn('data-research-use="unresolved"',page)
            self.assertIn('Papers, datasets, code, models, standards and research projects',page)
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
            self.assertIn('does not explicitly establish',parrot_data['rights']['scope'])
            self.assertEqual(parrot_data['acquisition'],'metadata_only')
            self.assertEqual(parrot_data['analysis_admission'],'not_admitted')
            self.assertEqual(parrot_data['files'],[])
            self.assertEqual(parrot_data['rights']['research_use'],'unresolved')
            self.assertEqual(parrot_data['rights']['commercial_use'],'not_admitted')
            self.assertEqual(parrot_data['rights']['redistribution'],'not_admitted')
            self.assertIn(html.escape(parrot_data['rights']['scope']),page)
            self.assertIn(html.escape(parrot_data['limitations']),page)
            figshare=next(r for r in resources if r['id']=='monk-parakeet-identity-figshare-2023')
            self.assertIn(f'<h2><a href="{figshare["landing_url"]}" rel="external noopener">{html.escape(figshare["title"])}',page)
            self.assertNotIn(f'<h2><a href="{figshare["url"]}" rel="external noopener">{html.escape(figshare["title"])}',page)
            research_index=(root/'research/index.html').read_text()
            self.assertIn('/talk2nature/research/resources/',research_index)
            self.assertIn('https://fixture.github.io/talk2nature/research/resources/',(root/'sitemap.xml').read_text())

    def test_moth_note_reports_aggregate_check_and_keeps_unmapped_bat_condition_out(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/Metivity/talk2nature')
            note=root/'research/moths-and-plants/index.html'
            page=note.read_text()
            self.assertIn('Note reviewed 2026-10-28',page)
            self.assertIn('matched the five main Table 1 tuples',page)
            self.assertIn('not a statistical-model reproduction',page)
            self.assertIn('workbook contains a lower-rate 2-click/min condition and a Bat label outside the reported Table 1 oviposition outcomes',page)
            self.assertIn('separate flight-response check of hearing after deafening',page)
            self.assertIn('The Methods mention the 2-click/min repeat, but Table 1 has no outcome row for it.',page)
            self.assertIn('The article does not map the workbook&#x27;s Bat egg-cluster label to that check; keep the row excluded.',page)
            self.assertIn('Although one workbook was checksum-verified and parsed, this does not verify the remaining files',page)
            self.assertNotIn('data/external/',page)

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

    def test_el_silencio_stays_a_metadata_only_detection_candidate(self):
        project_root=Path(__file__).resolve().parents[1]
        note=next(n for n in load('research') if n['slug']=='el-silencio-multitaxon-dataset-2025')
        self.assertEqual(note['source_ids'],[328,329,330,331,332,439])
        self.assertIn('not a communication or meaning benchmark',note['finding'])
        self.assertIn('no more than one second',note['finding'])
        self.assertIn('separate sound-identification task',note['finding'])
        self.assertIn('No inter-annotator reliability statistic',note['limitations'])
        self.assertIn('protocol',note['study_snapshot'][3][1].lower())
        self.assertIn('11,340',note['limitations'])
        self.assertIn('10,980',note['limitations'])
        self.assertIn('3,546,609,904 bytes',note['limitations'])
        self.assertEqual(note['atlas']['location_status'],'mapped')
        self.assertEqual(note['atlas']['locations'][0]['place_id'],'colombia-country')
        self.assertEqual(note['atlas']['locations'][0]['role'],'study_region')
        self.assertIn('country-scale',note['atlas']['location_note'])

        resources={r['id']:r for r in json.loads((project_root/'research/resources.json').read_text())['resources']}
        ids={'elsilencio-birdclefplus-overview-2025','elsilencio-labeled-audio-v1','elsilencio-unlabeled-soundscapes-2025'}
        self.assertEqual({key for key in resources if key.startswith('elsilencio-')},ids)
        for key in ids:
            self.assertEqual(resources[key]['acquisition'],'metadata_only')
            self.assertEqual(resources[key]['files'],[])
        labeled=resources['elsilencio-labeled-audio-v1']
        self.assertIn('CC BY 4.0',labeled['rights']['license'])
        self.assertIn('not independently establish source-recording rights',labeled['rights']['scope'])
        self.assertEqual(resources['elsilencio-unlabeled-soundscapes-2025']['version'],
                         'DOI 10.5281/zenodo.17122738; published 2025-09-15')
        paper=resources['elsilencio-birdclefplus-overview-2025']
        self.assertEqual(paper['rights']['license'].split()[0:3],['CC','BY','4.0'])
        self.assertEqual(paper['rights']['research_use'],'conditional')
        self.assertIn('excluded from the public website',paper['access'])
        self.assertIn(332,labeled['source_ids'])

        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/Metivity/talk2nature')
            self.assertTrue(check_site(root)['public'])
            page=(root/'research/el-silencio-multitaxon-dataset-2025/index.html').read_text()
            self.assertIn('do not supply independently observed behavior',page)
            self.assertIn('https://zenodo.org/records/17064353',page)
            self.assertIn('https://zenodo.org/records/17122738',page)
            self.assertIn('https://raw.githubusercontent.com/redecoacustica/elsilencio-dataset/5e2f7826c908fec3018740068bbdeda6c6977f35/Protocol.pdf',page)
            self.assertIn('separate task and dataset',page)
            self.assertIn('no more than one second',page)
            self.assertIn('content=\"index,follow\"',page)
            self.assertIn('https://fixture.github.io/talk2nature/research/el-silencio-multitaxon-dataset-2025/',page)
            self.assertIn('/talk2nature/research/el-silencio-multitaxon-dataset-2025/',(root/'sitemap.xml').read_text())
            reading=(root/'research/starting-points/index.html').read_text()
            self.assertIn('el-silencio-multitaxon-dataset-2025',reading)
            atlas=json.loads((root/'research/atlas/catalog.json').read_text())
            mapped=next(r for r in atlas['records'] if r['id']==note['slug'])
            self.assertEqual(mapped['location_status'],'mapped')
            self.assertEqual(mapped['locations'][0]['place_id'],'colombia-country')
            self.assertEqual(mapped['locations'][0]['role'],'study_region')

    def test_budgerigar_playback_note_bounds_trained_vocal_output(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/Metivity/talk2nature')
            self.assertTrue(check_site(root)['public'])
            page=(root/'research/budgerigar-playback-context/index.html').read_text()
            self.assertIn('Five individually housed budgerigars',page)
            self.assertIn('conditioned vocal output',page)
            self.assertIn('not evidence that an app can talk to or translate a parrot',page)
            self.assertIn('Keep playback out of the public app',page)
            self.assertIn('Published online 2015; issue 2016',page)
            self.assertIn('index,follow',page)
            self.assertIn('https://fixture.github.io/talk2nature/research/budgerigar-playback-context/',page)
            self.assertIn('https://pmc.ncbi.nlm.nih.gov/articles/PMC4696898/',page)
            note=next(n for n in load('research') if n['slug']=='budgerigar-playback-context')
            self.assertEqual(note['source_ids'],[312])
            resources=json.loads((Path(__file__).parents[1]/'research/resources.json').read_text())['resources']
            resource=next(r for r in resources if r['id']=='budgerigar-conditioned-vocal-output-seki-dooling-2016')
            self.assertEqual(resource['acquisition'],'metadata_only')
            self.assertEqual(resource['rights']['research_use'],'unresolved')
            self.assertEqual(resource['rights']['redistribution'],'unresolved')

    def test_budgerigar_dataset_mapping_stays_separate_from_sample_identity(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/Metivity/talk2nature')
            note=(root/'research/budgerigar-starting-point/index.html').read_text()
            catalog=(root/'research/resources/index.html').read_text()
            self.assertIn('Figure 2 data in ColonyNoiseCalls',note)
            self.assertIn('Figures 3–5 data in acoustiSAT_MAO.mat',note)
            self.assertIn('no verified mapping to a specific bird, session or condition',note)
            self.assertIn('44,101 value remains unexplained',note)
            self.assertIn('https://data.mendeley.com/api/docs/',note)
            self.assertIn('HTTP 401',catalog)
            self.assertIn('no current file manifest',catalog)
            self.assertIn('No training, model evaluation or public audio publication',catalog)

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

    def test_budgerigar_dataset_note_preserves_session_and_alignment_limits(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/Metivity/talk2nature')
            self.assertTrue(check_site(root)['public'])
            html=(root/'research/budgerigar-vocal-sociality-data/index.html').read_text()
            self.assertIn('newly formed experimental flocks, not home flocks',html)
            self.assertIn('separate 80-minute sessions',html)
            self.assertIn('no original call WAV files',html)
            self.assertIn('no original call WAV files or shared call/event timestamps',html)
            canonical='https://fixture.github.io/talk2nature/research/budgerigar-vocal-sociality-data/'
            self.assertIn(canonical,html)
            self.assertIn(canonical,(root/'sitemap.xml').read_text())
            resource=next(r for r in json.loads((Path(__file__).parents[1]/'research/resources.json').read_text())['resources'] if r['id']=='budgerigar-vocal-social-dryad')
            self.assertEqual(resource['acquisition'],'metadata_only')

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

    def test_openwhistle_source_ids_link_to_its_pinned_repository_records(self):
        project_root=Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/Metivity/talk2nature')
            self.assertTrue(check_site(root)['public'])
            page=(root/'research/openwhistle-dolphin-benchmark/index.html').read_text()
            sources=json.loads((project_root/'content/sources.json').read_text())
            by_id={source['id']:source for source in sources}
            readme='https://github.com/sumbre-lab/OpenWhistle/blob/ad715bb3cf24c36f85b3c3c8159077548134a39e/README.md'
            data_license='https://github.com/sumbre-lab/OpenWhistle/blob/ad715bb3cf24c36f85b3c3c8159077548134a39e/LICENSE-DATA'
            project_page='https://sumbre-lab.github.io/openwhistle/'
            self.assertEqual(by_id[390]['title'],'Rüttimann et al., multimodal BirdPark system for songbird behavior')
            self.assertEqual(by_id[411]['url'],readme)
            self.assertEqual(by_id[412]['url'],data_license)
            self.assertEqual(by_id[495]['url'],project_page)
            self.assertEqual(by_id[425]['url'],'https://www.geonames.org/295277/eilat.html')
            self.assertIn(readme,page)
            self.assertIn(data_license,page)
            self.assertIn(project_page,page)
            self.assertIn('www.geonames.org/295277/eilat.html',page)
            self.assertIn('voluntary',page)
            self.assertIn('NeurIPS 2026',page)
            self.assertIn('64.37 ± 2.67 full-set ten-type macro-F1',page)
            self.assertIn('81.1 ± 1.8% accuracy',page)
            self.assertIn('not interchangeable',page)
            self.assertNotIn('https://doi.org/10.7717/peerj.20203',page)
            resources=json.loads((project_root/'research/resources.json').read_text())['resources']
            by_resource={resource['id']:resource for resource in resources}
            self.assertEqual(by_resource['birdpark-multimodal-songbird-paper-2025']['source_ids'],[390])
            self.assertEqual(by_resource['openwhistle-pretraining-audio']['source_ids'],[341,412])
            self.assertEqual(by_resource['openwhistle-classification-dataset']['source_ids'],[342,412])
            self.assertEqual(by_resource['openwhistle-code']['source_ids'],[411])
            self.assertEqual(by_resource['openwhistle-project-benchmark-page']['source_ids'],[495])
            self.assertEqual(by_resource['openwhistle-project-benchmark-page']['acquisition'],'metadata_only')

    def test_first_animal_page_distinguishes_dataset_interaction_and_phone_paths(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/Metivity/talk2nature')
            self.assertTrue(check_site(root)['public'])
            page=(root/'research/first-animal/index.html').read_text()
            self.assertIn('109,963 songs',page)
            self.assertIn('2025 study already used deep metric learning',page)
            self.assertIn('original roughly 9 TB of continuous soundscapes are not included',page)
            self.assertIn('precise British National Grid nestbox coordinates in two tables',page)
            self.assertIn('We have not inspected coordinate values or acquired data files',page)
            self.assertIn('One question.',page)
            self.assertIn('Choose what you want to do first',page)
            self.assertNotIn('Quick answer',page)
            self.assertIn('Use the phone app with a pet',page)
            self.assertIn('Practice on a large sound library',page)
            self.assertIn('Study a signal and its receivers',page)
            self.assertIn('href="#budgerigars"',page)
            self.assertIn('href="#wytham-great-tit"',page)
            self.assertIn('href="#honeybee-signal"',page)
            self.assertIn('<section id="budgerigars">',page)
            self.assertIn('<section id="wytham-great-tit">',page)
            self.assertIn('<section id="honeybee-signal">',page)
            self.assertIn('FIRST_DATASET_REVIEW_PACKET.md',page)
            self.assertIn('submit a methods critique',page)
            self.assertIn('No recordings or private data are requested',page)
            self.assertIn('No Talk2Nature benchmark is selected or ready for training',page)
            self.assertIn('Compare household-animal data and app fit',page)
            self.assertIn('/talk2nature/research/companion-animal-cohort-evidence-2026/',page)
            self.assertIn('A 2025 study tested 12 adult finches on 11 researcher-defined call types',page)
            self.assertIn('archive described as 3,433 recordings',page)
            self.assertIn('The closest reviewed lead for studying turn-taking',page)
            self.assertIn('<details class="animal-detail">',page)
            self.assertNotIn('<details class="animal-detail" open',page)
            self.assertIn('conflicting CC BY-SA and CC BY-NC declarations',page)
            self.assertIn('95.6% of examples',page)
            self.assertIn('Budgerigars',page)
            self.assertIn('can a model reproduce expert-marked song-note boundaries',page)
            self.assertIn('index,follow',page)
            self.assertIn('https://fixture.github.io/talk2nature/research/first-animal/',page)
            self.assertIn('/talk2nature/research/wytham-great-tit-song-structure-2024/',page)
            self.assertIn('/talk2nature/research/zebra-finch-call-classifier-multitask-2026/',page)
            self.assertIn('/talk2nature/research/zebra-finch-call-categories-2025/',page)
            self.assertIn('https://github.com/Metivity/talk2nature/blob/main/docs/ZEBRA_FINCH_PERCEPTION_REVIEW.md',page)
            self.assertIn('https://github.com/Metivity/talk2nature/issues/new?template=scientific-review.yml',page)
            self.assertIn('Please do not attach recordings or private data.',page)
            self.assertIn('/talk2nature/research/zf-aim-zebra-finch-turn-taking-2026/',page)
            self.assertIn('https://fixture.github.io/talk2nature/research/first-animal/',(root/'sitemap.xml').read_text())
            self.assertIn('OpenWhistle dolphins: whistle types',(root/'research/first-animal/index.html').read_text())
            self.assertIn('official repository declares CC BY 4.0 for its datasets',page)
            self.assertIn('the Wav2Vec model license is unspecified',page)
            self.assertIn('Honeybee waggle dances',page)
            self.assertIn('more than 46 million 2019 track detections',page)
            self.assertIn('/talk2nature/research/honeybee-dance-following-2023/',page)
            honeybee=(root/'research'/'honeybee-dance-following-2023'/'index.html').read_text()
            self.assertIn('3,278,121 detections',honeybee)
            self.assertIn('hour rather than holding out bees or colonies',honeybee)
            self.assertIn('No data, video, code or model was downloaded',honeybee)
            self.assertIn('4,870,358,178 bytes',honeybee)
            self.assertIn('9,171,824 bytes, above the current 5 MiB per-file collector cap',honeybee)
            resources=json.loads((Path(__file__).resolve().parents[1]/'research'/'resources.json').read_text())['resources']
            honeybee_data=next(row for row in resources if row['id']=='honeybee-dance-following-data-2023')
            self.assertEqual(honeybee_data['acquisition'],'metadata_only')
            self.assertEqual(honeybee_data['files'],[])
            self.assertIn('4,870,358,178 bytes',honeybee_data['access'])
            self.assertIn('9,171,824 bytes',honeybee_data['access'])
            self.assertIn('CC BY 4.0',honeybee_data['rights']['license'])
            self.assertEqual(honeybee_data['source_ids'],[415,416])
            resources=json.loads((Path(__file__).parents[1]/'research/resources.json').read_text())['resources']
            by_id={resource['id']:resource for resource in resources}
            self.assertEqual(by_id['openwhistle-classification-dataset']['rights']['license'],'CC-BY-4.0')
            self.assertEqual(by_id['openwhistle-classification-dataset']['acquisition'],'metadata_only')
            self.assertEqual(by_id['openwhistle-wav2vec-model']['rights']['research_use'],'unresolved')
            self.assertEqual(by_id['openwhistle-code']['rights']['research_use'],'unresolved')

    def test_parrotlet_dryad_policy_is_linked_and_archive_stays_unadmitted(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/Metivity/talk2nature')
            page=(root/'research'/'parrotlet-vocal-babbling-development'/'index.html').read_text()
            self.assertIn('https://datadryad.org/publication_policy',page)
            self.assertIn('accepted datasets are published under CC0',page)
            self.assertIn('does not verify scientific validity',page)
            self.assertIn('HTTP 403',page)
            resource=next(r for r in json.loads((Path(__file__).parents[1]/'research/resources.json').read_text())['resources'] if r['id']=='parrotlet-vocal-babbling-data')
            self.assertEqual(resource['acquisition'],'metadata_only')
            self.assertEqual(resource['files'],[])

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
            self.assertIn('fileAccessRequest=true',rendered)
            self.assertIn('file is marked restricted=false',rendered)
            self.assertIn('the flag is ignored for unrestricted files',rendered)
            self.assertIn('does not separately explain the external-downloader scope',rendered)
            self.assertIn('https://guides.dataverse.org/en/6.11/api/native-api.html#restrict-files',rendered)
            self.assertIn('https://www.edmond.mpg.de/Terms_of_Use/',rendered)
            self.assertIn('index,follow',rendered)
            canonical=base+'/research/animal-spot-parrot-detection-2022/'
            self.assertIn(canonical,rendered)
            self.assertIn(canonical,(root/'sitemap.xml').read_text())
            note=next(n for n in load('research') if n['slug']=='animal-spot-parrot-detection-2022')
            self.assertIn(225,note['source_ids'])
            resources=json.loads((Path(__file__).resolve().parents[1]/'research'/'resources.json').read_text())['resources']
            data=next(r for r in resources if r['id']=='animal-spot-monk-parakeet-data-2022')
            self.assertEqual(data['acquisition'],'metadata_only')
            self.assertEqual(data['files'],[])
            self.assertIn(352,data['source_ids'])
            self.assertIn('ignored when unrestricted',data['access'])
            self.assertIn('No terms were accepted',data['access'])

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
            self.assertIn('Response Time(s) is an interval between consecutive call onsets, not a verified behavioral reply',html)
            self.assertIn('does not establish that one bird behaviorally answered another',html)
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
            self.assertIn('significant pre-induction power-spectral-density difference',html)
            self.assertIn('1,604.752%',html)
            self.assertIn('p=.327',html)
            self.assertIn('p=.391',html)
            self.assertIn('p=.580',html)
            self.assertIn('p=.116',html)
            self.assertIn('24 fungal electrode-pair records',html)
            self.assertIn('8 non-inoculated control records',html)
            self.assertIn('no contrast is statistically significant',html)
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
            self.assertIn('no account to try',university)
            self.assertIn('university-access-note',university)
            self.assertIn('href="https://github.com/Metivity/talk2nature/issues/new?template=first-use.yml">Share a short note',university)
            self.assertIn('One sentence is enough; device details are optional.',university)
            self.assertIn('href="https://github.com/Metivity/talk2nature/issues/new?template=reproduction.yml">use the workflow report',university)
            self.assertIn('Posting requires GitHub sign-in',university)
            self.assertIn('reports are public',university)
            self.assertIn('href="/talk2nature/app/compare/"',university)
            self.assertIn('href="/talk2nature/tools/interop/"',university)
            self.assertIn('Start the browser review',university)
            self.assertIn('Optional: test the Audacity handoff',university)
            self.assertIn('Neither tests what an animal means',university)
            self.assertIn('No Talk2Nature animal-communication model',university)
            self.assertIn('without permission',university)
            self.assertIn('id="evaluation-boundary"',university)
            self.assertEqual(university.count('<details class="university-disclosure">'),2)
            self.assertNotIn('<details class="university-disclosure" open',university)
            self.assertIn('Optional: review a scientific claim',university)
            self.assertIn('Four bounded research and measurement questions',university)
            self.assertIn('Optional: explore the recording-network idea',university)
            self.assertLess(university.index('id="evaluation-boundary"'),university.index('id="scientific-review"'))
            self.assertLess(university.index('class="section university-next"'),university.index('id="scientific-review"'))
            self.assertIn('id="recording-network"',university)
            self.assertIn('no Talk2Nature upload or shared recording server',university)
            self.assertIn('That last design is a proposal, not a service.',university)
            self.assertIn('NETWORK_AND_OUTREACH.md',university)
            self.assertIn('OPEN METHODS REVIEWS',university)
            self.assertIn('Researchers can review animal receiver-response evidence',university)
            self.assertIn('What do the cited receiver-response experiments support',university)
            self.assertIn('href="/talk2nature/research/bird-call-syntax/"',university)
            self.assertIn('phone and app-path variability',university)
            self.assertIn('href="/talk2nature/research/smartphone-bioacoustics-device-variability/"',university)
            self.assertIn('docs/PHONE_RECORDING_REVIEW.md',university)
            self.assertIn('bee-held-out analysis add useful evidence',university)
            self.assertIn('two-season, single-site study',university)
            self.assertIn('href="/talk2nature/research/honeybee-dance-following-2023/"',university)
            self.assertIn('docs/FIRST_DATASET_REVIEW_PACKET.md',university)
            self.assertIn('female Egyptian cotton leafworms using drought-associated plant ultrasound as a cue',university)
            self.assertIn('measured seedling-tray rate',university)
            self.assertIn('not a signal evolved to communicate',university)
            self.assertIn('href="/talk2nature/research/moths-and-plants/"',university)
            self.assertIn('https://elifesciences.org/articles/104700/peer-reviews',university)
            self.assertIn('Any submitted review is a public GitHub issue',university)
            self.assertIn('template=scientific-review.yml',university)
            self.assertIn('This is a literature critique, not a request to plan or conduct playback',university)
            self.assertNotIn('blob/main/docs/UNIVERSITY_EVALUATION.md',university)
            self.assertTrue((root/'assets/university.css').is_file())
            self.assertIn('.university-access-note{',(root/'assets/university.css').read_text())
            project_root=Path(__file__).resolve().parents[1]
            brief=(project_root/'docs/UNIVERSITY_EVALUATION.md').read_text()
            first_use_form=(project_root/'.github'/'ISSUE_TEMPLATE'/'first-use.yml').read_text()
            self.assertIn('One short sentence is enough',first_use_form)
            self.assertIn('submitting here requires GitHub sign-in',first_use_form)
            self.assertIn('This public report is about the software workflow',first_use_form)
            self.assertIn('Device and browser details are optional.',brief)
            self.assertIn('not a partnership announcement',brief)
            self.assertIn('not an ethics determination',brief)
            self.assertIn('plant–insect sensory ecology',brief)
            self.assertIn('no data, audio, playback or experiment is requested',brief)
            self.assertIn('There is no shared Talk2Nature recording network or university cloud workspace today.',brief)
            network=(project_root/'docs/NETWORK_AND_OUTREACH.md').read_text()
            self.assertIn('This is enough for a software/workflow review, not for a field study.',network)
            self.assertIn('Keep raw audio at the institution by default.',network)
            self.assertIn('No message has been sent by this plan.',network)
            self.assertIn('Candidate reviewer paths checked October 23, 2026',network)
            self.assertIn('not prospects who have expressed interest',network)
            self.assertIn('https://www.birds.cornell.edu/ccb/bioacoustalks/',network)
            self.assertIn('https://www.st-andrews.ac.uk/biology/people/vj/',network)
            self.assertIn('no registration or proposal has been made',network)
            status=(project_root/'docs/STATUS.md').read_text()
            status_history=(project_root/'docs/STATUS_HISTORY.md').read_text()
            self.assertIn('[STATUS_HISTORY.md](STATUS_HISTORY.md)',status)
            self.assertIn('source-checked international reviewer paths',status+status_history)
            self.assertIn('no group is a prospect, partner or endorser',status+status_history)
            self.assertIn('browser-only comparison of two invented observation sessions',brief)
            self.assertIn('Posting requires GitHub sign-in, and the issue is public',brief)
            self.assertIn('https://metivity.github.io/talk2nature/app/compare/',brief)
            self.assertIn('Posting requires GitHub sign-in, and the issue is public',brief)
            self.assertIn('optional, deeper Listen-to-Audacity check',brief)
            self.assertIn('no-animal phone-reference check',brief)
            self.assertIn('PHONE_RECORDING_REVIEW.md',brief)
            self.assertNotIn('try a short synthetic Listen-to-Audacity workflow',brief)
            self.assertIn('SUPPORT.md', (project_root/'README.md').read_text())
            researcher_kit=(project_root/'docs/RESEARCHER_START.md').read_text()
            self.assertIn('one sentence is enough and device details are optional',researcher_kit)
            self.assertIn('Posting requires GitHub sign-in and creates a public issue.',researcher_kit)

    def test_public_build_requires_real_origin(self):
        with tempfile.TemporaryDirectory() as d:
            for origin in ('','http://localhost:4173','https://example.com','https://good.test/?a=b','https://user:secret@good.test'):
                with self.subTest(origin=origin),self.assertRaises(ValueError): build(Path(d),origin,True)

    def test_funding_deadlines_show_fresh_check_and_official_cutoff_source(self):
        opportunities=load('opportunities')
        sources={source['id']:source for source in load('sources')}
        preseed=next(item for item in opportunities if item['slug']=='preseed')
        self.assertEqual(preseed['type'],'Pre-Seed co-investment grant')
        self.assertEqual(preseed['verified'],'2026-10-27')
        self.assertEqual(sources[27]['checked'],'2026-10-27')
        self.assertIn('no-go for this call at the project\'s documented readiness',preseed['next_action'])
        for requirement in ('NIS 3 million','NIS 300,000','at least 15%','at least 75%'):
            self.assertIn(requirement,preseed['next_action'])
        self.assertIn('not documented',preseed['fit'])
        self.assertIn('index lists Pre-Seed',preseed['next_action'])
        self.assertIn('Annex 6 to Track 1',preseed['next_action'])
        self.assertIn('written IIA confirmation',preseed['next_action'])
        coller=next(item for item in opportunities if item['slug']=='coller-dolittle')
        self.assertEqual(coller['verified'],'2026-10-28')
        self.assertEqual(coller['deadline_source_id'],25)
        self.assertEqual(coller['conflicting_date_source_id'],19)
        self.assertEqual(coller['application_status'],'No public result posted')
        self.assertIn('Both dates have passed',coller['next_action'])
        self.assertIn('Neither page describes late handling',coller['next_action'])
        self.assertEqual(sources[19]['checked'],'2026-10-28')
        self.assertEqual(sources[25]['checked'],'2026-10-28')
        trebek=next(item for item in opportunities if item['slug']=='natgeo-trebek-2026')
        self.assertEqual(trebek['name'],'National Geographic Society · 2027 Trebek Initiative RFP')
        self.assertEqual(trebek['verified'],'2026-10-25')
        self.assertEqual(trebek['portal_source_id'],451)
        self.assertIn('No-go this cycle',trebek['status'])
        self.assertIn('no Canada-specific workstream',trebek['fit'])
        self.assertIn('no readable RFP terms',trebek['next_action'])
        self.assertEqual(sources[451]['url'],'https://funding.nationalgeographic.org/s/fundingopportunity/119Hr000000CohhIAC/2027-trebek-initiative-rfp')
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True)
            self.assertTrue(check_site(root)['public'])
            page=(root/'opportunities/index.html').read_text()
            self.assertEqual(sum(source['id']==121 for source in load('sources')),1)
            self.assertIn('Deadline <time datetime="2026-10-08">October 8, 2026</time> · 12:00',page)
            self.assertIn('No public result posted',page)
            self.assertIn('September 30, 2026 by noon CET',page)
            self.assertIn('August 30',page)
            self.assertIn('official date details',page)
            self.assertIn('Checked 2026-10-28 · Not submitted; not recommended for current scope and readiness',page)
            self.assertIn('not documented',page)
            self.assertIn('no-go at documented readiness',page)
            self.assertIn('Deadline <time datetime="2026-11-09">November 9, 2026</time> · 12:00 Israel time',page)
            self.assertIn('Pre-Seed co-investment grant',page)
            self.assertIn('60% of an eligible Pre-Seed investment round, up to a NIS 2 million grant',page)
            self.assertIn('NIS 3 million',page)
            self.assertIn('NIS 300,000',page)
            self.assertIn('at least 15%',page)
            self.assertIn('at least 75%',page)
            self.assertIn('Checked 2026-10-27 · Not submitted · no-go at current documented readiness',page)
            self.assertIn('Official track rules ↗',page)
            self.assertIn('Official open-source procedure ↗',page)
            self.assertIn('Track 7 applicability and treatment',page)
            self.assertIn('2027 Trebek Initiative RFP',page)
            self.assertIn('No-go this cycle · Canada-focused project scope not established',page)
            self.assertIn('The linked RFP-specific terms were not accessible in this review.',page)
            self.assertIn('funding.nationalgeographic.org/s/fundingopportunity/119Hr000000CohhIAC/2027-trebek-initiative-rfp',page)
            os4ls=next(item for item in opportunities if item['slug']=='os4science-os4ls-2026')
            self.assertEqual(os4ls['deadline'],'2026-07-21')
            self.assertEqual(os4ls['status'],'2026 call closed · future cycle not announced')
            self.assertEqual(sources[os4ls['source_id']]['url'],'https://os4science.org/apply-for-funding/')
            self.assertEqual(sources[os4ls['terms_source_id']]['url'],'https://os4science.org/funding_opportunity/os4ls/')
            self.assertIn('early-stage prototypes',os4ls['fit'])
            self.assertIn('hosting repositories or databases',os4ls['fit'])
            self.assertIn('makes no grants to individuals',os4ls['next_action'])
            self.assertIn('no later call',os4ls['next_action'])
            self.assertIn('Open Source for the Life Sciences (2026)',page)
            self.assertIn('2026 call closed · future cycle not announced',page)
            experiment=next(item for item in opportunities if item['slug']=='experiment')
            self.assertEqual(experiment['verified'],'2026-10-24')
            self.assertEqual(experiment['eligibility_source_id'],409)
            self.assertEqual(experiment['payout_source_id'],410)
            self.assertIn('all-or-nothing funding',page)
            self.assertIn('country-specific payout confirmation',page)
            self.assertIn('These official pages differ',page)
            self.assertIn('launched campaigns cannot be deleted',page)
            self.assertIn('Payout and fees ↗',page)
            self.assertIn('https://experiment.com/faq',page)
            self.assertIn('https://experiment.com/guide/extra',page)
            self.assertIn('Wildlife Acoustics · Q4 Scientific Product Grant',page)
            self.assertIn('Deadline <time datetime="2026-11-15">November 15, 2026</time>',page)
            self.assertIn('up to $4,000 per applicant from a quarterly pool of up to $12,000',page)
            self.assertIn('charitable/educational tax-exempt status documentation',page)
            self.assertIn('do not prepare an application now',page)
            self.assertIn('https://innovationisrael.org.il/wp-content/uploads/2024/06/%D7%9E%D7%A1%D7%9C%D7%95%D7%9C-%D7%94%D7%98%D7%91%D7%94-%D7%9E%D7%A1-7-%D7%A7%D7%A8%D7%9F-%D7%94%D7%94%D7%96%D7%A0%D7%A7-15.07.2026.pdf',page)
            self.assertIn('https://innovationisrael.org.il/rules/%D7%A0%D7%95%D7%94%D7%9C-%D7%A7%D7%95%D7%93-%D7%A4%D7%AA%D7%95%D7%97/',page)
            self.assertIn('Deadline <time datetime="2026-11-03">November 3, 2026</time> · 12:00 CET',page)
            self.assertIn('current program page does not state the previously recorded one-million-user AI exception',page)
            self.assertIn('software supply-chain metadata',page)
            self.assertIn('Open · not recommended this cycle',page)
            self.assertIn('Horizon Europe country list ↗',page)
            self.assertIn('Applicant eligibility ↗',page)
            self.assertIn('Official GenAI policy ↗',page)
            self.assertIn('Current call and policy notice ↗',page)
            self.assertIn('Current application form ↗',page)
            self.assertIn('Expected opening <time datetime="2027-01-01">January 1, 2027</time>',page)
            self.assertIn('Deadline <time datetime="2026-12-17">December 17, 2026</time> · 11:59 PM PST (UTC−8)',page)
            self.assertIn('Deadline <time datetime="2026-11-20">November 20, 2026</time> · 11:59 PM PST (UTC−8)',page)
            self.assertIn('Planned · expected opening <time datetime="2027-01-01">January 1, 2027</time>; terms pending',page)
            self.assertIn('Open through <time datetime="2026-11-03">November 3, 2026</time> · not recommended for current scope/policy readiness',page)
            self.assertIn('Program operator update ↗',page)
            for source_id in (150,151,152,154,155,158,159,272,273,274):
                self.assertEqual(sum(source['id']==source_id for source in load('sources')),1)

    def test_biodivfuture_call_links_rules_and_discloses_deadline_conflict(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/Metivity/talk2nature')
            self.assertTrue(check_site(root)['public'])
            page=(root/'opportunities/index.html').read_text()
            self.assertIn('Biodiversa+ · BiodivFuture 2026–2027',page)
            self.assertIn('Deadline <time datetime="2026-11-10">November 10, 2026</time> · 12:00 CET · 11:00 UTC',page)
            self.assertIn('Israel national deadline <time datetime="2026-11-15">November 15, 2026</time> · 12:00 local (MoEP tender listing)',page)
            self.assertIn('TAU internal deadline (TAU applicants only) <time datetime="2026-11-03">November 3, 2026</time>',page)
            self.assertIn('now-accessible Commission listing says November 2, 2026 and Open',page)
            self.assertIn('official date conflict is unresolved',page)
            self.assertIn('Talk2Nature-led application remains a no-go',page)
            self.assertIn('National funding rules ↗',page)
            self.assertIn('Call partner search ↗',page)
            self.assertIn('Other official listing (date differs) ↗',page)
            self.assertIn('Israel Science Foundation-recognized host',page)
            self.assertIn('Israeli national call ↗',page)
            self.assertIn('MoEP applicant briefing ↗',page)
            self.assertIn('Institution-specific calendar ↗',page)
            self.assertIn('separate EPSS and Ministry submissions',page)
            self.assertIn('No application, partner profile or outreach is prepared',page)
            for source_id in (181,182,183,184,185,309,310,311,435):
                self.assertEqual(sum(source['id']==source_id for source in load('sources')),1)
            for source_url in (
                'https://www.biodiversa.eu/wp-content/uploads/2026/10/BiodivFuture_Funding-Organisation_Rules_V5_06-10-2026.pdf',
                'https://mr.gov.il/ilgstorefront/he/p/4000621848',
                'https://www.biodiversa.eu/wp-content/uploads/2026/10/BiodivFuture-MoEP-slides.pdf',
                'https://research-authority.tau.ac.il/grants/10193',
            ):
                self.assertIn(f'href="{source_url}"',page)

    def test_kunming_biodiversity_fund_shows_un_only_funding_and_country_gates(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True)
            self.assertTrue(check_site(root)['public'])
            page=(root/'opportunities/index.html').read_text()
            self.assertIn('UNEP · Kunming Biodiversity Fund 2026 Call',page)
            self.assertIn('Deadline <time datetime="2026-11-15">November 15, 2026</time> · 23:59 on deadline date; timezone not stated in the guideline',page)
            self.assertIn('Funds go directly only to UN agencies',page)
            self.assertIn('developing-country, NBSAP-aligned project',page)
            self.assertIn('CBD focal-point or Lead Ministry endorsement',page)
            self.assertIn('Not a standalone grant for Talk2Nature',page)
            self.assertIn('No country project, UN partner, field evidence, or sub-partner request is confirmed',page)
            self.assertIn('No application or outreach is prepared',page)
            self.assertIn('official date details',page)
            self.assertIn('Official program ↗',page)
            self.assertIn('Official track rules ↗',page)
            for source_id in (304,305):
                self.assertEqual(sum(source['id']==source_id for source in load('sources')),1)

    def test_horizon_biodiversity_monitoring_call_states_policy_fit_and_consortium_gates(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True)
            page=(root/'opportunities/index.html').read_text()
            self.assertIn('Horizon Europe · HORIZON-NATURE-2027-02-05: Cost-effective biodiversity monitoring',page)
            self.assertIn('HORIZON-NATURE-2027-02-05',page)
            self.assertIn('Deadline <time datetime="2027-01-14">January 14, 2027</time> · 17:00 Brussels time',page)
            self.assertIn('€16 million topic budget',page)
            self.assertIn('€5–6 million per project for three projects',page)
            self.assertIn('EU Pollinators Monitoring Scheme, soil biodiversity under the Soil Monitoring Law, or Water Framework Directive monitoring',page)
            self.assertIn('soil biodiversity under the Soil Monitoring Law',page)
            self.assertIn('Water Framework Directive',page)
            self.assertIn('relevant genomic techniques and area-specific DNA libraries, and FAIR-by-design data',page)
            self.assertIn('no validated statutory-monitoring or identification method in these areas',page)
            self.assertIn('Not a current lead bid or standalone app grant',page)
            self.assertIn('Open for submission · deadline 14 Jan 2027 · no direct bid fit',page)
            self.assertIn('Open For Submission',page)
            self.assertIn('The general RIA consortium rule requires three independent legal entities in three countries',page)
            self.assertIn('Do not pursue as a lead application or reshape the project to fit',page)
            self.assertIn('No registration, outreach or application has been made',page)
            self.assertIn('Official topic details ↗',page)
            self.assertIn('Official call listing ↗',page)
            self.assertIn('calls-for-proposals?callIdentifier=HORIZON-NATURE-2027-02',page)
            self.assertIn('Applicant eligibility ↗',page)
            for source_id in (201,202,240,413,414):
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
            self.assertTrue(any('/assets/session-label.mjs?' in a for a in assets))
            self.assertTrue(any('/assets/audacity-export.mjs?' in a for a in assets))
            self.assertTrue(any('/assets/aoef-export.mjs?' in a for a in assets))
            self.assertTrue(any('/assets/app-update.mjs?' in a for a in assets))
            self.assertTrue(any('/assets/app-nav-visibility.mjs?' in a for a in assets))
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
            app_pages=('app/index.html','app/station/index.html','app/review/index.html','app/compare/index.html','app/practice/index.html','app/check/index.html')
            for relative in app_pages:
                page=(root/relative).read_text()
                self.assertIn('id="app-update-status"',page)
                self.assertIn('role="status"',page)
            self.assertIn("from './app-update.mjs?v=",(root/'assets/app.js').read_text())
            self.assertIn("from './app-nav-visibility.mjs?v=",(root/'assets/app.js').read_text())

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

    def test_station_discloses_device_variability_before_capture_controls(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/fixture/talk2nature')
            page=(root/'app'/'station'/'index.html').read_text()
            copy=re.search(r'<p id="station-device" class="station-footnote">(.*?)</p>',page)
            self.assertIsNotNone(copy)
            self.assertIn('Phone microphones may filter or change sounds.',copy.group(1))
            self.assertIn('does not identify animals',copy.group(1))
            self.assertLess(page.index('id="station-device"'),page.index('id="station-record-controls"'))
            self.assertLess(page.index('id="station-record-controls"'),page.index('id="station-settings"'))
            advanced=re.search(r'<details id="station-advanced-instruments".*?</details>',page,re.S)
            self.assertIsNotNone(advanced)
            self.assertIn('The level meter is not calibrated',advanced.group(0))
            self.assertIn('dBFS',advanced.group(0))

    def test_microphone_free_practice_action_precedes_animal_and_permission_setup(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/fixture/talk2nature')
            page=(root/'app'/'station'/'index.html').read_text()
            self.assertEqual(page.count('id="station-demo"'),1)
            self.assertLess(page.index('id="station-demo"'),page.index('id="station-capture-mode"'))
            self.assertLess(page.index('id="station-demo"'),page.index('id="station-permission"'))
            self.assertIn('aria-describedby="station-demo-help"',page)
            self.assertIn('Try an invented example first. It uses no microphone or animal audio.',page)
            self.assertIn('.station-console:not([data-phase=setup]) .station-practice{display:none}',
                          (root/'assets'/'station.css').read_text())

    def test_station_journal_export_has_a_name_that_matches_its_visible_label(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/fixture/talk2nature')
            page=(root/'app'/'station'/'index.html').read_text()
            button=re.search(r'<button id="station-export"([^>]*)>(.*?)</button>',page)
            self.assertIsNotNone(button)
            aria_label=re.search(r'\baria-label="([^"]+)"',button.group(1))
            self.assertIsNotNone(aria_label)
            visible_label=re.sub(r'<[^>]+>','',button.group(2))
            self.assertEqual(html.unescape(aria_label.group(1)),html.unescape(visible_label))

    def test_station_save_flow_offers_compare_only_after_download_check(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); build(root,'https://fixture.github.io/talk2nature',True)
            station=(root/'app'/'station'/'index.html').read_text()
            compare=(root/'app'/'compare'/'index.html').read_text()
            self.assertIn('>Save this moment ↓</button>',station)
            self.assertIn('id="station-save-ack" class="station-save-ack" type="button" hidden>I saved the file</button>',station)
            self.assertIn('If it opens as a preview, use Share → Save to Files',station)
            self.assertIn('id="station-compare-link" class="station-save-next" href="/talk2nature/app/compare/" hidden>',station)
            self.assertIn('Choose the moment you downloaded from Talk2Nature. No unzipping needed.',compare)
            self.assertIn('Choose saved moment',compare)
            self.assertIn('Open one saved session to review its notes and clips.',compare)
            self.assertIn('You can review the first moment by itself.',compare)
            self.assertIn('Open one saved moment.',(root/'app'/'index.html').read_text())

    def test_mobile_guide_explains_direct_single_session_reopen_without_unzipping(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); build(root,'https://fixture.github.io/talk2nature',True)
            mobile=(root/'mobile'/'index.html').read_text()
            self.assertIn('Real sessions stay in temporary memory until you download a copy.',mobile)
            self.assertIn('Open it in Compare to review your saved moment; no unpacking needed.',mobile)
            self.assertNotIn('unzip it to review a WAV',mobile)

    def test_field_companion_listen_navigation_uses_the_beginner_whole_moment_route(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True)
            expected='href="/talk2nature/app/station/?mode=companion#station-console">Listen</a>'
            for relative in ('app/index.html','app/station/index.html','app/review/index.html','app/compare/index.html','app/practice/index.html','app/check/index.html'):
                with self.subTest(page=relative):
                    page=(root/relative).read_text()
                    navigation=re.search(r'<nav class="app-nav" aria-label="App navigation">(.*?)</nav>',page)
                    self.assertIsNotNone(navigation)
                    self.assertIn(expected,navigation.group(1))

    def test_field_companion_home_links_to_account_free_feedback_helper(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True)
            home=(root/'app/index.html').read_text()
            feedback=(root/'mobile/index.html').read_text()
            self.assertIn('href="/talk2nature/mobile/#share"',home)
            self.assertIn('Tell us what worked or felt confusing',home)
            self.assertIn('No account needed. Nothing is sent automatically.',home)
            self.assertIn('id="mobile-feedback-form"',feedback)
            self.assertIn('Nothing is saved or sent by this form.',feedback)

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
            self.assertIn('Download a copy before closing to keep a real moment.',home)
            guidance='Your sound and notes stay in this page. Download a copy before closing if you want to keep them.'
            self.assertIn(guidance,station)
            boundary='We do not call, imitate or prompt animals. You choose when recording starts and can stop it at any time. In the browser, recording ends if you leave this page.'
            self.assertIn(boundary,station)
            self.assertLess(station.index('id="station-zero-command"'),station.index('id="station-permission"'))
            self.assertLess(station.index('id="station-retention-guidance"'),station.index('id="station-start"'))
            self.assertIn('aria-describedby="station-zero-command station-retention-guidance"',station)
            self.assertIn('href="/talk2nature/app/station/?mode=demo#station-demo">Try a no-microphone rehearsal ↓</a>',station)
            start_button=re.search(r'<button id="station-start"[^>]*>',station).group(0)
            description_ids=re.search(r'\baria-describedby="([^"]+)"',start_button).group(1).split()
            rendered_ids=set(re.findall(r'\bid="([^"]+)"',station))
            self.assertTrue(set(description_ids).issubset(rendered_ids),description_ids)
            rehearsal_button=re.search(r'<button id="station-demo"[^>]*>',station).group(0)
            self.assertRegex(start_button,r'\sdisabled(?:\s|>)')
            self.assertNotRegex(rehearsal_button,r'\sdisabled(?:\s|>)')
            css=(root/'assets/app.css').read_text()
            self.assertIn('.app-session-actions{display:flex;flex-wrap:wrap;',css)
            self.assertIn('min-height:44px',css)

    def test_companion_home_removes_duplicate_start_and_keeps_the_beginner_paths_clear(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True)
            home=(root/'app/index.html').read_text()
            self.assertIn("Start with an invented example: no microphone or account needed. We don't call, imitate or prompt animals. Real observation is optional.",home)
            self.assertIn('No microphone is used unless you choose Start.',home)
            self.assertNotIn('the parrot did not prepare a TED talk',home)
            self.assertIn('Set up a real 30-second moment',home)
            self.assertIn('Try an example · no microphone',home)
            self.assertIn('href="/talk2nature/app/practice/">Practice first: three invented scenes · no microphone',home)
            self.assertNotIn('YOUR FIRST LITTLE FIELD NOTE',home)
            self.assertNotIn('class="field-invitation"',home)
            panel_marker='<details class="app-more-tools-panel glass">'
            self.assertIn(panel_marker,home)
            self.assertNotIn('<details class="app-more-tools-panel glass" open>',home)
            beginner_paths=home.split(panel_marker,1)[0]
            more_tools=home.split(panel_marker,1)[1].split('</details>',1)[0]
            self.assertIn('Practice first: three invented scenes · no microphone',beginner_paths)
            self.assertIn('.app-scenarios>.app-practice-prompt', (root/'assets/app.css').read_text())
            self.assertEqual(beginner_paths.count('<a class="scenario-card glass'),3)
            self.assertIn('href="/talk2nature/app/station/?mode=outdoor"',beginner_paths)
            self.assertIn('href="/talk2nature/app/station/?mode=companion"',beginner_paths)
            self.assertIn('02 / ANY ANIMAL, OR UNSURE',beginner_paths)
            self.assertIn('Choose an animal group if you like, or leave it unknown.',beginner_paths)
            self.assertIn('href="/talk2nature/app/station/?mode=parrot"',beginner_paths)
            self.assertIn('Check your phone at home.',more_tools)
            self.assertIn('Open one saved moment.',more_tools)
            self.assertIn('Review it by itself, or add another when you want to compare what changed.',more_tools)
            self.assertIn('href="/talk2nature/app/review/"',more_tools)
            self.assertIn('Review a recording',more_tools)
            self.assertIn('href="/talk2nature/app/practice/"',more_tools)
            self.assertNotIn('Check your phone at home.',beginner_paths)
            self.assertNotIn('Open one saved moment.',beginner_paths)

    def test_shared_moments_guidance_does_not_require_a_familiar_animal_or_known_identity(self):
        app_js=(Path(__file__).resolve().parents[1]/'web/assets/app.js').read_text()
        self.assertIn('Observe any animal naturally.',app_js)
        self.assertIn('leave the identity unsure.',app_js)

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

    def test_praatplusplus_note_limits_pinned_static_security_warning(self):
        note=next(n for n in load('research') if n['slug']=='praatplusplus-annotation-tool-2026')
        self.assertTrue({484,485} <= set(note['source_ids']))
        self.assertIn('your_secret_key',note['finding'])
        self.assertIn('0.0.0.0',note['finding'])
        self.assertIn('not a complete route-level',note['limitations'])
        with tempfile.TemporaryDirectory() as d:
            output=Path(d)
            build(output)
            page=(output/'research'/'praatplusplus-annotation-tool-2026'/'index.html').read_text()
        self.assertIn('Do not expose that revision on a shared network',page)
        self.assertIn('not a complete route-level',page)
        self.assertIn('login_routes.py#L9-L55',page)

    def test_monk_parakeet_identity_review_is_bounded_and_links_its_guide(self):
        project_root=Path(__file__).resolve().parents[1]
        note=next(n for n in load('research') if n['slug']=='parrot-data-feasibility')
        request=note['review_request']
        self.assertEqual(len(request['questions']),5)
        self.assertIn('not call meaning',request['summary'])
        self.assertIn('No independent review has been received',request['status'])
        self.assertEqual(request['guide_path'],'docs/FIRST_DATASET_REVIEW_PACKET.md')
        guide=(project_root/'docs'/'FIRST_DATASET_REVIEW_PACKET.md').read_text()
        self.assertIn('monk-parakeet known-caller identity',guide)
        self.assertIn('Earlier table-derived aggregate outputs have been removed',guide)
        self.assertIn('not admitted for processing',guide)
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/Metivity/talk2nature')
            page=(root/'research'/'parrot-data-feasibility'/'index.html').read_text()
        self.assertIn('Independent review of monk-parakeet caller identity',page)
        self.assertIn('known-caller identity analysis is useful and defensible',page)
        self.assertIn('https://github.com/Metivity/talk2nature/blob/main/docs/FIRST_DATASET_REVIEW_PACKET.md',page)
        self.assertIn('https://github.com/Metivity/talk2nature/issues/new?template=scientific-review.yml',page)

    def test_japanese_tit_note_renders_source_linked_competing_theories(self):
        project_root=Path(__file__).resolve().parents[1]
        note=next(n for n in load('research') if n['slug']=='bird-call-syntax')
        comparison=note['theory_comparison']
        self.assertEqual([item['name'] for item in comparison['items']],[
            'Minimal Compositionality',
            'Bird Implicatures',
            'Finite-list and finite-state/concatenation alternatives (Beckers et al., 2024)',
        ])
        self.assertEqual(len(note['review_request']['questions']),5)
        self.assertIn(318,note['source_ids'])
        guide=(project_root/'docs'/'JAPANESE_TIT_REVIEW.md').read_text()
        self.assertIn('Mendeley record exposes no file rows',guide)
        self.assertIn('Coye & Dutour (2025)',guide)
        self.assertIn('research/heterospecific-mobbing-sequences/',guide)
        self.assertIn('No reversed-order sequence was tested',guide)
        self.assertIn('No independent specialist review has been received',guide)
        self.assertIn('not a ready-to-run playback protocol',guide)
        sources={source['id']:source for source in load('sources')}
        critique=sources[318]
        self.assertEqual(critique['url'],'https://doi.org/10.3389/fpsyg.2024.1393895')
        self.assertIn('finite-state',critique['origin'])
        self.assertIn('CC BY',critique['rights']['article'])
        source=sources[266]
        self.assertEqual(source['review_url'],'https://cnrs.hal.science/hal-04840821v1')
        self.assertIn('CC BY 4.0',source['rights']['article'])
        comparator=sources[268]
        self.assertEqual(comparator['checked'],'2026-10-27')
        self.assertIn('HTTP 403',comparator['origin'])
        self.assertIn('CC BY 4.0',comparator['rights']['article'])
        self.assertIn('Xeno-Canto',comparator['rights']['article'])
        resources=json.loads((project_root/'research'/'resources.json').read_text())['resources']
        theory=next(item for item in resources if item['id']=='japanese-tit-bird-implicatures-2024-paper')
        self.assertIn('CC-BY-4.0',theory['rights']['license'])
        critique_paper=next(item for item in resources if item['id']=='songbird-syntax-critique-2024-paper')
        self.assertEqual(critique_paper['source_ids'],[318])
        self.assertEqual(critique_paper['acquisition'],'metadata_only')
        self.assertEqual(theory['acquisition'],'metadata_only')
        with tempfile.TemporaryDirectory() as d:
            build(Path(d),'https://fixture.github.io/talk2nature',True,'https://github.com/Metivity/talk2nature')
            page=(Path(d)/'research'/'bird-call-syntax'/'index.html').read_text()
        self.assertIn('Two explanations, one unresolved test',page)
        self.assertIn('Distinctive prediction:',page)
        self.assertIn('Minimal Compositionality',page)
        self.assertIn('Bird Implicatures',page)
        self.assertIn('separate Wiley supporting-information PDF returned HTTP 403',page)
        self.assertIn('https://cnrs.hal.science/hal-04840821v1',page)
        self.assertIn('OPEN METHODS QUESTION',page)
        self.assertIn('Which 2016 and 2017 contrasts best support an order-sensitive receiver response',page)
        self.assertIn('cross-species generalization',page)
        self.assertIn('No reversed-order condition was tested.',page)
        self.assertIn('Mobbing sequences of American wrens elicit mobbing responses in European tits',page)
        self.assertIn('class="review-actions" role="group"',page)
        self.assertIn('Submit a public methods review',page)
        self.assertIn('https://github.com/Metivity/talk2nature/blob/main/docs/JAPANESE_TIT_REVIEW.md',page)
        self.assertIn('scientific-review.yml',page)

    def test_lilac_crowned_amazon_context_note_preserves_evidence_and_rights_boundaries(self):
        note=next(n for n in load('research') if n['slug']=='lilac-crowned-amazon-vocal-context-2016')
        self.assertEqual(note['source_ids'],[275])
        self.assertIn('not prediction of behavior from sound',note['finding'])
        self.assertIn('playback evidence is needed',note['limitations'])
        self.assertEqual(note['atlas']['locations'][0]['place_id'],'chamela-cuixmala')
        resources=json.loads((Path(__file__).parents[1]/'research/resources.json').read_text())['resources']
        paper=next(r for r in resources if r['id']=='lilac-crowned-amazon-context-paper-2016')
        supplements=next(r for r in resources if r['id']=='lilac-crowned-amazon-context-supplements-2016')
        self.assertIn('CC-BY-4.0',paper['rights']['license'])
        self.assertIn('CC0',supplements['rights']['license'])
        self.assertNotEqual(paper['rights']['license'],supplements['rights']['license'])
        for resource in (paper,supplements):
            self.assertEqual(resource['acquisition'],'metadata_only')
            self.assertEqual(resource['files'],[])
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True)
            page=(root/'research'/'lilac-crowned-amazon-vocal-context-2016'/'index.html').read_text()
            self.assertIn('content="index,follow"',page)
            self.assertIn('https://fixture.github.io/talk2nature/research/lilac-crowned-amazon-vocal-context-2016/',page)
            self.assertIn('https://doi.org/10.1186/s12983-016-0169-6',page)
            self.assertIn('note-type discrimination',page)
            self.assertIn('lilac-crowned-amazon-vocal-context-2016/',(root/'sitemap.xml').read_text())

    def test_mobile_bioacoustics_note_keeps_device_claims_bounded_and_data_metadata_only(self):
        note=next(n for n in load('research') if n['slug']=='smartphone-bioacoustics-device-variability')
        self.assertEqual(note['source_ids'],[280,282,283,284,285])
        self.assertIn('53% of citizen recordings',note['finding'])
        self.assertIn('35 phone models',note['finding'])
        self.assertIn('does not establish general ultrasonic capture above that range',note['limitations'])
        self.assertIn('not microphone calibration',note['lesson'])
        self.assertIn('17.46 MB',note['study_snapshot'][-3][1])
        self.assertIn('HTTP 403',note['study_snapshot'][-3][1])
        self.assertEqual(note['atlas']['location_status'],'not_applicable')
        resources=json.loads((Path(__file__).parents[1]/'research/resources.json').read_text())['resources']
        ids={
            'nightingale-smartphone-recordings-paper-2021',
            'nightingale-smartphone-recordings-data-2021',
            'mobile-bat-monitoring-paper-2024',
            'mobile-bat-monitoring-data-2024',
        }
        selected=[r for r in resources if r['id'] in ids]
        self.assertEqual({r['id'] for r in selected},ids)
        for resource in selected:
            self.assertTrue(resource['source_ids'])
            self.assertEqual(resource['acquisition'],'metadata_only')
            self.assertEqual(resource['files'],[])
        nightingale=next(r for r in selected if r['id']=='nightingale-smartphone-recordings-data-2021')
        self.assertEqual(nightingale['rights']['license'],'CC BY 4.0, declared by the Zenodo record API')
        self.assertEqual(nightingale['rights']['research_use'],'conditional')
        self.assertIn('NCSP_Data.xlsx',nightingale['access'])
        self.assertIn('No audio file is listed',nightingale['access'])
        self.assertIn('not verified locally',nightingale['review_depth'])
        note=next(n for n in load('research') if n['slug']=='smartphone-bioacoustics-device-variability')
        self.assertIn('no audio file appears in that response',note['review_depth'])
        self.assertIn('spreadsheet files',note['limitations'])
        self.assertIn('does not show whether their rows link to sounds stored elsewhere',note['finding'])
        bats=next(r for r in selected if r['id']=='mobile-bat-monitoring-data-2024')
        self.assertIn('CC0 1.0',bats['rights']['license'])
        self.assertEqual(bats['rights']['research_use'],'conditional')
        self.assertIn('17.46 MB',bats['access'])
        self.assertIn('3.89 GB',bats['access'])
        self.assertIn(284,bats['source_ids'])
        self.assertIn(285,bats['source_ids'])
        self.assertIn('smartphone-bioacoustics-device-variability',next(p for p in load('learning-paths')['paths'] if p['id']=='first-animal')['notes'])
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True)
            page=(root/'research'/'smartphone-bioacoustics-device-variability'/'index.html').read_text()
            station=(root/'app'/'station'/'index.html').read_text()
            self.assertIn('content="index,follow"',page)
            self.assertIn('https://fixture.github.io/talk2nature/research/smartphone-bioacoustics-device-variability/',page)
            self.assertIn('17.46 MB',page)
            self.assertIn('https://dev.datadryad.org/help/guides/reuse',page)
            self.assertIn('The level meter is not calibrated',station)
            self.assertIn('smartphone-bioacoustics-device-variability/',(root/'sitemap.xml').read_text())

    def test_pteroset_review_keeps_detection_scope_rights_and_file_provenance_separate(self):
        note=next(n for n in load('research') if n['slug']=='pteroset-detection-benchmark-2026')
        self.assertEqual(note['source_ids'],[286,287,288,417,418])
        self.assertIn('not what a bird is communicating',note['finding'])
        self.assertIn('only the MAP1 test fold holds out a distinct named landscape',note['limitations'])
        self.assertEqual(note['atlas']['location_status'],'mapped')
        self.assertEqual({location['place_id'] for location in note['atlas']['locations']},{'pivijay-study-region','puerto-asis-study-region'})
        self.assertIn('municipal reference points',note['atlas']['location_note'])
        self.assertIn('All 12 names, sizes and provider MD5 strings in the exact v5 API manifest match this catalog',note['limitations'])
        self.assertIn('4,096-byte HTTP 206 range request',note['limitations'])
        self.assertIn('Row values were not reviewed or saved',note['limitations'])
        self.assertIn('record 21829388',note['next_review'])
        sources={s['id']:s for s in load('sources')}
        self.assertEqual({286,287,288} & sources.keys(),{286,287,288})
        resources=json.loads((Path(__file__).parents[1]/'research/resources.json').read_text())['resources']
        ids={'pteroset-paper-2026','pteroset-data-v5-2026','pteroset-code-2026','pteroset-checkpoints-2026'}
        selected={r['id']:r for r in resources if r['id'] in ids}
        self.assertEqual(set(selected),ids)
        for resource in selected.values():
            self.assertEqual(resource['acquisition'],'metadata_only')
            self.assertEqual(resource['files'],[])
            self.assertTrue(resource['source_ids'])
        self.assertIn('CC BY 4.0',selected['pteroset-paper-2026']['rights']['license'])
        self.assertIn('CC BY 4.0',selected['pteroset-data-v5-2026']['rights']['license'])
        self.assertIn('MIT',selected['pteroset-code-2026']['rights']['license'])
        self.assertEqual(selected['pteroset-checkpoints-2026']['rights']['research_use'],'unresolved')
        data_review=selected['pteroset-data-v5-2026']['review_depth']
        self.assertIn('no dataset file bytes were hashed',data_review)
        self.assertIn('only its header line',data_review)
        self.assertIn('row values were not reviewed or saved',data_review)
        self.assertEqual(selected['pteroset-data-v5-2026']['acquisition'],'metadata_only')
        code=selected['pteroset-code-2026']
        self.assertIn('record 21829388',code['decision'])
        self.assertIn('breakpoint()',code['limitations'])
        self.assertIn('latest Zenodo version',code['limitations'])
        self.assertIn('latitude and longitude',code['limitations'])
        manifest=selected['pteroset-data-v5-2026']['source_manifest']
        self.assertEqual(len(manifest),12)
        self.assertEqual(len({row['name'] for row in manifest}),12)
        self.assertTrue(all(row['size']>0 and re.fullmatch(r'md5:[0-9a-f]{32}',row['checksum']) for row in manifest))
        paths=load('learning-paths')['paths']
        for path_id in ('detect','model'):
            self.assertIn(note['slug'],next(p for p in paths if p['id']==path_id)['notes'])
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True)
            page=(root/'research'/'pteroset-detection-benchmark-2026'/'index.html').read_text()
            canonical='https://fixture.github.io/talk2nature/research/pteroset-detection-benchmark-2026/'
            self.assertIn('content="index,follow"',page)
            self.assertIn(canonical,page)
            self.assertIn('PteroSet',page)
            self.assertIn('https://doi.org/10.5281/zenodo.21829388',page)
            self.assertIn(canonical,(root/'sitemap.xml').read_text())

    def test_hyenaset_note_separates_event_labels_rights_and_baseline_exposure(self):
        note=next(n for n in load('research') if n['slug']=='hyenaset-event-detection-benchmark')
        self.assertEqual(note['source_ids'],[148,296,297,298,440])
        self.assertIn('not independently observed receiver responses',note['finding'])
        self.assertIn('pretrained on all available audio',note['limitations'])
        self.assertIn('transductive',note['limitations'])
        self.assertEqual(note['atlas']['location_status'],'mapped')
        self.assertEqual(note['atlas']['locations'][0]['place_id'],'kenya')
        self.assertEqual(note['atlas']['locations'][0]['role'],'study_region')
        self.assertEqual(note['atlas']['locations'][0]['source_id'],296)
        resources=json.loads((Path(__file__).parents[1]/'research/resources.json').read_text())['resources']
        paper=next(r for r in resources if r['id']=='hyenaset-preprint-2026')
        dataset=next(r for r in resources if r['id']=='hyenaset-dataset-v1')
        self.assertEqual(paper['rights']['license'],'CC BY 4.0 (bioRxiv version 2 record)')
        self.assertEqual(dataset['rights']['license'],'CC BY-NC-SA 4.0 (dataset-specific terms in the official Edmond API)')
        self.assertEqual(dataset['rights']['commercial_use'],'not_admitted')
        self.assertEqual(dataset['acquisition'],'metadata_only')
        self.assertEqual(dataset['files'],[])
        self.assertIn('107,184,528,475-byte',dataset['version'])
        detect=next(p for p in load('learning-paths')['paths'] if p['id']=='detect')
        self.assertIn(note['slug'],detect['notes'])
        self.assertIn('pretrains on all available audio',detect['gate'])
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True)
            page=(root/'research/hyenaset-event-detection-benchmark/index.html').read_text()
            canonical='https://fixture.github.io/talk2nature/research/hyenaset-event-detection-benchmark/'
            self.assertIn('content="index,follow"',page)
            self.assertIn(canonical,page)
            self.assertIn('CC BY-NC-SA 4.0',page)
            self.assertIn('all available audio',page)
            self.assertIn(canonical,(root/'sitemap.xml').read_text())

    def test_cowrumia_note_rejects_reused_test_set_and_keeps_component_rights_separate(self):
        slug='cowrumia-bovine-audio-app-2026'
        note=next(n for n in load('research') if n['slug']==slug)
        self.assertEqual(note['source_ids'],[306,307,308])
        self.assertIn('not an untouched final-test estimate',note['finding'])
        self.assertIn('does not group by animal, session or site',note['limitations'])
        self.assertEqual(note['atlas']['location_status'],'pending')
        self.assertEqual(note['atlas']['locations'],[])
        sources={s['id']:s for s in load('sources')}
        self.assertIn('validation_data',sources[307]['origin'])
        resources={r['id']:r for r in json.loads((Path(__file__).parents[1]/'research/resources.json').read_text())['resources']}
        code=resources['cowrumia-android-ml-code-2026']
        model=resources['cowrumia-bovine-model-assets-2026']
        data=resources['cowrumia-bovine-vocalization-data-2026']
        self.assertIn('MIT',code['rights']['license'])
        self.assertEqual(model['rights']['research_use'],'unresolved')
        self.assertEqual(data['rights']['research_use'],'unresolved')
        for resource in (code,model,data):
            self.assertEqual(resource['acquisition'],'metadata_only')
            self.assertEqual(resource['files'],[])
        model_path=next(p for p in load('learning-paths')['paths'] if p['id']=='model')
        self.assertIn(slug,model_path['notes'])
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True)
            page=(root/'research'/slug/'index.html').read_text()
            library=(root/'research/resources/index.html').read_text()
            canonical=f'https://fixture.github.io/talk2nature/research/{slug}/'
            self.assertIn('<meta name="robots" content="index,follow">',page)
            self.assertIn(f'rel="canonical" href="{canonical}"',page)
            self.assertIn('CowRumIA',page)
            self.assertIn('not an untouched final-test estimate',page)
            self.assertIn('https://zenodo.org/records/20406266',page)
            self.assertIn('CowRumIA bovine vocalization dataset v1.0.0',library)
            self.assertIn(canonical,(root/'sitemap.xml').read_text())

    def test_moologue_review_separates_mobile_learning_versions_and_component_rights(self):
        slug='moologue-cattle-call-learning-app-2026'
        note=next(n for n in load('research') if n['slug']==slug)
        self.assertEqual(note['source_ids'],[419,420,421])
        self.assertIn('offline-first educational app',note['finding'])
        self.assertIn('cloud workflow',note['finding'])
        self.assertIn('569 clips',note['finding'])
        self.assertIn('no root LICENSE file',note['limitations'])
        self.assertIn('HTTP 406',note['review_depth'])
        self.assertEqual(note['atlas']['location_status'],'pending')
        self.assertEqual(note['atlas']['locations'],[])
        resources={r['id']:r for r in json.loads((Path(__file__).parents[1]/'research/resources.json').read_text())['resources']}
        paper=resources['moologue-paper-2026']
        code=resources['moologue-app-code-2025-snapshot']
        dataset=resources['moologue-cattle-audio-dataset-2026']
        self.assertEqual(paper['rights']['license'],'CC-BY-NC-ND-4.0')
        self.assertEqual(code['rights']['research_use'],'unresolved')
        self.assertEqual(dataset['rights']['research_use'],'unresolved')
        self.assertEqual(dataset['rights']['redistribution'],'not_admitted')
        for resource in (paper,code,dataset):
            self.assertEqual(resource['acquisition'],'metadata_only')
            self.assertEqual(resource['files'],[])
            self.assertTrue(resource['source_ids'])
        model_path=next(p for p in load('learning-paths')['paths'] if p['id']=='model')
        self.assertIn(slug,model_path['notes'])
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True)
            page=(root/'research'/slug/'index.html').read_text()
            library=(root/'research/resources/index.html').read_text()
            canonical=f'https://fixture.github.io/talk2nature/research/{slug}/'
            self.assertIn('content="index,follow"',page)
            self.assertIn(canonical,page)
            self.assertIn('8023dbdfed8587d07eeafa54accb68408ffaefbe',page)
            self.assertIn('https://doi.org/10.5281/zenodo.17764250',page)
            self.assertIn('MooLogue',library)
            self.assertIn(canonical,(root/'sitemap.xml').read_text())

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
            self.assertIn('id="source-461"',sources)
            self.assertIn('href="https://doi.org/10.6084/m9.figshare.24147825.v1"',note)
            self.assertIn('second-observer reliability',note)
            self.assertIn('observer-classification accuracy 0.72',note)
            self.assertIn('not model performance',note)
            self.assertIn('does not test generalization to unseen birds',note)
            self.assertIn('Edmond V1/DataCite declares MIT at deposit level',note)
            self.assertIn('No Edmond file was downloaded and no terms were accepted',note)
            self.assertIn('href="https://api.datacite.org/dois/10.17617/3.RUIM5I"',note)
            self.assertNotIn('808 annotation rows',note)
            self.assertNotIn('46 unmatched',note)
            self.assertNotIn('762 references present',note)
            resources=json.loads((Path(__file__).parents[1]/'research/resources.json').read_text())['resources']
            annotation=next(r for r in resources if r['id']=='monk-parakeet-annotations')
            self.assertEqual(annotation['acquisition'],'metadata_only')
            self.assertEqual(annotation['files'],[])
            self.assertEqual(annotation['rights']['research_use'],'unresolved')
            supplement=next(r for r in resources if r['id']=='monk-parakeet-supplement')
            self.assertEqual(supplement['source_ids'],[55,461])
            self.assertEqual(supplement['rights']['license'],'CC-BY-4.0')
            self.assertEqual(supplement['acquisition'],'metadata_only')
            project_root=Path(__file__).parents[1]
            self.assertFalse((project_root/'research/parrot_sample_report.json').exists())
            self.assertFalse((project_root/'research/monk_parakeet_join_audit.json').exists())

    def test_parrot_video_interface_note_preserves_reporting_and_rights_gates(self):
        note=next(n for n in load('research') if n['slug']=='parrot-video')
        self.assertIn('65 parrot-triggered live calls',note['finding'])
        self.assertIn('live-minus-playback differences of +50, +17, +75, +17, +8, -8, -8, +33 and +25',note['finding'])
        self.assertIn('The printed row is reversed for seven birds',note['finding'])
        self.assertIn('Table 3',note['limitations'])
        self.assertIn('P3 and P5 also appear transposed',note['limitations'])
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
            self.assertIn('The printed row is reversed for seven birds',note_page)
            self.assertIn('P3 and P5 also appear transposed',note_page)
            self.assertIn('Parrot choice in live and playback video calls',resource_page)
            self.assertIn('No study dataset, code or media were acquired',resource_page)

    def test_parrot_touchscreen_full_text_review_keeps_phone_and_communication_boundaries(self):
        note=next(n for n in load('research') if n['slug']=='parrot-touchscreen-ergonomics')
        self.assertIn('full article text',note['review_depth'])
        self.assertIn('not a communication test',note['finding'])
        self.assertIn('not phones',note['limitations'])
        self.assertIn('does not justify adding playback',note['lesson'])
        resources=json.loads((Path(__file__).parents[1]/'research/resources.json').read_text())['resources']
        resource=next(r for r in resources if r['id']=='parrot-touchscreen-ergonomics-2024-paper')
        self.assertEqual(resource['source_ids'],[122])
        self.assertEqual(resource['acquisition'],'metadata_only')
        self.assertEqual(resource['files'],[])
        self.assertIn('CC BY-NC-ND 4.0',resource['rights']['license'])
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True)
            page=(root/'research/parrot-touchscreen-ergonomics/index.html').read_text()
            resources_page=(root/'research/resources/index.html').read_text()
            self.assertIn('What parrot touchscreen research can—and cannot—tell us',page)
            self.assertIn('rel="canonical" href="https://fixture.github.io/talk2nature/research/parrot-touchscreen-ergonomics/"',page)
            self.assertIn('<meta name="robots" content="index,follow">',page)
            self.assertIn('10.1-inch tablet',page)
            self.assertIn('No More Angry Birds: Investigating Touchscreen Ergonomics',resources_page)

    def test_learning_paths_have_actionable_reviewable_dependencies(self):
        notes={n['slug']:n for n in load('research')}
        paths=load('learning-paths')['paths']
        self.assertEqual(len({p['id'] for p in paths}),len(paths))
        for path in paths:
            self.assertTrue(set(path['notes']) <= notes.keys())
            for field in ('question','decision','next_step','gate'):
                self.assertTrue(path[field])
        for note in notes.values():
            self.assertIn(note['purpose'],('Models & evaluation','Data & annotation','Behavior & communication','Plants & fungi','Animal-computer interaction','Vocal development','Data standards & interoperability','Multimodal methods'))
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

    def test_honeybee_vision_note_keeps_signal_claims_rights_and_seo_bounded(self):
        project_root=Path(__file__).resolve().parents[1]
        note=next(n for n in load('research') if n['slug']=='honeybee-waggle-vision-decoding-2017')
        self.assertIn('not an independent colony-',note['limitations'])
        self.assertIn('distance required empirical calibration',note['limitations'])
        self.assertIn('general gesture translator',note['lesson'])
        self.assertIn('No independent insect-behavior',note['expert_review'])
        guide=(project_root/'docs'/'HONEYBEE_VISION_REVIEW.md').read_text()
        self.assertIn('no recognized license',guide)
        resources=json.loads((project_root/'research'/'resources.json').read_text())['resources']
        selected={r['id']:r for r in resources if r['id'].startswith('honeybee-')}
        self.assertEqual(set(selected),{
            'honeybee-waggle-vision-paper-2017',
            'honeybee-waggle-vision-code-2017',
            'honeybee-waggle-ground-truth-data-2017',
            'honeybee-beesbook-longterm-paper-2015',
            'honeybee-dance-following-paper-2023',
            'honeybee-dance-following-data-2023',
        })
        for resource in selected.values():
            with self.subTest(resource=resource['id']):
                self.assertEqual(resource['acquisition'],'metadata_only')
                self.assertEqual(resource['files'],[])
        self.assertEqual(selected['honeybee-waggle-vision-code-2017']['rights']['research_use'],'unresolved')
        self.assertEqual(selected['honeybee-waggle-ground-truth-data-2017']['rights']['redistribution'],'unresolved')
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/Metivity/talk2nature')
            self.assertTrue(check_site(root)['public'])
            page=(root/'research'/'honeybee-waggle-vision-decoding-2017'/'index.html').read_text()
            self.assertIn('A camera can decode a known bee signal',page)
            self.assertIn('no recognized license',page)
            self.assertIn('scientific-review.yml',page)
            self.assertIn('/research/honeybee-waggle-vision-decoding-2017/',(root/'sitemap.xml').read_text())
            resource_page=(root/'research'/'resources'/'index.html').read_text()
            self.assertIn('WDD_paper honeybee waggle-dance analysis code',resource_page)
            self.assertIn('WDD_paper 200-waggle-run ground-truth sample',resource_page)
            paths=(root/'research'/'starting-points'/'index.html').read_text()
            self.assertIn('/research/honeybee-waggle-vision-decoding-2017/',paths)

    def test_yellow_naped_amazon_note_separates_component_rights_and_is_indexable(self):
        project_root=Path(__file__).resolve().parents[1]
        note=next(n for n in load('research') if n['slug']=='yellow-naped-amazon-vocal-culture-2024')
        self.assertIn('dialect changes altered receiver behavior, fitness or call meaning',note['limitations'])
        self.assertLessEqual(len(note['seo_description']),160)
        resources=json.loads((project_root/'research'/'resources.json').read_text())['resources']
        selected={r['id']:r for r in resources if r['id'].startswith('yellow-naped-amazon-vocal-culture-') or r['id']=='amazon-vocal-culture-code-2024'}
        self.assertEqual(set(selected),{
            'yellow-naped-amazon-vocal-culture-paper-2024',
            'yellow-naped-amazon-vocal-culture-data-v6',
            'amazon-vocal-culture-code-2024',
        })
        for resource in selected.values():
            with self.subTest(resource=resource['id']):
                self.assertEqual(resource['acquisition'],'metadata_only')
        self.assertIn('no alternate route was used',selected['yellow-naped-amazon-vocal-culture-data-v6']['access'])
        self.assertIn('keep training admission false',selected['yellow-naped-amazon-vocal-culture-data-v6']['decision'])
        self.assertIn('all rights reserved',selected['yellow-naped-amazon-vocal-culture-paper-2024']['rights']['license'])
        self.assertIn('CC0-1.0',selected['yellow-naped-amazon-vocal-culture-data-v6']['rights']['license'])
        self.assertIn('MIT',selected['amazon-vocal-culture-code-2024']['rights']['license'])
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/Metivity/talk2nature')
            self.assertTrue(check_site(root)['public'])
            page=(root/'research'/'yellow-naped-amazon-vocal-culture-2024'/'index.html').read_text()
            self.assertIn('The data deposit is CC0-1.0',page)
            self.assertIn('all rights reserved',page)
            self.assertIn('separately MIT-licensed',page)
            self.assertIn('401',page)
            self.assertIn('/research/yellow-naped-amazon-vocal-culture-2024/',(root/'sitemap.xml').read_text())
            self.assertIn('/research/yellow-naped-amazon-vocal-culture-2024/',(root/'research'/'index.html').read_text())

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

    def test_inat_sounds_is_linked_as_a_restricted_species_classification_reference(self):
        project_root=Path(__file__).resolve().parents[1]
        note=next(n for n in load('research') if n['slug']=='inat-sounds-2024')
        self.assertEqual(note['source_ids'],[347,348,349,350,351])
        self.assertIn('not event-level meaning',note['finding'])
        self.assertIn('prohibit distributing recordings',note['limitations'])
        resources=json.loads((project_root/'research'/'resources.json').read_text())['resources']
        selected={r['id']:r for r in resources if r['id'].startswith('inat-sounds-')}
        self.assertEqual(set(selected),{
            'inat-sounds-paper-neurips-2024',
            'inat-sounds-dataset-2024',
            'inat-sounds-code-2024',
            'inat-sounds-model-weights-2024',
        })
        dataset=selected['inat-sounds-dataset-2024']
        self.assertEqual(dataset['acquisition'],'metadata_only')
        self.assertEqual(dataset['rights']['research_use'],'conditional')
        self.assertEqual(dataset['rights']['commercial_use'],'not_admitted')
        self.assertEqual(dataset['rights']['redistribution'],'not_admitted')
        self.assertEqual(selected['inat-sounds-code-2024']['rights']['license'],'MIT reported by the official GitHub repository for code.')
        weights=selected['inat-sounds-model-weights-2024']
        self.assertTrue(all(weights['rights'][field]=='unresolved' for field in ('research_use','commercial_use','redistribution')))
        self.assertEqual(weights['acquisition'],'metadata_only')
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/Metivity/talk2nature')
            self.assertTrue(check_site(root)['public'])
            page=(root/'research'/'inat-sounds-2024'/'index.html').read_text()
            self.assertIn('not event-level meaning',page)
            self.assertIn('non-commercial research and education only',page)
            self.assertIn('name="robots" content="index,follow"',page)
            self.assertIn('/research/inat-sounds-2024/',(root/'sitemap.xml').read_text())
            resource_page=(root/'research'/'resources'/'index.html').read_text()
            self.assertIn('iNatSounds 2024 multi-taxon audio dataset',resource_page)
            paths=(root/'research'/'starting-points'/'index.html').read_text()
            self.assertIn('/research/inat-sounds-2024/',paths)

    def test_ceb_api_inventory_keeps_annotation_tables_metadata_only(self):
        project_root=Path(__file__).resolve().parents[1]
        resources=json.loads((project_root/'research'/'resources.json').read_text())['resources']
        resource=next(r for r in resources if r['id']=='central-european-birds-ceb-v1-1')
        self.assertEqual(resource['reviewed'],'2026-10-23')
        self.assertEqual(resource['acquisition'],'metadata_only')
        self.assertEqual(resource['files'],[])
        self.assertIn('8,559,233 bytes',resource['review_depth'])
        self.assertIn('5 MiB per-file limit',resource['review_depth'])
        self.assertIn('No CSV rows',resource['review_depth'])
        self.assertIn('left uninspected',resource['access'])
        self.assertIn('cannot serve as a concealed locked holdout',resource['access'])
        sources=json.loads((project_root/'content'/'sources.json').read_text())
        source=next(s for s in sources if s['id']==333)
        self.assertEqual(source['checked'],'2026-10-23')
        self.assertIn('not locally verified',source['origin'])

    def test_zf_aim_release_manifest_keeps_unresolved_data_rights_out_of_training(self):
        project_root=Path(__file__).resolve().parents[1]
        manifest=json.loads((project_root/'research'/'zf_aim_zenodo_manifest_2026-10-23.json').read_text())
        data_manifest=json.loads((project_root/'research'/'zf_aim_data_zenodo_manifest_2026-10-24.json').read_text())
        resources=json.loads((project_root/'research'/'resources.json').read_text())['resources']
        release=next(r for r in resources if r['id']=='zebra-finch-zf-aim-zenodo-release-2026')
        data_release=next(r for r in resources if r['id']=='zebra-finch-zf-aim-data-release-2026')
        sources=json.loads((project_root/'content'/'sources.json').read_text())
        preprint_source=next(s for s in sources if s['id']==358)
        source=next(s for s in sources if s['id']==359)
        data_source=next(s for s in sources if s['id']==373)
        note=next(n for n in load('research') if n['slug']=='zf-aim-zebra-finch-turn-taking-2026')
        self.assertEqual(preprint_source['url'],'https://www.biorxiv.org/content/10.64898/2026.02.12.705387v3')
        self.assertEqual(preprint_source['title'],'Leveraging AI-powered interactive playbacks to decipher rules of communication in zebra finches')
        self.assertIn('metadata-only refresh',preprint_source['origin'])
        self.assertEqual(manifest['file_manifest_scope'],'Zenodo record top-level files only; the ZIP archive\'s internal manifest and contents were not inspected.')
        self.assertEqual(manifest['files'],[{
            'key':'zf_aim_release.zip',
            'bytes':26633934601,
            'provider_checksum':'md5:c4726cebb2b57e28a832725e8999731e',
        }])
        self.assertFalse(manifest['integrity']['payload_downloaded'])
        self.assertFalse(manifest['integrity']['checksum_verified_locally'])
        self.assertEqual(release['source_ids'],[359])
        self.assertEqual(release['acquisition'],'metadata_only')
        self.assertEqual(release['files'],[])
        self.assertEqual(release['rights']['research_use'],'unresolved')
        self.assertEqual(release['rights']['commercial_use'],'unresolved')
        self.assertEqual(release['rights']['redistribution'],'not_admitted')
        self.assertIn('inner manifest and contents',release['review_depth'])
        self.assertIn('top-level archive inventory',source['rights']['scope'])
        self.assertEqual(data_manifest['record']['id'],23047646)
        self.assertEqual(data_manifest['record']['record_license_identifier'],'cc-by-sa-4.0')
        self.assertIn('CC-BY-NC',data_manifest['record']['description_license_statement'])
        self.assertEqual(len(data_manifest['files']),11)
        self.assertEqual(sum(f['bytes'] for f in data_manifest['files'] if f['key'].endswith('.flac')),43502273064)
        self.assertFalse(data_manifest['integrity']['payload_downloaded'])
        self.assertFalse(data_manifest['integrity']['checksums_verified_locally'])
        self.assertEqual(data_release['source_ids'],[358,373])
        self.assertEqual(data_release['acquisition'],'metadata_only')
        self.assertEqual(data_release['files'],[])
        self.assertEqual(data_release['rights']['research_use'],'unresolved')
        self.assertEqual(data_release['rights']['commercial_use'],'unresolved')
        self.assertEqual(data_release['rights']['redistribution'],'not_admitted')
        self.assertIn('terms conflict',data_release['decision'])
        self.assertIn('complete top-level filename/size/checksum inventory',data_source['origin'])
        self.assertIn('code/model ZIP inventory',note['reuse']['asset'])
        self.assertIn('CC BY-SA 4.0 while its description says CC BY-NC',note['reuse']['rights'])
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            build(root,'https://fixture.github.io/talk2nature',True,'https://github.com/Metivity/talk2nature')
            page=(root/'research'/'resources'/'index.html').read_text()
            self.assertIn(release['title'],page)
            self.assertIn(data_release['title'],page)
            self.assertIn('metadata-only',page)

    def test_bird_corpus_notes_and_resources_link_to_their_actual_sources(self):
        project_root=Path(__file__).resolve().parents[1]
        sources={s['id']:s for s in load('sources')}
        notes={n['slug']:n for n in load('research')}
        resources=json.loads((project_root/'research'/'resources.json').read_text())['resources']
        resources={r['id']:r for r in resources}

        expected_notes={
            'birdset-powdermill-first-compute-candidate': {
                'https://zenodo.org/records/4656848',
                'https://doi.org/10.5061/dryad.d2547d81z',
            },
            'high-sierra-soundscape-metadata-preflight': {
                'https://zenodo.org/records/7525805',
                'https://zenodo.org/records/19340660',
            },
            'arcticbirdsounds-grouped-split-preflight': {
                'https://doi.org/10.1002/ecy.4047',
                'https://osf.io/b9trx/',
                'https://github.com/Vin985/arctic_songs',
            },
            'arcticsoundsnet-transfer-learning-preflight': {
                'https://doi.org/10.1016/j.ecoinf.2025.103270',
                'https://doi.org/10.5061/dryad.jh9w0vtnr',
                'https://github.com/MZiegenhorn/birdnet-discovery',
            },
        }
        for slug,expected_urls in expected_notes.items():
            with self.subTest(note=slug):
                actual_urls={sources[i]['url'] for i in notes[slug]['source_ids']}
                self.assertTrue(expected_urls.issubset(actual_urls))
                self.assertFalse(any('nlnet.nl' in url or 'mendeley.com' in url
                                     for url in actual_urls))

        expected_resources={
            'powdermill-bird-soundscapes': {'https://zenodo.org/records/4656848'},
            'birdset-baseal-perch-v2-embeddings': {
                'https://zenodo.org/records/19340660',
                'https://zenodo.org/records/4656848',
                'https://zenodo.org/records/7525805',
            },
            'high-sierras-hsn-soundscapes': {'https://zenodo.org/records/7525805'},
            'arcticbirdsounds-soundscape-dataset': {
                'https://doi.org/10.1002/ecy.4047',
                'https://osf.io/b9trx/',
            },
            'arcticsoundsnet-dryad-data': {
                'https://doi.org/10.5061/dryad.jh9w0vtnr',
                'https://doi.org/10.1016/j.ecoinf.2025.103270',
            },
            'wytham-great-tit-source-data': {
                'https://osf.io/n8ac9/',
                'https://doi.org/10.1016/j.anbehav.2024.02.008',
            },
        }
        for resource_id,expected_urls in expected_resources.items():
            with self.subTest(resource=resource_id):
                actual_urls={sources[i]['url'] for i in resources[resource_id]['source_ids']}
                self.assertTrue(expected_urls.issubset(actual_urls))
                self.assertFalse(any('nlnet.nl' in url or 'mendeley.com' in url
                                     for url in actual_urls))

    def test_nbm_review_separates_detection_labels_from_meaning_and_component_rights(self):
        project_root=Path(__file__).resolve().parents[1]
        note=next(n for n in load('research') if n['slug']=='nocturnal-bird-migration-dataset-2026')
        self.assertEqual(note['source_ids'],[431,432,433,434])
        self.assertIn('2,077 audio files',note['finding'])
        self.assertIn('270 total',note['finding'])
        self.assertIn('271 recordings',note['finding'])
        self.assertIn('They do not label observed behavior, receiver response, intention or meaning',note['finding'])
        self.assertIn('mAP@IoU0.5 of 0.67',note['finding'])
        self.assertIn('not independently reproduced',note['limitations'])
        self.assertEqual(note['atlas']['location_status'],'not_applicable')
        resources=json.loads((project_root/'research'/'resources.json').read_text())['resources']
        selected={r['id']:r for r in resources if r['id'].startswith('nbm-')}
        self.assertEqual(set(selected),{
            'nbm-detection-paper-2026',
            'nbm-dataset-v4',
            'nbm-bird-sound-detection-code',
            'nbm-detection-model-weights',
        })
        self.assertTrue(all(r['acquisition']=='metadata_only' and r['files']==[] for r in selected.values()))
        self.assertIn('per-recording terms',selected['nbm-dataset-v4']['rights']['license'])
        self.assertEqual(selected['nbm-dataset-v4']['rights']['research_use'],'unresolved')
        self.assertEqual(selected['nbm-bird-sound-detection-code']['rights']['commercial_use'],'unresolved')
        self.assertEqual(selected['nbm-detection-model-weights']['rights']['redistribution'],'unresolved')

    def test_arctic_bird_library_additions_keep_tasks_and_evidence_limits_separate(self):
        project_root = Path(__file__).resolve().parents[1]
        notes = {note['slug']: note for note in load('research')}
        expected = {
            'individual-bird-identification-temporal-embeddings-2026',
            'wytham-great-tit-song-reidentification-2025',
            'birdset-powdermill-first-compute-candidate',
            'high-sierra-soundscape-metadata-preflight',
            'arcticbirdsounds-grouped-split-preflight',
            'arcticsoundsnet-transfer-learning-preflight',
        }
        self.assertTrue(expected.issubset(notes))
        source_ids = {source['id'] for source in json.loads(
            (project_root / 'content' / 'sources.json').read_text())}
        for slug in expected:
            self.assertTrue(set(notes[slug]['source_ids']).issubset(source_ids), slug)

        arctic = notes['arcticbirdsounds-grouped-split-preflight']
        combined = arctic['finding'] + ' ' + arctic['limitations']
        self.assertIn('4,318', combined)
        self.assertIn('4,319', combined)
        self.assertIn('site-held-out', combined)
        self.assertIn('not evidence', combined)
        caller_id = notes['individual-bird-identification-temporal-embeddings-2026']
        self.assertIn('not animal conversation', caller_id['finding'])
        resource = next(r for r in json.loads(
            (project_root / 'research' / 'resources.json').read_text())['resources']
                        if r['id'] == 'powdermill-bird-soundscapes')
        self.assertEqual(resource['acquisition'], 'sample_approved')
        self.assertEqual(resource['record_doi'], '10.5061/dryad.d2547d81z')
        self.assertEqual(resource['zenodo_api_license_id'], 'cc-zero')
        self.assertIn('not training admission', resource['decision'])

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build(root, 'https://fixture.github.io/talk2nature', True,
                  'https://github.com/Metivity/talk2nature')
            self.assertTrue(check_site(root)['public'])
            page = (root / 'research' / 'arcticbirdsounds-grouped-split-preflight'
                    / 'index.html').read_text()
            self.assertIn('4,318', page)
            self.assertIn('4,319', page)
            self.assertIn('site-held-out', page)

    def test_wytham_great_tit_resource_separates_song_structure_from_meaning(self):
        project_root=Path(__file__).resolve().parents[1]
        note=next(n for n in load('research') if n['slug']=='wytham-great-tit-song-structure-2024')
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

    def test_mozilla_calls_separate_fellowship_theme_fit_from_incubator_readiness(self):
        project_root=Path(__file__).resolve().parents[1]
        opportunities=json.loads((project_root/'content'/'opportunities.json').read_text())
        sources=json.loads((project_root/'content'/'sources.json').read_text())
        sources_by_id={source['id']:source for source in sources}
        fellowship=next(item for item in opportunities if item['slug']=='mozilla-fellowship-2027')
        incubator=next(item for item in opportunities if item['slug']=='mozilla-human-scale-ai-incubator-2026')

        self.assertEqual(fellowship['verified'],'2026-10-31')
        self.assertEqual(fellowship['deadline'],'2026-12-17')
        self.assertIn('community-run environmental sensing',fellowship['fit'])
        self.assertIn('not validation of animal communication',fellowship['fit'])
        self.assertIn('own work and voice',fellowship['next_action'])
        self.assertIn('do not begin an LOI until the founder confirms',fellowship['next_action'])
        for source_id in [fellowship['source_id'],fellowship['terms_source_id'],fellowship['faq_source_id'],fellowship['eligibility_source_id']]:
            self.assertEqual(sources_by_id[source_id]['checked'],'2026-10-31')

        self.assertEqual(incubator['verified'],'2026-10-31')
        self.assertEqual(incubator['deadline'],'2026-11-20')
        self.assertIn('no AI feature at the core',incubator['next_action'])
        self.assertIn('no-go',incubator['status'])
        for source_id in [incubator['source_id'],incubator['faq_source_id']]:
            self.assertEqual(sources_by_id[source_id]['checked'],'2026-10-31')


if __name__=='__main__': unittest.main()
