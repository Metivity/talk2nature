"""Owner-only metadata rehearsal. No recording upload, playback or training endpoint."""
import hashlib
import json
import secrets
import time
from datetime import datetime
from pathlib import Path
from typing import Annotated, Literal
from urllib.parse import urlsplit

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel, ConfigDict, Field, StrictBool, field_validator
from starlette.middleware.trustedhost import TrustedHostMiddleware

from admin.auth import OWNER_EMAIL, Settings, allowed_owner, verify_google_token
from admin.store import open_store, StorageUnavailable, audit, observation
from admin.studies import attach_session, register_studies

ASSETS = Path(__file__).parent / "ui"
SESSION_SECONDS = 4 * 60 * 60
CHALLENGE_SECONDS = 5 * 60


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Credential(Input):
    credential: str = Field(min_length=1, max_length=8192)


class Observation(Input):
    study_session_id: str | None = Field(default=None, min_length=1, max_length=80)
    species: str = Field(min_length=2, max_length=80)
    individual_id: str = Field(min_length=2, max_length=80)
    session_id: str = Field(min_length=2, max_length=80)
    recorded_at: datetime
    context: Literal["unknown", "resting", "moving", "feeding", "social"]
    label_source: Literal["unknown", "direct_observation", "video"]
    note: str = Field(default="", max_length=1000)
    rights: Literal["unknown", "creator", "licensed"]
    rights_evidence: str = Field(default="", max_length=500)
    consent_review: StrictBool
    consent_training: StrictBool
    consent_publication: StrictBool
    synthetic: StrictBool

    @field_validator("recorded_at")
    @classmethod
    def timezone_required(cls, value):
        if value.utcoffset() is None:
            raise ValueError("An explicit timezone is required.")
        return value


class Review(Input):
    version: int = Field(ge=1)
    decision: Literal["accept", "reject"]
    rights_checked: StrictBool = False
    consent_checked: StrictBool = False
    privacy_checked: StrictBool = False
    label_checked: StrictBool = False


class Version(Input):
    version: int = Field(ge=1)


class Release(Input):
    ids: list[str] = Field(min_length=1, max_length=100)


def create_app(settings=None, verifier=None, clock=None):
    settings = settings or Settings.from_env()
    verify = verifier or verify_google_token
    now = clock or (lambda: int(time.time()))
    store = open_store(settings)
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    app.state.store = store
    session_cookie = "__Host-t2n_session" if settings.secure else "t2n_session"
    nonce_cookie = "__Host-t2n_nonce" if settings.secure else "t2n_nonce"
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=[urlsplit(settings.origin).hostname])

    def cookie(response, name, value, lifetime):
        response.set_cookie(name, value, max_age=lifetime, httponly=True,
                            secure=settings.secure, samesite="strict", path="/")

    def same_origin(request):
        if request.headers.get("origin") != settings.origin:
            raise HTTPException(403, "Request origin is not permitted.")

    def require_owner(request: Request):
        token = request.cookies.get(session_cookie, "")
        with store.connect() as db:
            session = db.execute("SELECT * FROM sessions WHERE digest=? AND expires>?", (digest(token), now())).fetchone()
            owner = db.execute("SELECT subject FROM owner WHERE singleton=1").fetchone()
        if (not session or not owner or session["subject"] != owner["subject"]
                or (settings.owner_sub and session["subject"] != settings.owner_sub)):
            raise HTTPException(401, "Sign in with the owner's Google account.")
        if request.method not in {"GET", "HEAD", "OPTIONS"}:
            same_origin(request)
            if not secrets.compare_digest(request.headers.get("x-csrf-token", ""), session["csrf"]):
                raise HTTPException(403, "Refresh the page before making this change.")
        return dict(session)

    Owner = Annotated[dict, Depends(require_owner)]

    @app.exception_handler(StorageUnavailable)
    async def unavailable(request, exc):
        return JSONResponse({'detail': 'Private storage is temporarily unavailable.'}, status_code=503)

    @app.exception_handler(RequestValidationError)
    async def invalid_input(request, exc):
        # Pydantic's default response can echo raw credentials or private text.
        return JSONResponse({"detail": "Invalid or unsupported fields. Check required values and timezone."}, status_code=422)

    @app.middleware("http")
    async def boundaries(request, call_next):
        if request.method not in {"GET", "HEAD", "OPTIONS"}:
            # Endpoints accept only bounded JSON; reject streaming bodies too.
            try:
                length = int(request.headers.get("content-length", "-1"))
            except ValueError:
                length = -1
            if length < 0 or length > 16384:
                return JSONResponse({"detail": "A JSON body of at most 16 KiB is required."}, status_code=413)
            if request.headers.get("content-type", "").split(";")[0] != "application/json":
                return JSONResponse({"detail": "JSON is required."}, status_code=415)
            body = await request.body()
            if len(body) > 16384:
                return JSONResponse({"detail": "Request is too large."}, status_code=413)
        response = await call_next(request)
        response.headers.update({
            "Cache-Control": "no-store", "X-Robots-Tag": "noindex, nofollow, noarchive",
            "X-Content-Type-Options": "nosniff", "Referrer-Policy": "strict-origin",
            "X-Frame-Options": "DENY", "Cross-Origin-Opener-Policy": "same-origin-allow-popups",
            "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' https://accounts.google.com/gsi/client; style-src 'self' https://accounts.google.com/gsi/style; connect-src 'self' https://accounts.google.com/gsi/; frame-src https://accounts.google.com/gsi/; img-src 'self' data:; base-uri 'none'; object-src 'none'; frame-ancestors 'none'; form-action 'self'",
        })
        if settings.secure:
            response.headers["Strict-Transport-Security"] = "max-age=31536000"
        return response

    @app.get("/")
    def signin():
        return FileResponse(ASSETS / "signin.html")

    @app.get("/privacy")
    def privacy():
        storage = ('This instance stores metadata in PostgreSQL. Remote connections require verified TLS. '
                   'Database encryption at rest, hosting location and backup retention depend on the deployment configuration.'
                   if settings.database_url else
                   'This instance stores a local SQLite file outside the public website and Git history. '
                   'The file is not encrypted by the application and depends on the host’s disk protection.')
        return HTMLResponse((ASSETS / 'privacy.html').read_text().replace('{{storage_description}}', storage))

    @app.get("/assets/{name}")
    def asset(name: str):
        if name not in {"style.css", "signin.js", "workbench.js"}:
            raise HTTPException(404)
        return FileResponse(ASSETS / name)

    @app.get("/health")
    def health():
        return {"status": "ok", "mode": "synthetic-metadata-only"}

    @app.get('/ready')
    def ready():
        with store.connect() as db:
            db.execute('SELECT COUNT(*) FROM owner').fetchone()
        return {'status': 'ready', 'mode': 'synthetic-metadata-only'}

    @app.get("/auth/config")
    def auth_config(response: Response):
        if not settings.client_id:
            return {"ready": False}
        nonce = secrets.token_urlsafe(32)
        with store.connect() as db:
            db.execute("DELETE FROM challenges WHERE expires<=?", (now(),))
            if db.execute("SELECT COUNT(*) FROM challenges").fetchone()[0] >= 100:
                raise HTTPException(429, "Please try again in a few minutes.")
            db.execute("INSERT INTO challenges VALUES(?,?)", (digest(nonce), now()+CHALLENGE_SECONDS))
        cookie(response, nonce_cookie, nonce, CHALLENGE_SECONDS)
        return {"ready": True, "client_id": settings.client_id, "nonce": nonce}

    @app.post("/auth/google")
    def login(body: Credential, request: Request, response: Response):
        same_origin(request)
        if not settings.client_id:
            raise HTTPException(503, "Google Sign-In has not been configured.")
        nonce = request.cookies.get(nonce_cookie, "")
        # Consume before verification. Concurrent replays cannot both succeed.
        with store.connect() as db:
            challenge = db.execute("DELETE FROM challenges WHERE digest=? AND expires>? RETURNING digest", (digest(nonce), now())).fetchone()
        if not challenge:
            raise HTTPException(401, "Sign-in expired. Reload and try again.")
        try:
            claims = verify(body.credential, settings.client_id)
        except Exception:
            raise HTTPException(401, "Google identity could not be verified.") from None
        if (not isinstance(claims, dict) or claims.get("nonce") != nonce
                or not allowed_owner(claims, settings)):
            raise HTTPException(403, "This account does not have access.")
        token, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
        with store.connect() as db:
            owner = db.execute("SELECT subject FROM owner WHERE singleton=1").fetchone()
            if owner and owner["subject"] != claims["sub"]:
                raise HTTPException(403, "This account does not have access.")
            if not owner:
                db.execute("INSERT INTO owner VALUES(1,?)", (claims["sub"],))
            db.execute("DELETE FROM sessions WHERE expires<=? OR digest=?", (now(), digest(request.cookies.get(session_cookie, ""))))
            db.execute("INSERT INTO sessions VALUES(?,?,?,?)", (digest(token), claims["sub"], csrf, now()+SESSION_SECONDS))
            audit(db, "owner_login", "owner", now())
        cookie(response, session_cookie, token, SESSION_SECONDS)
        response.delete_cookie(nonce_cookie, secure=settings.secure, httponly=True, samesite="strict")
        return {"ok": True}

    @app.get("/admin")
    def workbench(request: Request):
        try:
            require_owner(request)
        except HTTPException:
            return RedirectResponse("/", status_code=303)
        return FileResponse(ASSETS / "workbench.html")

    @app.get("/api/me")
    def me(owner: Owner):
        return {"email": OWNER_EMAIL, "csrf": owner["csrf"], "mode": "synthetic-metadata-only"}

    @app.post("/auth/logout")
    def logout(request: Request, response: Response, owner: Owner):
        with store.connect() as db:
            db.execute("DELETE FROM sessions WHERE digest=?", (owner["digest"],))
        response.delete_cookie(session_cookie, secure=settings.secure, httponly=True, samesite="strict")
        return {"ok": True}

    @app.get("/api/observations")
    def observations(owner: Owner):
        with store.connect() as db:
            return [observation(row) for row in db.execute("SELECT * FROM observations ORDER BY created DESC, id")]

    @app.post("/api/observations", status_code=201)
    def submit(body: Observation, owner: Owner):
        if not body.synthetic:
            raise HTTPException(409, "Real-data admission awaits an approved protocol and storage review.")
        if not body.consent_review:
            raise HTTPException(409, "Review permission is required to submit an observation.")
        value = body.model_dump(mode="json")
        value["consent_version"] = "rehearsal-v1"
        key = secrets.token_hex(12)
        with store.connect() as db:
            if db.execute("SELECT COUNT(*) FROM observations").fetchone()[0] >= 500:
                raise HTTPException(409, "The local rehearsal is limited to 500 observations.")
            attach_session(db, value)
            db.execute("INSERT INTO observations(id,payload,state,created) VALUES(?,?,?,?)", (key, json.dumps(value), "quarantined", now()))
            if body.study_session_id:
                db.execute("INSERT INTO observation_links VALUES(?,?)", (key, body.study_session_id))
            audit(db, "submitted", key, now())
        return {"id": key, "state": "quarantined", "version": 1}

    @app.post("/api/observations/{key}/review")
    def review(key: str, body: Review, owner: Owner):
        with store.connect() as db:
            row = db.execute("SELECT * FROM observations WHERE id=?", (key,)).fetchone()
            if not row:
                raise HTTPException(404, "Observation not found.")
            if row["version"] != body.version or row["state"] != "quarantined":
                raise HTTPException(409, "This observation has changed. Refresh before reviewing.")
            value = observation(row)
            if body.decision == "accept" and (not all([body.rights_checked, body.consent_checked, body.privacy_checked, body.label_checked])
                    or value["rights"] == "unknown" or not value["rights_evidence"]
                    or value["label_source"] == "unknown" or value["context"] == "unknown"):
                raise HTTPException(409, "Rights, consent, privacy and an independent context label must all be reviewed.")
            state = "accepted" if body.decision == "accept" else "rejected"
            payload = json.loads(row["payload"])
            payload["review"] = {"decision": body.decision, "reviewer": "owner",
                                 "reviewed_at": now(), "source_version": body.version,
                                 "checks": {field: getattr(body, field) for field in
                                            ("rights_checked", "consent_checked", "privacy_checked", "label_checked")}}
            db.execute("UPDATE observations SET payload=?,state=?,version=version+1 WHERE id=?", (json.dumps(payload),state,key))
            audit(db, state, key, now())
        return {"state": state}

    @app.post("/api/observations/{key}/withdraw")
    def withdraw(key: str, body: Version, owner: Owner):
        with store.connect() as db:
            row = db.execute("SELECT * FROM observations WHERE id=?", (key,)).fetchone()
            if not row:
                raise HTTPException(404)
            if row["version"] != body.version or row["state"] == "withdrawn":
                raise HTTPException(409, "This observation has changed. Refresh first.")
            db.execute("UPDATE observations SET payload='{}', state='withdrawn', version=version+1 WHERE id=?", (key,))
            db.execute("DELETE FROM observation_links WHERE observation_id=?", (key,))
            for release in db.execute("SELECT id,members FROM releases WHERE revoked=0").fetchall():
                if key in json.loads(release["members"]):
                    db.execute("UPDATE releases SET revoked=1 WHERE id=?", (release["id"],))
                    audit(db, "release_revoked", release["id"], now())
            audit(db, "withdrawn", key, now())
        return {"state": "withdrawn", "notice": "Active metadata removed; dependent releases revoked. Previously downloaded copies need separate deletion."}

    @app.post("/api/releases", status_code=201)
    def release(body: Release, owner: Owner):
        if len(set(body.ids)) != len(body.ids):
            raise HTTPException(422, "Duplicate observation IDs are not allowed.")
        with store.connect() as db:
            records = []
            for key in sorted(body.ids):
                row = db.execute("SELECT * FROM observations WHERE id=?", (key,)).fetchone()
                if not row or row["state"] not in {"accepted", "released"}:
                    raise HTTPException(409, "Every selected observation must pass review.")
                value = observation(row)
                if not value["consent_training"]:
                    raise HTTPException(409, "Training permission is required for every observation.")
                proof = value.get("review", {})
                checks = proof.get("checks", {})
                if proof.get("decision") != "accept" or not all(checks.get(field) is True for field in
                        ("rights_checked", "consent_checked", "privacy_checked", "label_checked")):
                    raise HTTPException(409, "A stored review record is required for every observation.")
                # Mutable workflow state is not part of a content fingerprint.
                records.append({"id": key, **json.loads(row["payload"])})
            fingerprint = digest(json.dumps(records, sort_keys=True, separators=(",", ":")))
            key = secrets.token_hex(12)
            db.execute("INSERT INTO releases(id,members,fingerprint,created) VALUES(?,?,?,?)", (key, json.dumps(sorted(body.ids)), fingerprint, now()))
            for member in body.ids:
                db.execute("UPDATE observations SET state='released',version=version+1 WHERE id=?", (member,))
            audit(db, "release_created", key, now())
        return {"id": key, "fingerprint": fingerprint, "synthetic": True}

    @app.get("/api/releases")
    def releases(owner: Owner):
        with store.connect() as db:
            return [{"id":r["id"], "count":len(json.loads(r["members"])), "revoked":bool(r["revoked"]), "fingerprint":r["fingerprint"]} for r in db.execute("SELECT * FROM releases ORDER BY created DESC, id")]

    @app.get("/api/releases/{key}")
    def export(key: str, owner: Owner):
        with store.connect() as db:
            row = db.execute("SELECT * FROM releases WHERE id=?", (key,)).fetchone()
            if not row:
                raise HTTPException(404)
            if row["revoked"]:
                raise HTTPException(410, "This release was revoked after a withdrawal.")
            records = []
            for member in json.loads(row["members"]):
                item = db.execute("SELECT * FROM observations WHERE id=?", (member,)).fetchone()
                if not item or item["state"] != "released":
                    raise HTTPException(410, "This release is no longer available.")
                records.append({"id": member, **json.loads(item["payload"])})
            if digest(json.dumps(records, sort_keys=True, separators=(",", ":"))) != row["fingerprint"]:
                raise HTTPException(409, "Release content no longer matches its fingerprint. Review the data store before exporting.")
            return {"schema_version":1, "synthetic":True, "kind":"metadata-rehearsal", "fingerprint":row["fingerprint"], "records":records,
                    "limitations":["No source audio or verified recording hashes; not an acoustic training dataset.", "Review checkboxes are attestations, not independent verification.", "No permission to publish is implied by a private training release."]}

    @app.get("/api/audit")
    def history(owner: Owner):
        with store.connect() as db:
            return [dict(r) for r in db.execute("SELECT action,target,created FROM audit ORDER BY id DESC LIMIT 100")]

    register_studies(app, store, require_owner, now)
    return app
