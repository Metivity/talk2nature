import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from talk2nature.atlas import public_atlas, atlas_goals
from talk2nature.knowledge import catalog_graph
from admin.catalog import read_catalog
from web.build import ROOT, build, load


class AtlasTests(unittest.TestCase):
    def setUp(self):
        self.notes=load('research'); self.sources=load('sources'); self.places=load('atlas-places')
    def atlas(self,notes=None,places=None):
        return public_atlas(self.notes if notes is None else notes,self.sources,self.places if places is None else places)
    def test_complete_catalog_and_evidence_versions_with_explicit_missing_locations(self):
        atlas=self.atlas(); records={r['id']:r for r in atlas['records']}
        self.assertEqual(set(records),{n['slug'] for n in self.notes})
        graph=catalog_graph(read_catalog()); versions={n['id'] for n in graph['nodes']}
        self.assertTrue(all(r['evidence_version'] in versions for r in atlas['records']))
        self.assertEqual(records['parrot-community-data']['location_status'],'pending')
        self.assertEqual(records['parrot-community-data']['locations'],[])
        self.assertEqual(records['birdnet']['location_status'],'not_applicable')
        self.assertEqual(sum(bool(r['locations']) for r in atlas['records']),20)
        self.assertEqual(len(atlas['places']),20)
        self.assertEqual(self.atlas(list(reversed(self.notes))),atlas)
    def test_observation_dates_are_distinct_from_publication_and_origin_from_study_site(self):
        rows={r['id']:r for r in self.atlas()['records']}
        self.assertEqual(rows['honeybee-dance-history']['source_year'],1973)
        self.assertEqual(rows['honeybee-dance-history']['observation_period']['start_year'],1949)
        self.assertEqual(rows['whale-birth']['source_year'],2026)
        self.assertEqual(rows['whale-birth']['observation_period']['start_year'],2023)
        self.assertEqual(rows['bat-context']['locations'][0]['role'],'animal_origin')
        self.assertEqual(rows['elephant-calls-controls']['source_year'],2026)
    def test_precise_or_unreviewed_locations_and_missing_citations_fail_closed(self):
        for mutation in [lambda p:p.update(precision='exact'),lambda p:p.update(latitude=47.8123),lambda p:p.update(longitude=181),lambda p:p.update(latitude=True),lambda p:p.update(latitude=float('nan')),lambda p:p.update(private_address='sensitive')]:
            places=deepcopy(self.places);mutation(places['places'][0])
            with self.assertRaises(ValueError):self.atlas(places=places)
        notes=deepcopy(self.notes);n=next(n for n in notes if n['slug']=='bird-call-syntax')
        for mutation in [lambda a:a['locations'][0].update(source_id=109),lambda a:a['locations'][0].update(place_id='missing'),lambda a:a['locations'][0].update(role='author_affiliation'),lambda a:a.update(location_status='pending'),lambda a:a.update(private_note='sensitive')]:
            changed=deepcopy(n);mutation(changed['atlas'])
            with self.assertRaises(ValueError):self.atlas([changed if x['slug']==n['slug'] else x for x in notes])
    def test_observation_period_needs_source_and_cannot_postdate_the_note(self):
        for field,value in [('end_year',2099),('start_year',2000),('source_id',65)]:
            notes=deepcopy(self.notes);n=next(n for n in notes if n['slug']=='honeybee-dance-history');n['atlas']['observation_period'][field]=value
            with self.assertRaises(ValueError):self.atlas(notes)
    def test_projection_excludes_arbitrary_future_private_fields_and_tracks_changes(self):
        notes=deepcopy(self.notes);notes[0]['private_recording']='DO_NOT_EXPORT';after=self.atlas(notes)
        self.assertNotIn('DO_NOT_EXPORT',json.dumps(after));self.assertNotEqual(after['fingerprint'],self.atlas()['fingerprint'])
        places=deepcopy(self.places);places['places'][0]['longitude']+=.1
        self.assertNotEqual(self.atlas(places=places)['fingerprint'],self.atlas()['fingerprint'])
    def test_build_has_readable_no_script_timeline_valid_graph_links_and_public_json(self):
        with tempfile.TemporaryDirectory() as d:
            build(Path(d),'https://fixture.github.io/talk2nature',True)
            html=(Path(d)/'research/atlas/index.html').read_text()
            self.assertIn('1949 orientation trial',html);self.assertIn('Location awaiting review',html)
            self.assertIn('/talk2nature/research/map/#evidence-honeybee-dance-history',html)
            self.assertIn('id="atlas-controls" hidden',html)
            self.assertNotIn('geolocation',html)
            self.assertIn('2024.lrec-main.1432.pdf',html)
            goals=(Path(d)/'research/atlas/goals/index.html').read_text()
            self.assertIn('20 of 20',goals)
            self.assertIn('3 of 3',goals)
            self.assertEqual(goals.count('Target reached'),2)
            self.assertIn('Needs a scientific reviewer',goals)
            self.assertIn('Three historical source notes',goals)
            self.assertEqual(len(json.loads((Path(d)/'research/atlas/catalog.json').read_text())['records']),len(self.notes))

    def test_expanded_locations_retain_multi_site_and_date_boundaries(self):
        rows={r['id']:r for r in self.atlas()['records']}
        expected={'dolphingemma':{'bahamas'},'dog-barks':{'tepic','puebla'},
                  'parrot-data-feasibility':{'barcelona'},'plant-sounds':{'tel-aviv'},
                  'reef-sound-recruitment':{'lizard-island'},'honeyguide-human-cooperation':{'niassa'}}
        for key,places in expected.items():
            self.assertEqual({l['place_id'] for l in rows[key]['locations']},places)
        self.assertIsNone(rows['dolphingemma']['observation_period'])
        self.assertIsNone(rows['dog-barks']['observation_period'])
        self.assertEqual(rows['reef-sound-recruitment']['source_year'],2019)
        self.assertEqual(rows['reef-sound-recruitment']['observation_period']['start_year'],2017)
        self.assertEqual(rows['parrot-data-feasibility']['observation_period']['end_year'],2021)
        self.assertIsNone(rows['honeyguide-human-cooperation']['observation_period'])
        sources={s['id']:s for s in self.atlas()['sources']}
        self.assertIn('2024.lrec-main.1432.pdf',sources[21]['review_url'])

    def test_goals_compute_coverage_and_keep_scientific_gates_as_plans(self):
        plan=load('atlas-goals');atlas=self.atlas();goals=atlas_goals(atlas,plan)['goals']
        self.assertEqual((goals[0]['current'],goals[0]['target']),(20,20))
        self.assertEqual(goals[1]['current'],3)
        self.assertTrue(all('current' not in g for g in goals[2:]))
        fewer=deepcopy(atlas);fewer['records']=[r for r in fewer['records'] if r['id']!='dog-barks']
        self.assertEqual(atlas_goals(fewer,plan)['goals'][0]['current'],19)
        self.assertEqual(atlas_goals(fewer,plan)['goals'][0]['status'],'In progress')
        for field,value in [('metric','unverified_uploads'),('target',True),('target',0),('path','https://elsewhere.example/'),('path','//elsewhere/')]:
            changed=deepcopy(plan);changed['goals'][0][field]=value
            with self.assertRaises(ValueError):atlas_goals(atlas,changed)

    def test_historical_studies_keep_sampling_windows_and_later_review_distinct(self):
        rows={r['id']:r for r in self.atlas()['records']}
        whale=rows['humpback-song-history']
        self.assertEqual(whale['source_year'],1985)
        self.assertEqual(whale['year_basis'],'Original study year')
        self.assertEqual((whale['observation_period']['start_year'],whale['observation_period']['end_year']),(1957,1975))
        self.assertIn('13 sampled years',whale['observation_period']['label'])
        self.assertIn(120,whale['source_ids'])
        self.assertEqual(rows['vervet-alarm-development']['source_year'],1980)
        for key in ['vervet-alarm-development','raven-object-gestures','wolf-howling-context','dolphin-signature-addressing']:
            self.assertIsNone(rows[key]['observation_period'])
        fish=rows['grouper-moray-coordination']
        self.assertEqual(fish['source_year'],2006)
        self.assertEqual(fish['observation_period']['end_year'],2004)
        self.assertEqual(fish['locations'][0]['source_id'],117)
