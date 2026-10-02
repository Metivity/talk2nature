"""Behavioral API contracts inherited by both SQLite and PostgreSQL suites."""
from unittest.mock import patch
import json

from admin.app import create_app
from fastapi.testclient import TestClient


class LineageCases:
    def lineage_setup(self):
        self.login()
        study, session = self.start_study_session()
        obs = self.submit(study_session_id=session['id'], session_id=session['id'])
        audio = self.media_fixture(obs)
        a = self.post('/api/media', audio)
        self.assertEqual(a.status_code, 201, a.text)
        video = {**audio, 'modality':'video', 'codec':'h264', 'sample_rate':None, 'frame_rate':30, 'sha256':'b'*64}
        v = self.post('/api/media', video)
        self.assertEqual(v.status_code, 201, v.text)
        align = {'audio_id':a.json()['id'], 'video_id':v.json()['id'], 'offset_ms':50, 'drift_ppm':10,
                 'uncertainty_ms':5, 'audio_start_ms':100, 'audio_end_ms':900, 'method':'synthetic_fixture_clock',
                 'method_version':'fixture-v1', 'synthetic':True}
        paired = self.post('/api/media-alignments', align)
        self.assertEqual(paired.status_code, 201, paired.text)
        return study, session, obs, a.json(), v.json(), paired.json(), align

    def media_fixture(self, obs, **changes):
        return {'observation_id':obs, 'modality':'audio', 'sha256':'a'*64, 'byte_count':32044,
                'duration_ms':1000, 'codec':'pcm_s16le', 'sample_rate':16000, 'device_alias':'invented-device',
                'descriptor_kind':'invented_fixture_no_object', 'synthetic':True, **changes}

    def registered_run(self):
        setup = self.lineage_setup()
        study, session, obs, a, v, pair, align = setup
        self.assertEqual(self.accept(obs).status_code, 200)
        release = self.post('/api/releases', {'ids':[obs]}).json()
        body = {'release_id':release['id'], 'media_ids':[a['id'],v['id']], 'alignment_ids':[pair['id']],
                'code_revision':'c'*40, 'checkpoint_sha256':'d'*64, 'checkpoint_license':'synthetic-fixture-only',
                'environment_sha256':'e'*64, 'seed':7, 'splits':[{'observation_id':obs, 'partition':'test'}],
                'purpose':'synthetic_pipeline_rehearsal', 'synthetic':True}
        r = self.post('/api/model-runs', body)
        self.assertEqual(r.status_code, 201, r.text)
        result = {'run_id':r.json()['id'], 'media_id':a['id'], 'start_ms':100, 'end_ms':500,
                  'probabilities':{'feeding':0.6,'moving':0.4}, 'abstained':True,
                  'calibration':'unvalidated_synthetic', 'synthetic':True}
        return setup, release, body, r.json(), result

    def test_lineage_restarts_with_frozen_inputs_and_typed_graph(self):
        setup, release, body, run, result = self.registered_run()
        response = self.post('/api/model-results', result)
        self.assertEqual(response.status_code, 201, response.text)
        self.assertFalse(run['executed'])
        app = create_app(self.settings, clock=lambda:self.timestamp)
        with TestClient(app, base_url='http://localhost:4180') as client:
            client.cookies.update(self.client.cookies)
            inventory = client.get('/api/lineage').json()
            spec = inventory['model_runs'][0]['payload']
            self.assertEqual(spec['release_fingerprint'], release['fingerprint'])
            self.assertEqual(spec['input_fingerprints'][setup[3]['id']], setup[3]['fingerprint'])
            self.assertTrue(inventory['model_results'][0]['payload']['abstained'])
            graph = client.get('/api/knowledge-graph').json()
        kinds = {n['kind'] for n in graph['nodes']}
        self.assertTrue({'media','alignment','model_run','model_result','study','session','observation','release'} <= kinds)
        self.assertTrue({'documents','captured_in','aligns','uses_media','uses_release','produces','predicts_on'} <= {e['relation'] for e in graph['edges']})
        ids = {n['id'] for n in graph['nodes']}
        self.assertTrue(all(e['from'] in ids and e['to'] in ids for e in graph['edges']))
        self.assertNotIn('invented-device', json.dumps(graph))
        self.assertNotIn('probabilities', json.dumps(graph))
        self.assertEqual(self.client.get('/api/lineage').headers['cache-control'], 'no-store')

    def test_lineage_real_data_uploads_and_unreviewed_models_stay_closed(self):
        setup = self.lineage_setup(); obs, a, v, pair, align = setup[2:]
        self.assertEqual(self.post('/api/media', self.media_fixture(obs, synthetic=False)).status_code,409)
        self.assertEqual(self.post('/api/media', self.media_fixture(obs, object_key='private/file.wav')).status_code,422)
        self.assertEqual(self.post('/api/media', self.media_fixture(obs, descriptor_kind='recording')).status_code,422)
        self.assertEqual(self.post('/api/media-alignments', {**align, 'synthetic':False}).status_code,409)
        self.assertEqual(self.post('/api/releases', {'ids':[obs]}).status_code,409)
        self.assertEqual(len(self.client.get('/api/lineage').json()['research_media']),2)
        self.assertEqual(self.client.post('/api/media', json=self.media_fixture(obs), headers={'Origin':'http://localhost:4180'}).status_code,403)
        self.client.cookies.clear()
        self.assertEqual(self.client.get('/api/lineage').status_code,401)
        self.assertEqual(self.post('/api/media', self.media_fixture(obs)).status_code,401)

    def test_media_modality_hash_scope_and_review_freeze(self):
        setup = self.lineage_setup(); obs, a, v, pair, align = setup[2:]
        for changes in ({'sha256':'not-a-hash'},{'sample_rate':None},{'frame_rate':30},{'byte_count':True},
                        {'duration_ms':0},{'modality':'video'},{'duration_ms':120001}):
            with self.subTest(changes=changes):
                self.assertEqual(self.post('/api/media', self.media_fixture(obs, **changes)).status_code,422)
        unlinked = self.submit()
        self.assertEqual(self.post('/api/media', self.media_fixture(unlinked)).status_code,409)
        self.accept(obs)
        self.assertEqual(self.post('/api/media', self.media_fixture(obs)).status_code,409)
        self.assertEqual(self.post('/api/media-alignments', align).status_code,409)

    def test_alignment_checks_modality_session_interval_drift_and_uncertainty(self):
        setup = self.lineage_setup(); obs, a, v, pair, align = setup[2:]
        for changes, code in [({'audio_id':v['id'],'video_id':a['id']},409), ({'audio_end_ms':50},422),
                              ({'offset_ms':500},422),({'uncertainty_ms':200},422),({'drift_ppm':20000},422)]:
            with self.subTest(changes=changes):
                self.assertEqual(self.post('/api/media-alignments',{**align,**changes}).status_code,code)
        _, other_session = self.start_study_session()
        other_obs = self.submit(study_session_id=other_session['id'],session_id=other_session['id'])
        other = self.post('/api/media',self.media_fixture(other_obs)).json()
        self.assertEqual(self.post('/api/media-alignments',{**align,'audio_id':other['id']}).status_code,409)

    def test_model_specs_require_exact_release_inputs_splits_and_alignment(self):
        setup, release, body, run, result = self.registered_run()
        for changes, code in [({'synthetic':False},409),({'media_ids':[body['media_ids'][0]]*2},422),
                              ({'alignment_ids':[]},409),({'media_ids':['missing']},409),
                              ({'splits':[{'observation_id':'absent','partition':'test'}]},422),
                              ({'splits':body['splits']*2},422),({'release_id':'absent'},409),
                              ({'purpose':'animal_translation'},422),({'alignment_ids':['missing']},409)]:
            with self.subTest(changes=changes):
                self.assertEqual(self.post('/api/model-runs',{**body,**changes}).status_code,code)
        self.assertEqual(len(self.client.get('/api/lineage').json()['model_runs']),1)

    def test_model_results_are_bounded_and_do_not_change_observed_labels(self):
        setup, release, body, run, result = self.registered_run()
        before = self.client.get('/api/observations').json()
        for changes, code in [({'synthetic':False},409),({'end_ms':1001},422),({'start_ms':600},422),({'start_ms':0},422),
                              ({'probabilities':{'feeding':0.6,'moving':0.8}},422),
                              ({'probabilities':{'feeding':1}},422),({'probabilities':{'resting':0.4,'feeding':0.6}},422),
                              ({'media_id':'unknown'},409),({'calibration':'validated'},422)]:
            with self.subTest(changes=changes):
                self.assertEqual(self.post('/api/model-results',{**result,**changes}).status_code,code)
        self.assertEqual(self.post('/api/model-results', result).status_code,201)
        self.assertEqual(self.client.get('/api/observations').json(),before)

    def test_grouped_splits_and_all_multimodal_inputs_are_checked(self):
        setup = self.lineage_setup(); study, session, obs, a, v, pair, align = setup
        other = self.submit(study_session_id=session['id'],session_id=session['id'])
        second_audio = self.post('/api/media',self.media_fixture(other)).json()
        second_pair = self.post('/api/media-alignments',{**align,'audio_id':second_audio['id']}).json()
        self.accept(obs); self.accept(other)
        release = self.post('/api/releases',{'ids':[obs,other]}).json()
        body = {'release_id':release['id'],'media_ids':[a['id'],v['id'],second_audio['id']],
                'alignment_ids':[pair['id'],second_pair['id']], 'code_revision':'c'*40,'checkpoint_sha256':'d'*64,
                'checkpoint_license':'invented','environment_sha256':'e'*64,'seed':0,
                'splits':[{'observation_id':obs,'partition':'train'},{'observation_id':other,'partition':'test'}],
                'purpose':'synthetic_pipeline_rehearsal','synthetic':True}
        self.assertEqual(self.post('/api/model-runs',body).status_code,409)
        body['splits'][0]['partition']='test'
        self.assertEqual(self.post('/api/model-runs',{**body,'alignment_ids':[pair['id']]}).status_code,409)
        self.assertEqual(self.post('/api/model-runs',{**body,'media_ids':[a['id'],v['id']]}).status_code,409)
        registered = self.post('/api/model-runs',body)
        self.assertEqual(registered.status_code,201,registered.text)
        result = {'run_id':registered.json()['id'],'media_id':second_audio['id'],'start_ms':100,'end_ms':500,
                  'probabilities':{'feeding':0.5,'moving':0.5},'abstained':True,
                  'calibration':'unvalidated_synthetic','synthetic':True}
        self.assertEqual(self.post('/api/model-results',result).status_code,201)
        # Withdrawing one input invalidates results on other inputs of that run.
        self.assertEqual(self.post('/api/observations/'+obs+'/withdraw',{'version':3}).status_code,200)
        inventory=self.client.get('/api/lineage').json()
        self.assertEqual(inventory['model_results'][0]['state'],'withdrawn')
        self.assertEqual(next(r for r in inventory['research_media'] if r['id']==second_audio['id'])['state'],'active')

    def test_new_lineage_mutations_require_auth_and_csrf(self):
        setup, release, body, run, result = self.registered_run()
        mutations = [('/api/media',self.media_fixture(setup[2])),('/api/media-alignments',setup[6]),
                     ('/api/model-runs',body),('/api/model-results',result)]
        for path, data in mutations:
            self.assertEqual(self.client.post(path,json=data,headers={'Origin':'http://localhost:4180'}).status_code,403)
        self.client.cookies.clear()
        for path, data in mutations:
            self.assertEqual(self.post(path,data).status_code,401)

    def test_withdrawal_scrubs_all_derivatives_and_prevents_reuse(self):
        setup, release, body, run, result = self.registered_run()
        self.assertEqual(self.post('/api/model-results',result).status_code,201)
        obs = setup[2]
        self.assertEqual(self.post('/api/observations/'+obs+'/withdraw',{'version':3}).status_code,200)
        inventory = self.client.get('/api/lineage').json()
        for table in inventory:
            for row in inventory[table]:
                self.assertEqual(row['payload'],{})
        self.assertEqual(inventory['model_runs'][0]['state'],'invalidated')
        self.assertEqual(self.post('/api/model-results',result).status_code,409)
        self.assertEqual(self.post('/api/model-runs',body).status_code,409)
        graph = self.client.get('/api/knowledge-graph').json()
        self.assertFalse({'media','alignment','model_result'} & {n['kind'] for n in graph['nodes']})
        self.assertFalse(any(e['from']=='run:'+run['id'] for e in graph['edges']))
        self.assertEqual(self.client.get('/api/releases/'+release['id']).status_code,410)

    def test_withdrawal_rolls_back_when_derivative_invalidation_fails(self):
        from admin.lineage import invalidate_lineage
        setup, release, body, run, result = self.registered_run()
        def fail(db, key, now):
            invalidate_lineage(db,key,now)
            raise RuntimeError('Synthetic failure before commit')
        with patch('admin.app.invalidate_lineage',side_effect=fail), self.assertRaises(RuntimeError):
            self.post('/api/observations/'+setup[2]+'/withdraw',{'version':3})
        inventory = self.client.get('/api/lineage').json()
        self.assertEqual(inventory['model_runs'][0]['state'],'registered')
        self.assertTrue(all(r['state']=='active' for r in inventory['research_media']))
        self.assertEqual(self.client.get('/api/releases/'+release['id']).status_code,200)

    def test_lineage_detects_media_and_release_tampering(self):
        setup, release, body, run, result = self.registered_run()
        with self.app.state.store.connect() as db:
            db.execute("UPDATE research_media SET payload='{}' WHERE id=?",(setup[3]['id'],))
        self.assertEqual(self.post('/api/model-results',result).status_code,409)
        self.assertEqual(self.post('/api/model-runs',body).status_code,409)
        with self.app.state.store.connect() as db:
            db.execute("UPDATE releases SET fingerprint='tampered' WHERE id=?",(release['id'],))
        self.assertEqual(self.post('/api/model-runs',body).status_code,409)
