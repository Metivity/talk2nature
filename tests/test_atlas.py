import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from talk2nature.atlas import public_atlas, atlas_goals, group
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
        parrot_home=records['parrot-video']
        self.assertEqual(parrot_home['location_status'],'not_applicable')
        self.assertEqual(parrot_home['locations'],[])
        self.assertIn('home-based study',parrot_home['location_note'])
        self.assertIn('conference venue, not the study location',parrot_home['location_note'])
        self.assertEqual(records['birdnet']['location_status'],'not_applicable')
        inat_sounds=records['inat-sounds-2024']
        self.assertEqual(inat_sounds['location_status'],'not_applicable')
        self.assertEqual(inat_sounds['locations'],[])
        self.assertIn('global compilation',inat_sounds['location_note'])
        wabad=records['wabad-global-bird-acoustic-dataset']
        self.assertEqual(wabad['location_status'],'not_applicable')
        self.assertEqual(wabad['locations'],[])
        self.assertIn('single field region',wabad['location_note'])
        self.assertIn(338,wabad['source_ids'])
        ceb=records['central-european-birds-dataset-v1-1']
        self.assertEqual({location['place_id'] for location in ceb['locations']},{'germany-country','greece-country'})
        self.assertIn('Xeno-Canto',ceb['location_note'])
        self.assertTrue({441,442} <= set(ceb['source_ids']))
        for place_id,coordinates in [('germany-country',(51.5,10.5)),('greece-country',(39.0,22.0))]:
            place=next(p for p in self.places['places'] if p['id']==place_id)
            self.assertEqual(place['precision'],'country')
            self.assertEqual((place['latitude'],place['longitude']),coordinates)
        rook=records['rook-observed-context-corpus']
        self.assertEqual(rook['location_status'],'mapped')
        self.assertEqual({location['place_id'] for location in rook['locations']},{'strasbourg-region','cambridge-region-uk'})
        self.assertEqual(rook['source_ids'],[452,453,454,455])
        self.assertEqual({location['source_id'] for location in rook['locations']},{452})
        for place_id in ('strasbourg-region','cambridge-region-uk'):
            place=next(p for p in self.places['places'] if p['id']==place_id)
            self.assertEqual(place['precision'],'region')
        magpie=records['oriental-magpie-robin-urban-noise-2025']
        self.assertEqual(magpie['location_status'],'mapped')
        self.assertEqual({location['place_id'] for location in magpie['locations']},{'kathmandu-valley-nepal'})
        self.assertIn('coarse Kathmandu Valley',magpie['location_note'])
        bat_origin=records['egyptian-fruit-bat-data']
        self.assertEqual(bat_origin['location_status'],'mapped')
        self.assertEqual(bat_origin['locations'],[{
            'place_id':'herzliya',
            'role':'animal_origin',
            'source_id':142,
            'locator':'Methods: Animal retrieval and care',
            'basis':'The data descriptor states adult bats were caught in a natural roost near Herzliya, Israel. This existing coarse region marker shows animal origin, not the recording chambers, exact roost, or an individual animal location.'
        }])
        self.assertIn('recording chambers are not assigned',bat_origin['location_note'])
        herzliya=next(p for p in self.places['places'] if p['id']=='herzliya')
        self.assertEqual(herzliya['precision'],'region')
        self.assertEqual(sum(bool(r['locations']) for r in atlas['records']),47)
        pteroset=records['pteroset-detection-benchmark-2026']
        self.assertEqual({location['place_id'] for location in pteroset['locations']},{'pivijay-study-region','puerto-asis-study-region'})
        self.assertIn('municipal reference points',pteroset['location_note'])
        self.assertTrue({417,418} <= set(pteroset['source_ids']))
        openwhistle=records['openwhistle-dolphin-benchmark']
        self.assertEqual(openwhistle['location_status'],'mapped')
        self.assertEqual(openwhistle['locations'][0]['place_id'],'eilat-study-region')
        self.assertIn(425,openwhistle['source_ids'])
        el_silencio=records['el-silencio-multitaxon-dataset-2025']
        self.assertEqual(el_silencio['location_status'],'mapped')
        self.assertEqual(el_silencio['locations'][0]['place_id'],'colombia-country')
        self.assertEqual(el_silencio['locations'][0]['role'],'study_region')
        self.assertEqual(el_silencio['locations'][0]['source_id'],328)
        self.assertIn(439,el_silencio['source_ids'])
        colombia=next(p for p in self.places['places'] if p['id']=='colombia-country')
        self.assertEqual(colombia['precision'],'country')
        self.assertEqual((colombia['latitude'],colombia['longitude']),(4.0,-73.3))
        self.assertIn('country-scale',el_silencio['location_note'])
        hyena=records['hyenaset-event-detection-benchmark']
        self.assertEqual(hyena['location_status'],'mapped')
        self.assertEqual(hyena['locations'][0]['place_id'],'kenya')
        self.assertEqual(hyena['locations'][0]['role'],'study_region')
        self.assertEqual(hyena['locations'][0]['source_id'],296)
        self.assertIn('country-scale',hyena['location_note'])
        self.assertNotIn('reserve',next(p for p in self.places['places'] if p['id']=='kenya')['label'].lower())
        kenya=next(p for p in self.places['places'] if p['id']=='kenya')
        self.assertEqual(kenya['precision'],'country')
        self.assertEqual((kenya['latitude'],kenya['longitude']),(1.0,38.0))
        self.assertEqual(records['great-green-macaw-vocal-development-2026']['locations'][0]['place_id'],'costa-rica')
        playback=records['parrot-vocal-imitation-addressing-2012']
        self.assertEqual(playback['group'],'birds')
        self.assertEqual(playback['locations'][0]['place_id'],'costa-rica')
        self.assertEqual(playback['observation_period']['start_year'],2007)
        humpback=records['humpback-tag-accelerometer-caller-attribution-2026']
        self.assertEqual(humpback['location_status'],'mapped')
        self.assertEqual(humpback['locations'][0]['place_id'],'stellwagen-bank-ma-bay')
        self.assertEqual(humpback['locations'][0]['source_id'],486)
        self.assertEqual(humpback['observation_period']['start_year'],2023)
        self.assertEqual(humpback['observation_period']['end_year'],2025)
        stellwagen=next(p for p in atlas['places'] if p['id']=='stellwagen-bank-ma-bay')
        self.assertEqual(stellwagen['precision'],'region')
        self.assertEqual((stellwagen['latitude'],stellwagen['longitude']),(42.4,-70.4))
        self.assertEqual(len(atlas['places']),51)
        lark=records['duponts-lark-vocal-types-2026']
        self.assertEqual(lark['locations'][0]['place_id'],'spain')
        self.assertIn('country-level',lark['location_note'])
        spain=next(p for p in self.places['places'] if p['id']=='spain')
        self.assertEqual(spain['precision'],'country')
        self.assertEqual(self.atlas(list(reversed(self.notes))),atlas)

    def test_species_level_taxa_map_to_their_biological_group(self):
        self.assertEqual(group('Orange-fronted conure (Eupsittula canicularis)'), 'birds')
        self.assertEqual(group('Yellow-naped amazon (Amazona auropalliata)'), 'birds')
        self.assertEqual(group('Egyptian fruit bat (Rousettus aegyptiacus)'), 'mammals')
        self.assertEqual(group('Fusarium oxysporum (filamentous fungus)'), 'plants_fungi')
        self.assertEqual(group('Amphibians'), 'other_animals')
    def test_observation_dates_are_distinct_from_publication_and_origin_from_study_site(self):
        rows={r['id']:r for r in self.atlas()['records']}
        self.assertEqual(rows['honeybee-dance-history']['source_year'],1973)
        self.assertEqual(rows['honeybee-dance-history']['observation_period']['start_year'],1949)
        self.assertEqual(rows['whale-birth']['source_year'],2026)
        self.assertEqual(rows['whale-birth']['observation_period']['start_year'],2023)
        self.assertEqual(rows['bat-context']['locations'][0]['role'],'animal_origin')
        self.assertEqual(rows['elephant-calls-controls']['source_year'],2026)
        self.assertEqual(rows['duponts-lark-vocal-types-2026']['observation_period']['start_year'],2024)
        self.assertEqual(rows['duponts-lark-vocal-types-2026']['observation_period']['end_year'],2025)
    def test_honeybee_candidate_maps_only_a_coarse_study_region(self):
        atlas=self.atlas(); records={r['id']:r for r in atlas['records']}
        honeybee=records['honeybee-dance-following-2023']
        self.assertEqual(honeybee['location_status'],'mapped')
        self.assertEqual(honeybee['locations'][0]['place_id'],'berlin-study-region')
        self.assertEqual(honeybee['locations'][0]['role'],'study_region')
        self.assertEqual(honeybee['locations'][0]['source_id'],415)
        self.assertEqual((honeybee['observation_period']['start_year'],honeybee['observation_period']['end_year']),(2019,2021))
        self.assertIn('coarse marker',honeybee['location_note'])
        self.assertIn('coordinates',honeybee['location_note'])
        berlin=next(p for p in atlas['places'] if p['id']=='berlin-study-region')
        self.assertEqual(berlin['precision'],'region')
        self.assertEqual((berlin['latitude'],berlin['longitude']),(52.5,13.4))
    def test_openwhistle_maps_only_a_rounded_eilat_study_region(self):
        atlas=self.atlas(); records={r['id']:r for r in atlas['records']}
        openwhistle=records['openwhistle-dolphin-benchmark']
        self.assertEqual(openwhistle['location_status'],'mapped')
        self.assertEqual(openwhistle['locations'][0]['role'],'study_region')
        self.assertEqual(openwhistle['locations'][0]['source_id'],340)
        self.assertIn('Section 3 Data Collection',openwhistle['locations'][0]['locator'])
        self.assertIn('rounded',openwhistle['locations'][0]['basis'])
        self.assertIn('voluntary',openwhistle['location_note'])
        self.assertIn('hydrophone deployments',openwhistle['location_note'])
        eilat=next(p for p in atlas['places'] if p['id']=='eilat-study-region')
        self.assertEqual(eilat['precision'],'region')
        self.assertEqual((eilat['latitude'],eilat['longitude']),(29.6,34.9))
        source={s['id']:s for s in atlas['sources']}[425]
        self.assertEqual(source['url'],'https://www.geonames.org/295277/eilat.html')
        self.assertNotIn('29.55805',json.dumps(atlas['places']))
        self.assertNotIn('34.94821',json.dumps(atlas['places']))
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
            self.assertIn('47 <span>/ 20 goal</span>',goals)
            self.assertIn('aria-label="20 research notes with verified places: 47 current; goal 20"',goals)
            self.assertIn('3 <span>/ 3 goal</span>',goals)
            self.assertEqual(goals.count('Target reached'),2)
            self.assertIn('Needs a scientific reviewer',goals)
            self.assertIn('Three historical source notes',goals)
            self.assertEqual(len(json.loads((Path(d)/'research/atlas/catalog.json').read_text())['records']),len(self.notes))
            mammalps_page=(Path(d)/'research/mammalps-audio-behavior-benchmark/index.html').read_text()
            self.assertIn('June–August 2023',mammalps_page)
            self.assertIn('August–October 2023',mammalps_page)

    def test_expanded_locations_retain_multi_site_and_date_boundaries(self):
        rows={r['id']:r for r in self.atlas()['records']}
        expected={'dolphingemma':{'bahamas'},'dog-barks':{'tepic','puebla'},
                  'parrot-data-feasibility':{'barcelona'},'plant-sounds':{'tel-aviv'},
                  'reef-sound-recruitment':{'lizard-island'},'honeyguide-human-cooperation':{'niassa'},
                  'wild-parrot-duet-structure-2026':{'costa-rica'},
                  'monk-parakeet-social-structure-2025':{'barcelona'},
                  'duponts-lark-vocal-types-2026':{'spain'},
                  'heterospecific-mobbing-sequences':{'lyon-region'}}
        for key,places in expected.items():
            self.assertEqual({l['place_id'] for l in rows[key]['locations']},places)
        self.assertIsNone(rows['dolphingemma']['observation_period'])
        self.assertIsNone(rows['dog-barks']['observation_period'])
        self.assertEqual(rows['reef-sound-recruitment']['source_year'],2019)
        self.assertEqual(rows['reef-sound-recruitment']['observation_period']['start_year'],2017)
        self.assertEqual(rows['parrot-data-feasibility']['observation_period']['end_year'],2021)
        self.assertIsNone(rows['honeyguide-human-cooperation']['observation_period'])
        budgerigar=rows['budgerigar-vocal-sociality-data']
        self.assertEqual([l['place_id'] for l in budgerigar['locations']],['las-cruces'])
        self.assertEqual(budgerigar['observation_period']['start_year'],2020)
        self.assertEqual(budgerigar['observation_period']['end_year'],2021)
        sources={s['id']:s for s in self.atlas()['sources']}
        mammalps=rows['mammalps-audio-behavior-benchmark']
        self.assertEqual([l['place_id'] for l in mammalps['locations']],['swiss-national-park'])
        self.assertIsNone(mammalps['observation_period'])
        self.assertIn('conflict',mammalps['location_note'])
        heterospecific=rows['heterospecific-mobbing-sequences']
        self.assertEqual(heterospecific['locations'][0]['source_id'],268)
        self.assertEqual(heterospecific['observation_period']['start_year'],2022)
        lyon=next(p for p in self.atlas()['places'] if p['id']=='lyon-region')
        self.assertEqual(lyon['precision'],'region')
        self.assertIn('August–October 2023',mammalps['limitations'])
        self.assertIn('403',mammalps['review_depth'])
        self.assertIn('openaccess.thecvf.com',sources[132]['url'])
        self.assertIn('supplemental',sources[133]['url'])
        retrieval=rows['prompting-mammalps-video-retrieval']
        self.assertEqual([l['place_id'] for l in retrieval['locations']],['swiss-national-park'])
        self.assertEqual(retrieval['observation_period']['start_year'],2023)
        self.assertEqual(retrieval['observation_period']['end_year'],2024)
        self.assertIn('do not compare identical query sets',retrieval['limitations'])
        self.assertIn('135 ecology-informed queries',retrieval['finding'])
        self.assertEqual(retrieval['source_ids'],[137,138,139,140,141])
        self.assertIn('2024.lrec-main.1432.pdf',sources[21]['review_url'])
        parrotlet=rows['parrotlet-vocal-babbling-development']
        self.assertEqual([l['place_id'] for l in parrotlet['locations']],['guarico-venezuela'])
        self.assertEqual(parrotlet['observation_period']['start_year'],2017)
        self.assertEqual(parrotlet['observation_period']['end_year'],2018)
        self.assertIn('not yet integrated',parrotlet['finding'])
        self.assertIn('2.56 GB',parrotlet['limitations'])
        self.assertEqual(parrotlet['source_ids'],[134,135,136,444])
        self.assertIn('does not check scientific validity',parrotlet['limitations'])
        self.assertIn('HTTP 403',parrotlet['limitations'])
        wild_parrot=rows['wild-parrot-duet-structure-2026']
        self.assertEqual(wild_parrot['observation_period']['start_year'],2006)
        self.assertEqual(wild_parrot['observation_period']['end_year'],2008)
        self.assertEqual(wild_parrot['locations'][0]['role'],'study_region')
        monk=rows['monk-parakeet-social-structure-2025']
        self.assertEqual(monk['locations'][0]['source_id'],344)
        self.assertEqual(monk['locations'][0]['role'],'study_region')
        self.assertEqual(monk['locations'][0]['place_id'],'barcelona')
        self.assertEqual(monk['observation_period']['locator'],'Methods section 2.1, Study system')
        self.assertEqual((monk['observation_period']['start_year'],monk['observation_period']['end_year']),(2020,2021))
        self.assertIn('does not plot a park, nest or UTM coordinate',monk['location_note'])
        self.assertNotIn('Parc de la Ciutadella',json.dumps(monk))
        self.assertEqual(next(p for p in self.atlas()['places'] if p['id']=='barcelona')['precision'],'region')
        identity=rows['monk-parakeet-population-identity-2023']
        self.assertEqual({l['place_id'] for l in identity['locations']},{'uruguay','united-states','costa-rica'})
        self.assertEqual((identity['observation_period']['start_year'],identity['observation_period']['end_year']),(1994,2019))
        self.assertIn('training accuracy',identity['limitations'])
        self.assertIn('unseen-caller accuracy',identity['limitations'])
        costa_rica=next(p for p in self.atlas()['places'] if p['id']=='costa-rica')
        self.assertEqual(costa_rica['precision'],'country')
        wytham=rows['wytham-great-tit-song-structure-2024']
        self.assertEqual(wytham['location_status'],'mapped')
        self.assertEqual(wytham['locations'][0]['source_id'],367)
        self.assertEqual(wytham['locations'][0]['place_id'],'wytham-woods')
        self.assertEqual(wytham['locations'][0]['role'],'study_region')
        self.assertIn('no coordinate values or data files were inspected or plotted',wytham['location_note'])
        self.assertNotIn('nestboxes.csv',json.dumps(wytham))
        self.assertEqual(next(p for p in self.atlas()['places'] if p['id']=='wytham-woods')['precision'],'region')

    def test_common_endophyte_transfer_stays_distinct_from_communication_and_unlicensed_assets(self):
        note=next(n for n in self.notes if n['slug']=='common-endophyte-networks-resource-transfer')
        self.assertEqual(note['source_ids'],[270,271])
        self.assertIn('cannot establish plant-to-plant communication',note['limitations'].lower())
        self.assertEqual(note['atlas']['location_status'],'not_applicable')
        self.assertEqual(note['atlas']['locations'],[])
        path=next(p for p in load('learning-paths')['paths'] if p['id']=='multimodal')
        self.assertIn(note['slug'],path['notes'])
        resources=json.loads((ROOT/'research/resources.json').read_text())['resources']
        by_id={r['id']:r for r in resources}
        paper=by_id['common-endophyte-networks-paper-2026']
        self.assertIn('CC BY 4.0',paper['rights']['license'])
        for key in ('common-endophyte-networks-data-2026','common-endophyte-networks-code-2026'):
            resource=by_id[key]
            self.assertEqual(resource['acquisition'],'metadata_only')
            self.assertEqual(resource['files'],[])
            self.assertEqual(resource['rights']['research_use'],'unresolved')
            self.assertEqual(resource['rights']['commercial_use'],'unresolved')

    def test_goals_compute_coverage_and_keep_scientific_gates_as_plans(self):
        plan=load('atlas-goals');atlas=self.atlas();goals=atlas_goals(atlas,plan)['goals']
        self.assertEqual((goals[0]['current'],goals[0]['target']),(47,20))
        self.assertEqual(goals[1]['current'],3)
        self.assertTrue(all('current' not in g for g in goals[2:]))
        fewer=deepcopy(atlas);fewer['records']=[r for r in fewer['records'] if r['id'] not in {'dog-barks','budgerigar-vocal-sociality-data','mammalps-audio-behavior-benchmark','parrotlet-vocal-babbling-development','wild-parrot-duet-structure-2026'}]
        self.assertEqual(atlas_goals(fewer,plan)['goals'][0]['current'],42)
        self.assertEqual(atlas_goals(fewer,plan)['goals'][0]['status'],'Target reached')
        mapped=[r for r in atlas['records'] if r['locations']]
        below=deepcopy(atlas); below['records']=[r for r in atlas['records'] if not r['locations']]+mapped[:19]
        below_goal=atlas_goals(below,plan)['goals'][0]
        self.assertEqual((below_goal['current'],below_goal['status']),(19,'In progress'))
        with tempfile.TemporaryDirectory() as temp:
            output=Path(temp)
            build(output,'https://fixture.github.io/talk2nature',True)
            page=(output/'research/atlas/goals/index.html').read_text()
            self.assertIn('47 <span>/ 20 goal</span>',page)
            self.assertIn('aria-label="20 research notes with verified places: 47 current; goal 20"',page)
        for field,value in [('metric','unverified_uploads'),('target',True),('target',0),('path','https://elsewhere.example/'),('path','//elsewhere/')]:
            changed=deepcopy(plan);changed['goals'][0][field]=value
            with self.assertRaises(ValueError):atlas_goals(atlas,changed)

    def test_historical_studies_keep_sampling_windows_and_later_review_distinct(self):
        atlas=self.atlas();rows={r['id']:r for r in atlas['records']}
        whale=rows['humpback-song-history']
        self.assertEqual(whale['source_year'],1985)
        self.assertEqual(whale['year_basis'],'Original study year')
        self.assertEqual((whale['observation_period']['start_year'],whale['observation_period']['end_year']),(1957,1975))
        self.assertIn('13 sampled years',whale['observation_period']['label'])
        self.assertIn(120,whale['source_ids'])
        vervet=rows['vervet-alarm-development']
        self.assertEqual(vervet['source_year'],1980)
        self.assertIn(429,vervet['source_ids'])
        self.assertEqual({item['place_id'] for item in vervet['locations']},{'amboseli','kwazulu-natal'})
        self.assertEqual(vervet['place_labels'],['Amboseli region, Kenya','KwaZulu-Natal region, South Africa'])
        self.assertIn('precise wildlife-site coordinates are deliberately not reproduced',vervet['location_note'])
        kwa=next(place for place in atlas['places'] if place['id']=='kwazulu-natal')
        self.assertEqual(kwa['precision'],'region')
        for key in ['vervet-alarm-development','raven-object-gestures','wolf-howling-context','dolphin-signature-addressing']:
            self.assertIsNone(rows[key]['observation_period'])
        fish=rows['grouper-moray-coordination']
        self.assertEqual(fish['source_year'],2006)
        self.assertEqual(fish['observation_period']['end_year'],2004)
        self.assertEqual(fish['locations'][0]['source_id'],117)
