import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from talk2nature.atlas import public_atlas
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
        self.assertEqual(sum(bool(r['locations']) for r in atlas['records']),8)
        self.assertEqual(len(atlas['places']),7)
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
            self.assertEqual(len(json.loads((Path(d)/'research/atlas/catalog.json').read_text())['records']),len(self.notes))
