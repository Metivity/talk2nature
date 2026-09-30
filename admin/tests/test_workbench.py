import json
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient
from google.auth import crypt, jwt

from admin.app import create_app, digest
from admin.auth import Settings

CLIENT_ID = "test-client.apps.googleusercontent.com"
ORIGIN = "http://localhost:4180"


def fixture(**changes):
    value = {"species":"Cockatiel", "individual_id":"synthetic-bird-01", "session_id":"synthetic-session-01",
             "recorded_at":"2026-09-30T12:00:00+03:00", "context":"feeding", "label_source":"direct_observation",
             "note":"Invented example: bird near food bowl.", "rights":"creator", "rights_evidence":"Invented fixture; no recording exists.",
             "consent_review":True, "consent_training":True, "consent_publication":False, "synthetic":True}
    value.update(changes)
    return value


class WorkbenchTests(unittest.TestCase):
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
        self.settings = Settings(client_id=CLIENT_ID, database=Path(self.temp.name)/"private"/"admin.sqlite3")
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
        for path in ["/api/me","/api/observations","/api/releases","/api/releases/guessed","/api/audit"]:
            with self.subTest(path=path): self.assertEqual(self.client.get(path).status_code,401)
        self.assertEqual(self.client.get("/admin",follow_redirects=False).status_code,303)

    def test_every_private_write_requires_authentication(self):
        for path,body in [("/api/observations",fixture()),("/api/releases",{"ids":["x"]}),
                          ("/api/observations/x/review",{"version":1,"decision":"reject"}),
                          ("/api/observations/x/withdraw",{"version":1}),("/auth/logout",{})]:
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
        app=create_app(Settings(database=Path(self.temp.name)/"not-configured.sqlite3"))
        with TestClient(app,base_url=ORIGIN) as client:
            self.assertEqual(client.get("/auth/config").json(),{"ready":False})
            self.assertEqual(client.post("/auth/google",json={"credential":"x"},headers={"Origin":ORIGIN}).status_code,503)

    def test_subject_configuration_revokes_old_sessions(self):
        self.login()
        app=create_app(Settings(client_id=CLIENT_ID,owner_sub="replacement",database=self.settings.database))
        with TestClient(app,base_url=ORIGIN) as client:
            client.cookies.update(self.client.cookies)
            self.assertEqual(client.get("/api/me").status_code,401)

    def test_http_remote_origin_rejected_and_https_cookie_protected(self):
        with self.assertRaises(ValueError): Settings(origin="http://example.com")
        app=create_app(Settings(origin="https://private.example",client_id=CLIENT_ID,database=Path(self.temp.name)/"secure.sqlite3"))
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
        fingerprint=digest(json.dumps(exported["records"],sort_keys=True,separators=(",",":")))
        self.assertEqual(exported["fingerprint"],fingerprint)

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


if __name__ == "__main__":
    unittest.main()
