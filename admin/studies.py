"""Frozen passive-observation protocols and synthetic sessions, under owner auth."""
import json
import secrets
from datetime import datetime
from typing import Annotated, Literal

from fastapi import Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field, StrictBool, field_validator

from admin.catalog import fingerprint
from admin.store import audit

Context = Literal['resting', 'moving', 'feeding', 'social']


class StudyInput(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    title: str = Field(min_length=3, max_length=120)
    species: str = Field(min_length=2, max_length=80)
    question: str = Field(min_length=10, max_length=600)
    protocol: str = Field(min_length=20, max_length=2000)
    stop_rule: str = Field(min_length=10, max_length=500)
    codebook: dict[Context, Annotated[str, Field(min_length=5, max_length=300)]] = Field(min_length=1, max_length=4)
    evidence_keys: list[str] = Field(min_length=1, max_length=10)
    method: Literal['passive_observation']
    synthetic: StrictBool


class SessionInput(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    study_id: str = Field(min_length=1, max_length=80)
    individual_id: str = Field(min_length=2, max_length=80)
    started_at: datetime
    synthetic: StrictBool

    @field_validator('started_at')
    @classmethod
    def timezone_required(cls, value):
        if value.utcoffset() is None:
            raise ValueError('Timezone required.')
        return value


class Transition(BaseModel):
    model_config = ConfigDict(extra='forbid')
    version: int = Field(ge=1)


def study_record(db, row):
    return {**dict(row), 'payload': json.loads(row['payload']),
            'evidence': [dict(e) for e in db.execute(
                'SELECT evidence_key,fingerprint FROM study_evidence WHERE study_id=? ORDER BY evidence_key', (row['id'],))]}


def attach_session(db, value):
    """Validate a linked session inside the observation's write transaction."""
    key = value.get('study_session_id')
    if not key:
        return
    session = db.execute('SELECT * FROM study_sessions WHERE id=?', (key,)).fetchone()
    if not session or session['state'] != 'open':
        raise HTTPException(409, 'Select an open study session.')
    study = db.execute('SELECT * FROM studies WHERE id=?', (session['study_id'],)).fetchone()
    protocol = json.loads(study['payload'])
    info = json.loads(session['payload'])
    if (study['state'] != 'active' or value['species'] != protocol['species']
            or value['individual_id'] != info['individual_id'] or value['session_id'] != key):
        raise HTTPException(409, 'Observation identity must match its active study session.')
    if value['context'] != 'unknown' and value['context'] not in protocol['codebook']:
        raise HTTPException(409, 'This context is not in the frozen study codebook.')
    if datetime.fromisoformat(value['recorded_at']) < datetime.fromisoformat(info['started_at']):
        raise HTTPException(409, 'Observation time must be within the study session.')
    value['study'] = {'id': study['id'], 'title': protocol['title'], 'protocol_version': 1,
                      'protocol_fingerprint': study['fingerprint'], 'session_id': key,
                      'evidence': study_record(db, study)['evidence']}


def register_studies(app, store, require_owner, now):
    Owner = Annotated[dict, Depends(require_owner)]

    @app.get('/api/evidence')
    def evidence(owner: Owner):
        with store.connect() as db:
            return [{**dict(r), 'payload': json.loads(r['payload'])} for r in db.execute('''
                SELECT c.*,v.payload FROM evidence_catalog c JOIN evidence_versions v
                ON c.key=v.key AND c.fingerprint=v.fingerprint WHERE c.active=1 ORDER BY c.kind,c.title''')]

    @app.get('/api/evidence/{key}/versions/{checksum}')
    def evidence_version(key: str, checksum: str, owner: Owner):
        with store.connect() as db:
            row = db.execute('SELECT payload FROM evidence_versions WHERE key=? AND fingerprint=?', (key, checksum)).fetchone()
        if not row:
            raise HTTPException(404)
        return {'key': key, 'fingerprint': checksum, 'payload': json.loads(row['payload'])}

    @app.get('/api/studies')
    def studies(owner: Owner):
        with store.connect() as db:
            return [study_record(db, r) for r in db.execute('SELECT * FROM studies ORDER BY created DESC,id')]

    @app.post('/api/studies', status_code=201)
    def create(body: StudyInput, owner: Owner):
        if not body.synthetic:
            raise HTTPException(409, 'Only synthetic study rehearsal is available.')
        if len(set(body.evidence_keys)) != len(body.evidence_keys):
            raise HTTPException(422, 'Duplicate evidence references.')
        key = secrets.token_hex(12)
        value = body.model_dump(mode='json')
        with store.connect() as db:
            if db.execute('SELECT COUNT(*) FROM studies').fetchone()[0] >= 100:
                raise HTTPException(409, 'The rehearsal is limited to 100 studies.')
            refs = []
            for ref in sorted(body.evidence_keys):
                record = db.execute('SELECT * FROM evidence_catalog WHERE key=? AND active=1', (ref,)).fetchone()
                if not record:
                    raise HTTPException(409, 'Every reference must exist in the imported catalog.')
                refs.append((ref, record['fingerprint']))
            checksum = fingerprint({'protocol': value, 'evidence': refs})
            db.execute('INSERT INTO studies(id,payload,fingerprint,state,created) VALUES(?,?,?,?,?)',
                       (key, json.dumps(value), checksum, 'draft', now()))
            db.executemany('INSERT INTO study_evidence VALUES(?,?,?)', [(key, ref, fp) for ref, fp in refs])
            audit(db, 'study_created', key, now())
        return {'id': key, 'state': 'draft', 'version': 1, 'fingerprint': checksum}

    @app.post('/api/studies/{key}/activate')
    def activate(key: str, body: Transition, owner: Owner):
        with store.connect() as db:
            changed = db.execute("UPDATE studies SET state='active',version=version+1 WHERE id=? AND version=? AND state='draft'",
                                 (key, body.version)).rowcount
            if not changed:
                raise HTTPException(409, 'Study changed or is not a draft.')
            audit(db, 'study_activated', key, now())
        return {'state': 'active', 'notice': 'Synthetic rehearsal only; protocol content is frozen.'}

    @app.get('/api/study-sessions')
    def sessions(owner: Owner):
        with store.connect() as db:
            return [{**dict(r), 'payload': json.loads(r['payload'])} for r in db.execute(
                'SELECT * FROM study_sessions ORDER BY created DESC,id')]

    @app.post('/api/study-sessions', status_code=201)
    def start(body: SessionInput, owner: Owner):
        if not body.synthetic:
            raise HTTPException(409, 'Only synthetic sessions are available.')
        key = secrets.token_hex(12)
        with store.connect() as db:
            study = db.execute("SELECT * FROM studies WHERE id=? AND state='active'", (body.study_id,)).fetchone()
            if not study:
                raise HTTPException(409, 'Activate a study before starting a session.')
            if db.execute('SELECT COUNT(*) FROM study_sessions').fetchone()[0] >= 500:
                raise HTTPException(409, 'The rehearsal is limited to 500 sessions.')
            db.execute('INSERT INTO study_sessions(id,study_id,payload,state,created) VALUES(?,?,?,?,?)',
                       (key, body.study_id, json.dumps(body.model_dump(mode='json')), 'open', now()))
            audit(db, 'study_session_started', key, now())
        return {'id': key, 'state': 'open', 'version': 1}

    @app.post('/api/study-sessions/{key}/close')
    def close(key: str, body: Transition, owner: Owner):
        with store.connect() as db:
            row = db.execute('SELECT * FROM study_sessions WHERE id=?', (key,)).fetchone()
            if not row or row['state'] != 'open' or row['version'] != body.version:
                raise HTTPException(409, 'Session changed or is already closed.')
            value = json.loads(row['payload'])
            value['closed_at'] = now()
            db.execute("UPDATE study_sessions SET payload=?,state='closed',version=version+1 WHERE id=?", (json.dumps(value),key))
            audit(db, 'study_session_closed', key, now())
        return {'state': 'closed'}
