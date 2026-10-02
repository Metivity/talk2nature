import json
import tempfile
import time
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient
from google.auth import crypt, jwt

from admin.app import create_app, digest
from admin.auth import Settings
from admin.catalog import sync_catalog
from admin.tests.lineage_cases import LineageCases

CLIENT_ID = "test-client.apps.googleusercontent.com"
ORIGIN = "http://localhost:4180"


def fixture(**changes):
    value = {"species":"Cockatiel", "individual_id":"synthetic-bird-01", "session_id":"synthetic-session-01",
             "recorded_at":"2026-09-30T12:00:00+03:00", "context":"feeding", "label_source":"direct_observation",
             "note":"Invented example: bird near food bowl.", "rights":"creator", "rights_evidence":"Invented fixture; no recording exists.",
             "consent_review":True, "consent_training":True, "consent_publication":False, "synthetic":True}
    value.update(changes)
    return value


def study_fixture(**changes):
    value = {'title': 'Synthetic movement study', 'species': 'Cockatiel',
             'question': 'Can visible movement be labeled consistently?',
             'protocol': 'Observe an invented bird without playback and record visible behavior before predictions.',
             'stop_rule': 'Stop on disturbance or uncertainty about permissions.',
             'codebook': {'moving': 'Visible change in position.', 'feeding': 'Visible ingestion of food.'},
             'evidence_keys': ['resource:fixture'], 'method': 'passive_observation', 'synthetic': True}
    value.update(changes)
    return value


class WorkbenchTests(LineageCases, unittest.TestCase):
    def settings_for_test(self):
        return Settings(client_id=CLIENT_ID, database=Path(self.temp.name)/"private"/"admin.sqlite3")

    @classmethod
    def setUpClass(cls):
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        private = key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
        cls.public = key.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo).decode()
        cls.signer = crypt.RSASigner.from_string(private, key_id="test-key")

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.timestamp = int(time.time())
        self.settings = self.settings_for_test()
        self.app = create_app(self.settings, clock=lambda:self.timestamp)
        self.client = TestClient(self.app, base_url=ORIGIN)
        self.addCleanup(self.client.close)
        certs = patch("google.oauth2.id_token._fetch_certs", return_value={"test-key":self.public})
        certs.start()
        self.addCleanup(certs.stop)

    def token(self, **changes):
        config = self.client.get("/auth/config").json()
        claims = {"iss":"https://accounts.google.com", "aud":CLIENT_ID, "iat":int(time.time()), "exp":int(time.time())+3600,
                  "sub":"synthetic-owner-subject", "email":"raviv@metivity.com", "email_verified":True, "hd":"metivity.com", "nonce":config["nonce"]}
        claims.update(changes)
        return jwt.encode(self.signer, claims).decode()

    def login(self, **changes):
        result = self.client.post("/auth/google", json={"credential":self.token(**changes)}, headers={"Origin":ORIGIN})
        if result.status_code == 200:
            self.csrf = self.client.get("/api/me").json()["csrf"]
        return result

    def post(self, path, body):
        return self.client.post(path, json=body, headers={"Origin":ORIGIN,"X-CSRF-Token":self.csrf})

    def submit(self, **changes):
        result = self.post("/api/observations", fixture(**changes))
        self.assertEqual(result.status_code, 201, result.text)
        return result.json()["id"]

    def accept(self, key):
        return self.post(f"/api/observations/{key}/review", {"version":1,"decision":"accept","rights_checked":True,"consent_checked":True,"privacy_checked":True,"label_checked":True})

    def test_every_private_read_requires_authentication(self):
        for path in ["/api/me","/api/observations","/api/releases","/api/releases/guessed","/api/audit",
                     '/api/lineage','/api/knowledge-graph','/api/studies','/api/study-sessions','/api/evidence','/api/evidence/resource:fixture/versions/guessed']:
            with self.subTest(path=path): self.assertEqual(self.client.get(path).status_code,401)
        self.assertEqual(self.client.get("/admin",follow_redirects=False).status_code,303)

    def test_google_button_styles_are_limited_to_signin(self):
        config = self.client.get('/auth/config').json()
        self.assertEqual(config['login_hint'], 'raviv@metivity.com')
        self.assertEqual(set(config), {'ready', 'client_id', 'nonce', 'login_hint'})
        def directives(path):
            return dict(part.strip().split(' ', 1) for part in
                        self.client.get(path).headers['content-security-policy'].split(';'))
        signin = directives('/')
        self.assertIn("'unsafe-inline'", signin['style-src'])
        self.assertNotIn("'unsafe-inline'", signin['script-src'])
        self.assertEqual(self.login().status_code, 200)
        for path in ['/admin', '/privacy', '/api/me', '/assets/signin.js']:
            with self.subTest(path=path):
                policy = directives(path)
                self.assertNotIn("'unsafe-inline'", policy['style-src'])
                self.assertNotIn("'unsafe-inline'", policy['script-src'])

    def test_every_private_write_requires_authentication(self):
        for path,body in [("/api/observations",fixture()),("/api/releases",{"ids":["x"]}),
                          ("/api/observations/x/review",{"version":1,"decision":"reject"}),
                          ("/api/observations/x/withdraw",{"version":1}),("/auth/logout",{}),
                          ('/api/studies',study_fixture()),('/api/studies/x/activate',{'version':1}),
                          ('/api/study-sessions',{'study_id':'x','individual_id':'synthetic-bird','started_at':fixture()['recorded_at'],'synthetic':True}),
                          ('/api/study-sessions/x/close',{'version':1})]:
            with self.subTest(path=path): self.assertEqual(self.client.post(path,json=body).status_code,401)

    def test_real_signature_verification_and_owner_binding(self):
        self.assertEqual(self.login().status_code,200)
        with self.app.state.store.connect() as db:
            self.assertEqual(db.execute("SELECT subject FROM owner").fetchone()[0],"synthetic-owner-subject")
            saved=db.execute("SELECT digest FROM sessions").fetchone()[0]
        self.assertNotEqual(saved,self.client.cookies["t2n_session"])
        self.assertEqual(saved,digest(self.client.cookies["t2n_session"]))
        self.assertEqual(self.client.get("/admin").status_code,200)

    def test_rejects_same_domain_other_person_and_unverified_email(self):
        for changes in [{"email":"other@metivity.com"},{"email_verified":False},{"hd":None},{"sub":""}]:
            with self.subTest(changes=changes): self.assertEqual(self.login(**changes).status_code,403)

    def test_rejects_changed_subject_even_for_same_email(self):
        self.assertEqual(self.login().status_code,200)
        self.assertEqual(self.login(sub="different-subject").status_code,403)

    def test_google_rejects_audience_expiry_issuer_and_signature(self):
        for changes in [{"aud":"wrong-client"},{"exp":int(time.time())-60},{"iss":"https://attacker.example"},{"iat":int(time.time())+600}]:
            with self.subTest(changes=changes): self.assertEqual(self.login(**changes).status_code,401)
        token=self.token()
        parts=token.split(".")
        parts[2] = ("A" if parts[2][0] != "A" else "B") + parts[2][1:]
        self.assertEqual(self.client.post("/auth/google",json={"credential":".".join(parts)},headers={"Origin":ORIGIN}).status_code,401)

    def test_nonce_origin_and_replay_protection(self):
        self.assertEqual(self.login(nonce="wrong").status_code,403)
        token=self.token()
        self.assertEqual(self.client.post("/auth/google",json={"credential":token},headers={"Origin":"https://attacker.example"}).status_code,403)
        self.assertEqual(self.client.post("/auth/google",json={"credential":token},headers={"Origin":ORIGIN}).status_code,200)
        self.assertEqual(self.client.post("/auth/google",json={"credential":token},headers={"Origin":ORIGIN}).status_code,401)

    def test_expired_challenge_fails(self):
        token=self.token(); self.timestamp+=301
        self.assertEqual(self.client.post("/auth/google",json={"credential":token},headers={"Origin":ORIGIN}).status_code,401)

    def test_sessions_expire_and_logout_revokes_old_cookie(self):
        self.login(); old=self.client.cookies["t2n_session"]
        self.assertEqual(self.post("/auth/logout",{}).status_code,200)
        self.client.cookies.set("t2n_session",old)
        self.assertEqual(self.client.get("/api/observations").status_code,401)
        self.client.cookies.clear(); self.login(); self.timestamp+=4*3600+1
        self.assertEqual(self.client.get("/api/observations").status_code,401)

    def test_csrf_and_origin_required_for_changes(self):
        self.login()
        for headers in [{},{"Origin":ORIGIN},{"Origin":"https://attacker.example","X-CSRF-Token":self.csrf},{"Origin":ORIGIN,"X-CSRF-Token":"wrong"}]:
            self.assertEqual(self.client.post("/api/observations",json=fixture(),headers=headers).status_code,403)

    def test_no_client_configuration_fails_closed(self):
        app=create_app(replace(self.settings, client_id='', database=Path(self.temp.name)/"not-configured.sqlite3"))
        with TestClient(app,base_url=ORIGIN) as client:
            self.assertEqual(client.get("/auth/config").json(),{"ready":False})
            self.assertEqual(client.post("/auth/google",json={"credential":"x"},headers={"Origin":ORIGIN}).status_code,503)

    def test_subject_configuration_revokes_old_sessions(self):
        self.login()
        app=create_app(replace(self.settings, owner_sub="replacement"))
        with TestClient(app,base_url=ORIGIN) as client:
            client.cookies.update(self.client.cookies)
            self.assertEqual(client.get("/api/me").status_code,401)

    def test_http_remote_origin_rejected_and_https_cookie_protected(self):
        with self.assertRaises(ValueError): Settings(origin="http://example.com")
        app=create_app(replace(self.settings, origin="https://private.example", database=Path(self.temp.name)/"secure.sqlite3"))
        with TestClient(app,base_url="https://private.example") as client:
            header=client.get("/auth/config").headers["set-cookie"]
            for text in ["__Host-t2n_nonce","HttpOnly","Secure","SameSite=strict","Path=/"]: self.assertIn(text,header)

    def test_private_security_headers_and_untrusted_host(self):
        response=self.client.get("/api/me")
        self.assertEqual(response.headers["cache-control"],"no-store")
        self.assertIn("noindex",response.headers["x-robots-tag"])
        self.assertIn("frame-ancestors 'none'",response.headers["content-security-policy"])
        self.assertEqual(self.client.get("/",headers={"Host":"attacker.example"}).status_code,400)
        self.assertEqual(self.client.get("/assets/app.py").status_code,404)

    def test_privacy_disclosure_is_available_before_signin(self):
        response=self.client.get("/privacy")
        self.assertEqual(response.status_code,200)
        self.assertIn("verified TLS" if self.settings.database_url else "not encrypted by the application",response.text)
        self.assertNotIn('{{storage_description}}', response.text)
        self.assertIn("no Gmail, Drive or Calendar access",response.text)
        self.assertIn("noindex",response.headers["x-robots-tag"])

    def test_input_limits_no_secrets_echo_and_real_data_disabled(self):
        self.login()
        self.assertEqual(self.post("/api/observations",fixture(synthetic=False)).status_code,409)
        self.assertEqual(self.post("/api/observations",fixture(consent_review=False)).status_code,409)
        self.assertEqual(self.post("/api/observations",fixture(recorded_at="2026-09-30T12:00:00")).status_code,422)
        self.assertEqual(self.post("/api/observations",fixture(consent_training="false")).status_code,422)
        self.assertEqual(self.post("/api/observations",fixture(unexpected="sensitive secret")).status_code,422)
        self.assertNotIn("sensitive secret",self.post("/api/observations",fixture(unexpected="sensitive secret")).text)
        self.assertEqual(self.client.post("/auth/google",json={"credential":"x"*20000}).status_code,413)

    def test_review_and_release_are_distinct_gates(self):
        self.login(); key=self.submit()
        self.assertEqual(self.post("/api/releases",{"ids":[key]}).status_code,409)
        self.assertEqual(self.post(f"/api/observations/{key}/review",{"version":1,"decision":"accept"}).status_code,409)
        self.assertEqual(self.accept(key).status_code,200)
        self.assertEqual(self.accept(key).status_code,409)
        released=self.post("/api/releases",{"ids":[key]})
        self.assertEqual(released.status_code,201)
        exported=self.client.get("/api/releases/"+released.json()["id"]).json()
        self.assertTrue(exported["synthetic"])
        self.assertFalse(exported["records"][0]["consent_publication"])
        review=exported["records"][0]["review"]
        self.assertEqual(review["decision"],"accept")
        self.assertEqual(review["reviewer"],"owner")
        self.assertEqual(review["source_version"],1)
        self.assertEqual(review["reviewed_at"],self.timestamp)
        self.assertTrue(all(review["checks"].values()))
        fingerprint=digest(json.dumps(exported["records"],sort_keys=True,separators=(",",":")))
        self.assertEqual(exported["fingerprint"],fingerprint)

    def test_release_refuses_missing_review_provenance(self):
        self.login(); key=self.submit()
        # A legacy accepted row without saved attestations cannot enter a new release.
        with self.app.state.store.connect() as db:
            db.execute("UPDATE observations SET state='accepted' WHERE id=?",(key,))
        self.assertEqual(self.post("/api/releases",{"ids":[key]}).status_code,409)

    def test_export_detects_changed_released_content(self):
        self.login(); key=self.submit(); self.accept(key)
        released=self.post("/api/releases",{"ids":[key]}).json()["id"]
        with self.app.state.store.connect() as db:
            payload=json.loads(db.execute("SELECT payload FROM observations WHERE id=?",(key,)).fetchone()[0])
            payload["note"]="Changed outside the release workflow"
            db.execute("UPDATE observations SET payload=? WHERE id=?",(json.dumps(payload),key))
        response=self.client.get("/api/releases/"+released)
        self.assertEqual(response.status_code,409)
        self.assertNotIn("Changed outside",response.text)

    def test_unknown_rights_context_evidence_or_label_cannot_be_accepted(self):
        self.login()
        for changes in [{"rights":"unknown"},{"rights_evidence":""},{"context":"unknown"},{"label_source":"unknown"}]:
            self.assertEqual(self.accept(self.submit(**changes)).status_code,409)

    def test_training_opt_out_does_not_prevent_review_but_blocks_release(self):
        self.login(); key=self.submit(consent_training=False)
        self.assertEqual(self.accept(key).status_code,200)
        self.assertEqual(self.post("/api/releases",{"ids":[key]}).status_code,409)

    def test_withdrawal_scrubs_metadata_and_revokes_all_dependent_releases(self):
        self.login(); key=self.submit(note="Synthetic private note"); self.accept(key)
        release1=self.post("/api/releases",{"ids":[key]}).json()["id"]
        release2=self.post("/api/releases",{"ids":[key]}).json()["id"]
        self.assertEqual(self.post(f"/api/observations/{key}/withdraw",{"version":1}).status_code,409)
        self.assertEqual(self.post(f"/api/observations/{key}/withdraw",{"version":4}).status_code,200)
        self.assertNotIn("Synthetic private note",self.client.get("/api/observations").text)
        for key in [release1,release2]: self.assertEqual(self.client.get("/api/releases/"+key).status_code,410)
        self.assertNotIn("Synthetic private note",self.client.get("/api/audit").text)

    def test_release_creation_is_atomic_and_duplicates_rejected(self):
        self.login(); first=self.submit(); second=self.submit(consent_training=False)
        self.accept(first); self.accept(second)
        self.assertEqual(self.post("/api/releases",{"ids":[first,first]}).status_code,422)
        self.assertEqual(self.post("/api/releases",{"ids":[first,second]}).status_code,409)
        self.assertEqual(self.client.get("/api/releases").json(),[])
        self.assertEqual({r["state"] for r in self.client.get("/api/observations").json()},{"accepted"})

    def test_rejected_records_do_not_enter_releases(self):
        self.login(); key=self.submit()
        self.assertEqual(self.post(f"/api/observations/{key}/review",{"version":1,"decision":"reject"}).status_code,200)
        self.assertEqual(self.post("/api/releases",{"ids":[key]}).status_code,409)

    def seed_evidence(self):
        self.entries = [{'key':'resource:fixture','kind':'resource','title':'Synthetic reference',
                         'payload':{'title':'Synthetic reference','version':'test-v1'}}]
        return sync_catalog(self.app.state.store, self.entries, self.timestamp)

    def create_study(self):
        self.seed_evidence()
        result=self.post('/api/studies',study_fixture())
        self.assertEqual(result.status_code,201,result.text)
        return result.json()

    def start_study_session(self):
        study=self.create_study()
        self.assertEqual(self.post('/api/studies/'+study['id']+'/activate',{'version':1}).status_code,200)
        result=self.post('/api/study-sessions',{'study_id':study['id'],'individual_id':fixture()['individual_id'],
            'started_at':fixture()['recorded_at'],'synthetic':True})
        self.assertEqual(result.status_code,201,result.text)
        return study,result.json()

    def test_catalog_import_is_idempotent_and_keeps_cited_versions(self):
        self.login();study=self.create_study()
        original=self.client.get('/api/evidence').json()[0]['fingerprint']
        self.assertEqual(sync_catalog(self.app.state.store,self.entries,self.timestamp),
                         {'records':1,'created':0,'changed':0,'retired':0})
        self.entries[0]['payload']['version']='test-v2'
        self.assertEqual(sync_catalog(self.app.state.store,self.entries,self.timestamp)['changed'],1)
        old=self.client.get('/api/evidence/resource:fixture/versions/'+original).json()
        self.assertEqual(old['payload']['version'],'test-v1')
        saved=self.client.get('/api/studies').json()[0]
        self.assertEqual(saved['evidence'][0]['fingerprint'],original)
        self.assertEqual(saved['fingerprint'],study['fingerprint'])
        replacement=[{'key':'source:replacement','kind':'source','title':'Replacement', 'payload':{'title':'Replacement'}}]
        self.assertEqual(sync_catalog(self.app.state.store,replacement,self.timestamp)['retired'],1)
        self.assertEqual(self.client.get('/api/evidence/resource:fixture/versions/'+original).status_code,200)
        self.assertEqual(len(self.client.get('/api/evidence').json()),1)

    def test_catalog_duplicate_import_leaves_existing_catalog_intact(self):
        self.login();self.seed_evidence()
        with self.assertRaises(ValueError):
            sync_catalog(self.app.state.store,self.entries+self.entries,self.timestamp)
        self.assertEqual(len(self.client.get('/api/evidence').json()),1)

    def test_study_admission_rejects_real_interventions_and_bad_evidence(self):
        self.login();self.seed_evidence()
        for changes,code in [({'synthetic':False},409),({'method':'playback'},422),({'codebook':{}},422),
                             ({'evidence_keys':['absent']},409),({'evidence_keys':['resource:fixture']*2},422)]:
            with self.subTest(changes=changes):
                self.assertEqual(self.post('/api/studies',study_fixture(**changes)).status_code,code)
        self.assertEqual(self.client.get('/api/studies').json(),[])
        self.assertEqual(self.client.post('/api/studies',json=study_fixture(),headers={'Origin':ORIGIN}).status_code,403)

    def test_study_must_be_activated_and_session_must_be_synthetic(self):
        self.login();study=self.create_study()
        body={'study_id':study['id'],'individual_id':'synthetic-bird','started_at':fixture()['recorded_at'],'synthetic':True}
        self.assertEqual(self.post('/api/study-sessions',body).status_code,409)
        self.assertEqual(self.post('/api/studies/'+study['id']+'/activate',{'version':2}).status_code,409)
        self.assertEqual(self.post('/api/studies/'+study['id']+'/activate',{'version':1}).status_code,200)
        self.assertEqual(self.post('/api/studies/'+study['id']+'/activate',{'version':1}).status_code,409)
        self.assertEqual(self.post('/api/study-sessions',{**body,'synthetic':False}).status_code,409)
        self.assertEqual(self.post('/api/study-sessions',{**body,'started_at':'2026-09-30T12:00:00'}).status_code,422)

    def test_linked_observation_enforces_identity_codebook_and_start_time(self):
        self.login();study,session=self.start_study_session()
        base=fixture(study_session_id=session['id'],session_id=session['id'])
        for changes in [{'species':'Wrong species'},{'individual_id':'another-bird'},{'session_id':'different'},
                        {'context':'resting'},{'recorded_at':'2026-09-29T12:00:00+03:00'}, {'study_session_id':'absent'}]:
            with self.subTest(changes=changes):
                self.assertEqual(self.post('/api/observations',{**base,**changes}).status_code,409)
        self.assertEqual(self.client.get('/api/observations').json(),[])

    def test_linkage_persists_across_restart_and_survives_release_until_withdrawal(self):
        self.login();study,session=self.start_study_session()
        key=self.submit(study_session_id=session['id'],session_id=session['id'])
        self.assertEqual(self.accept(key).status_code,200)
        release=self.post('/api/releases',{'ids':[key]}).json()['id']
        app=create_app(self.settings,clock=lambda:self.timestamp)
        with TestClient(app,base_url=ORIGIN) as client:
            client.cookies.update(self.client.cookies)
            self.assertEqual(len(client.get('/api/studies').json()),1)
            self.assertEqual(len(client.get('/api/study-sessions').json()),1)
            record=client.get('/api/releases/'+release).json()['records'][0]
            self.assertEqual(record['study']['protocol_fingerprint'],study['fingerprint'])
            self.assertEqual(record['study']['protocol_version'],1)
            self.assertEqual(record['study']['session_id'],session['id'])
        self.assertEqual(self.post('/api/observations/'+key+'/withdraw',{'version':3}).status_code,200)
        with self.app.state.store.connect() as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM observation_links').fetchone()[0],0)
        self.assertEqual(self.client.get('/api/releases/'+release).status_code,410)

    def test_closing_session_blocks_new_observations_without_losing_existing_ones(self):
        self.login();study,session=self.start_study_session()
        key=self.submit(study_session_id=session['id'],session_id=session['id'])
        self.assertEqual(self.post('/api/study-sessions/'+session['id']+'/close',{'version':2}).status_code,409)
        self.assertEqual(self.post('/api/study-sessions/'+session['id']+'/close',{'version':1}).status_code,200)
        self.assertEqual(self.post('/api/study-sessions/'+session['id']+'/close',{'version':1}).status_code,409)
        self.assertEqual(self.post('/api/observations',fixture(study_session_id=session['id'],session_id=session['id'])).status_code,409)
        self.assertEqual(self.accept(key).status_code,200)

    def test_graph_tracks_frozen_references_and_withdrawal_without_notes(self):
        self.login()
        entries = [{'key':'resource:fixture','kind':'resource','title':'Original source', 'payload':{'title':'Original source'}}]
        sync_catalog(self.app.state.store, entries)
        study = self.post('/api/studies', study_fixture()).json()
        self.assertEqual(self.post('/api/studies/'+study['id']+'/activate', {'version':1}).status_code,200)
        session = self.post('/api/study-sessions', {'study_id':study['id'],'individual_id':'synthetic-bird-01','started_at':'2026-09-30T11:00:00+03:00','synthetic':True}).json()
        key = self.submit(study_session_id=session['id'], session_id=session['id'], note='PRIVATE NOTE MUST NOT APPEAR IN GRAPH')
        self.accept(key)
        release = self.post('/api/releases', {'ids':[key]}).json()
        entries[0]['payload']['title'] = 'Changed source'; entries[0]['title']='Changed source'
        sync_catalog(self.app.state.store, entries)
        response = self.client.get('/api/knowledge-graph')
        self.assertEqual(response.status_code,200)
        graph = response.json()
        self.assertEqual(graph['visibility'],'owner_only')
        self.assertNotIn('PRIVATE NOTE MUST NOT APPEAR', response.text)
        historical = [n for n in graph['nodes'] if n.get('historical')]
        self.assertEqual(len(historical),1); self.assertEqual(historical[0]['title'],'Original source')
        self.assertEqual({e['relation'] for e in graph['edges']}, {'uses_frozen_evidence','follows_protocol','observed_in','contains'})
        self.assertEqual(self.post('/api/observations/'+key+'/withdraw',{'version':3}).status_code,200)
        graph = self.client.get('/api/knowledge-graph').json()
        self.assertFalse(any(n['id']=='observation:'+key for n in graph['nodes']))
        self.assertFalse(any(e['relation']=='contains' for e in graph['edges']))
        self.assertTrue(next(n for n in graph['nodes'] if n['id']=='release:'+release['id'])['revoked'])


if __name__ == "__main__":
    unittest.main()
