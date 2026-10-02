"""Synthetic-only media and model provenance. No bytes, uploads or ML execution."""
import json
import math
import secrets
from typing import Annotated, Literal

from fastapi import Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field, StrictBool, model_validator

from admin.catalog import fingerprint
from admin.store import audit

Key = Annotated[str, Field(min_length=1, max_length=80)]
Sha = Annotated[str, Field(pattern=r'^[0-9a-f]{64}$')]
Nonnegative = Annotated[float, Field(ge=0, allow_inf_nan=False)]
Positive = Annotated[float, Field(gt=0, allow_inf_nan=False)]
Context = Literal['resting', 'moving', 'feeding', 'social']


class Input(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True, allow_inf_nan=False)
    synthetic: StrictBool


class Media(Input):
    observation_id: Key
    modality: Literal['audio', 'video']
    sha256: Sha
    byte_count: int = Field(strict=True, gt=0, le=100_000_000)
    duration_ms: Positive = Field(le=120_000)
    codec: Literal['pcm_s16le', 'h264', 'vp9']
    sample_rate: int | None = Field(default=None, strict=True, ge=8000, le=384000)
    frame_rate: Positive | None = Field(default=None, le=240)
    device_alias: str = Field(min_length=1, max_length=80)
    descriptor_kind: Literal['invented_fixture_no_object']

    @model_validator(mode='after')
    def format_matches_modality(self):
        if self.modality == 'audio':
            if self.codec != 'pcm_s16le' or self.sample_rate is None or self.frame_rate is not None:
                raise ValueError('Audio requires PCM and a sample rate.')
        elif self.codec == 'pcm_s16le' or self.frame_rate is None or self.sample_rate is not None:
            raise ValueError('Video requires a frame rate and a video codec.')
        return self


class Alignment(Input):
    audio_id: Key
    video_id: Key
    offset_ms: float = Field(ge=-120000, le=120000)
    drift_ppm: float = Field(ge=-10000, le=10000)
    uncertainty_ms: Nonnegative = Field(le=120000)
    audio_start_ms: Nonnegative
    audio_end_ms: Positive
    method: Literal['synthetic_fixture_clock']
    method_version: str = Field(min_length=1, max_length=80)


class Split(BaseModel):
    model_config = ConfigDict(extra='forbid')
    observation_id: Key
    partition: Literal['train', 'validation', 'test']


class Run(Input):
    release_id: Key
    media_ids: list[Key] = Field(min_length=1, max_length=100)
    alignment_ids: list[Key] = Field(default_factory=list, max_length=50)
    code_revision: str = Field(pattern=r'^[0-9a-f]{40}$')
    checkpoint_sha256: Sha
    checkpoint_license: str = Field(min_length=1, max_length=120)
    environment_sha256: Sha
    seed: int = Field(strict=True, ge=0, le=2147483647)
    splits: list[Split] = Field(min_length=1, max_length=100)
    purpose: Literal['synthetic_pipeline_rehearsal']


class Result(Input):
    run_id: Key
    media_id: Key
    start_ms: Nonnegative
    end_ms: Positive
    probabilities: dict[Context, Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]] = Field(min_length=1, max_length=4)
    abstained: StrictBool
    calibration: Literal['unvalidated_synthetic']


def gate(body):
    if not body.synthetic:
        raise HTTPException(409, 'Only invented metadata rehearsal is available. Real media and results are not admitted.')


def bounded(db, table, limit):
    # table is an internal literal at each call site, never an input identifier.
    if db.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0] >= limit:
        raise HTTPException(409, 'The synthetic lineage rehearsal has reached its record limit.')


def active_media(db, key):
    row = db.execute('SELECT * FROM research_media WHERE id=?', (key,)).fetchone()
    if not row or row['state'] != 'active':
        raise HTTPException(409, 'Select active media metadata.')
    if fingerprint(json.loads(row['payload'])) != row['fingerprint']:
        raise HTTPException(409, 'Media metadata no longer matches its fingerprint.')
    return row


def release_records(db, key):
    row = db.execute('SELECT * FROM releases WHERE id=?', (key,)).fetchone()
    if not row or row['revoked']:
        raise HTTPException(409, 'Select a current reviewed training release.')
    records = []
    for member in json.loads(row['members']):
        item = db.execute('SELECT * FROM observations WHERE id=?', (member,)).fetchone()
        if not item or item['state'] != 'released':
            raise HTTPException(409, 'Release membership is no longer available.')
        payload = json.loads(item['payload'])
        review = payload.get('review', {})
        if (not payload.get('synthetic') or not payload.get('consent_training')
                or review.get('decision') != 'accept'
                or not all(review.get('checks', {}).get(f) is True for f in
                           ('rights_checked', 'consent_checked', 'privacy_checked', 'label_checked'))):
            raise HTTPException(409, 'Each input needs its stored rights, consent and label review.')
        records.append({'id': member, **payload})
    if fingerprint(records) != row['fingerprint']:
        raise HTTPException(409, 'The release no longer matches its frozen content.')
    return row, records


def invalidate_lineage(db, observation_id, now):
    """Part of the observation withdrawal transaction; never leaves live derivatives."""
    media = [r['id'] for r in db.execute('SELECT id FROM research_media WHERE observation_id=?', (observation_id,))]
    runs = set()
    for key in media:
        runs.update(r['run_id'] for r in db.execute('SELECT run_id FROM model_inputs WHERE media_id=?', (key,)))
        db.execute("UPDATE media_sync SET state='withdrawn',payload='{}' WHERE audio_id=? OR video_id=?", (key, key))
        db.execute("UPDATE research_media SET state='withdrawn',payload='{}' WHERE id=?", (key,))
    # A release can be an input dependency even if its withdrawn record has no
    # media in a future run format. Follow explicit release membership as well.
    for row in db.execute('SELECT r.id,r.members,m.id AS run_id FROM releases r JOIN model_runs m ON r.id=m.release_id'):
        if observation_id in json.loads(row['members']):
            runs.add(row['run_id'])
    for key in sorted(runs):
        db.execute("UPDATE model_results SET state='withdrawn',payload='{}' WHERE run_id=?", (key,))
        db.execute("UPDATE model_runs SET state='invalidated',payload='{}' WHERE id=?", (key,))
        audit(db, 'model_run_invalidated', key, now())


def register_lineage(app, store, require_owner, now):
    Owner = Annotated[dict, Depends(require_owner)]

    @app.get('/api/lineage')
    def inventory(owner: Owner):
        with store.connect() as db:
            return {table: [{**dict(r), 'payload': json.loads(r['payload'])} for r in
                            db.execute(f'SELECT * FROM {table} ORDER BY created,id')]
                    for table in ('research_media', 'media_sync', 'model_runs', 'model_results')}

    @app.post('/api/media', status_code=201)
    def media(body: Media, owner: Owner):
        gate(body)
        with store.connect() as db:
            bounded(db, 'research_media', 2000)
            obs = db.execute('SELECT * FROM observations WHERE id=?', (body.observation_id,)).fetchone()
            link = db.execute('SELECT * FROM observation_links WHERE observation_id=?', (body.observation_id,)).fetchone()
            if not obs or obs['state'] != 'quarantined' or not link:
                raise HTTPException(409, 'Attach media to a linked synthetic observation before review.')
            payload = json.loads(obs['payload'])
            if not payload.get('synthetic') or not payload.get('consent_review'):
                raise HTTPException(409, 'Synthetic review permission is required.')
            value = body.model_dump(mode='json')
            value['notice'] = 'Invented descriptor; hash and device declarations are not verified media or rights.'
            key = secrets.token_hex(12); checksum = fingerprint(value)
            db.execute('INSERT INTO research_media VALUES(?,?,?,?,?,?,?,?)',
                       (key, body.observation_id, link['study_session_id'], body.modality, json.dumps(value), checksum, 'active', now()))
            audit(db, 'media_descriptor_created', key, now())
        return {'id': key, 'fingerprint': checksum, 'state': 'active', 'synthetic': True}

    @app.post('/api/media-alignments', status_code=201)
    def alignment(body: Alignment, owner: Owner):
        gate(body)
        with store.connect() as db:
            bounded(db, 'media_sync', 1000)
            audio, video = active_media(db, body.audio_id), active_media(db, body.video_id)
            if audio['modality'] != 'audio' or video['modality'] != 'video' or audio['study_session_id'] != video['study_session_id']:
                raise HTTPException(409, 'Alignment needs audio and video from the same study session.')
            for item in (audio, video):
                if db.execute('SELECT state FROM observations WHERE id=?', (item['observation_id'],)).fetchone()['state'] != 'quarantined':
                    raise HTTPException(409, 'Alignment is frozen when an observation is reviewed.')
            a, v = json.loads(audio['payload']), json.loads(video['payload'])
            start = body.audio_start_ms * (1 + body.drift_ppm / 1e6) + body.offset_ms
            end = body.audio_end_ms * (1 + body.drift_ppm / 1e6) + body.offset_ms
            if (body.audio_start_ms >= body.audio_end_ms or body.audio_end_ms > a['duration_ms']
                    or start - body.uncertainty_ms < 0 or end + body.uncertainty_ms > v['duration_ms']):
                raise HTTPException(422, 'The alignment and uncertainty window must fit both media durations.')
            value = body.model_dump(mode='json')
            value['mapping'] = 'video_ms = audio_ms * (1 + drift_ppm / 1000000) + offset_ms'
            key = secrets.token_hex(12); checksum = fingerprint(value)
            db.execute('INSERT INTO media_sync VALUES(?,?,?,?,?,?,?)',
                       (key, body.audio_id, body.video_id, json.dumps(value), checksum, 'active', now()))
            audit(db, 'alignment_created', key, now())
        return {'id': key, 'fingerprint': checksum}

    @app.post('/api/model-runs', status_code=201)
    def run(body: Run, owner: Owner):
        gate(body)
        with store.connect() as db:
            bounded(db, 'model_runs', 200)
            release, records = release_records(db, body.release_id)
            members = {r['id'] for r in records}
            if len(set(body.media_ids)) != len(body.media_ids) or len(set(body.alignment_ids)) != len(body.alignment_ids):
                raise HTTPException(422, 'Duplicate model input IDs.')
            media = [active_media(db, key) for key in sorted(body.media_ids)]
            if {r['observation_id'] for r in media} != members:
                raise HTTPException(409, 'Media must cover exactly the selected release observations.')
            splits = {s.observation_id: s.partition for s in body.splits}
            if len(splits) != len(body.splits) or set(splits) != members:
                raise HTTPException(422, 'Provide one split assignment per release observation.')
            subjects, studies = {}, set()
            for record in records:
                study = record.get('study', {})
                studies.add(study.get('id'))
                previous = subjects.setdefault(record['individual_id'], splits[record['id']])
                if previous != splits[record['id']]:
                    raise HTTPException(409, 'The same individual cannot occur in different data splits.')
            if None in studies or len(studies) != 1:
                raise HTTPException(409, 'Use one frozen study and codebook per model rehearsal.')
            study = db.execute('SELECT payload,fingerprint FROM studies WHERE id=?', (next(iter(studies)),)).fetchone()
            alignments, aligned_media = [], set()
            for key in sorted(body.alignment_ids):
                row = db.execute('SELECT * FROM media_sync WHERE id=?', (key,)).fetchone()
                if (not row or row['state'] != 'active' or row['audio_id'] not in body.media_ids or row['video_id'] not in body.media_ids
                        or fingerprint(json.loads(row['payload'])) != row['fingerprint']):
                    raise HTTPException(409, 'Use an active alignment entirely within these model inputs.')
                alignments.append({'id': key, 'fingerprint': row['fingerprint']})
                aligned_media.update((row['audio_id'], row['video_id']))
            if {m['modality'] for m in media} == {'audio', 'video'} and aligned_media != set(body.media_ids):
                raise HTTPException(409, 'Every multimodal input must have explicit alignment provenance.')
            value = body.model_dump(mode='json')
            value.update(release_fingerprint=release['fingerprint'], study_fingerprint=study['fingerprint'],
                         codebook=json.loads(study['payload'])['codebook'],
                         input_fingerprints={m['id']: m['fingerprint'] for m in media}, alignments=alignments,
                         split_fingerprint=fingerprint(splits),
                         notice='Registered synthetic specification only; no model ran and no performance was validated.')
            key = secrets.token_hex(12); checksum = fingerprint(value)
            db.execute('INSERT INTO model_runs VALUES(?,?,?,?,?,?)', (key, body.release_id, json.dumps(value), checksum, 'registered', now()))
            db.executemany('INSERT INTO model_inputs VALUES(?,?,?)', [(key, m['id'], m['fingerprint']) for m in media])
            audit(db, 'model_specification_registered', key, now())
        return {'id': key, 'fingerprint': checksum, 'state': 'registered', 'executed': False}

    @app.post('/api/model-results', status_code=201)
    def result(body: Result, owner: Owner):
        gate(body)
        with store.connect() as db:
            bounded(db, 'model_results', 2000)
            row = db.execute('SELECT * FROM model_runs WHERE id=?', (body.run_id,)).fetchone()
            member = db.execute('SELECT * FROM model_inputs WHERE run_id=? AND media_id=?', (body.run_id, body.media_id)).fetchone()
            if not row or row['state'] != 'registered' or not member:
                raise HTTPException(409, 'Select an active run and one of its frozen inputs.')
            spec = json.loads(row['payload'])
            if fingerprint(spec) != row['fingerprint']:
                raise HTTPException(409, 'Model specification no longer matches its fingerprint.')
            release_records(db, row['release_id'])
            for frozen in db.execute('SELECT * FROM model_inputs WHERE run_id=?', (body.run_id,)):
                if active_media(db, frozen['media_id'])['fingerprint'] != frozen['media_fingerprint']:
                    raise HTTPException(409, 'A model input version changed.')
            media = active_media(db, body.media_id)
            if media['fingerprint'] != member['media_fingerprint']:
                raise HTTPException(409, 'Model input version changed.')
            if (body.start_ms >= body.end_ms or body.end_ms > json.loads(media['payload'])['duration_ms']
                    or set(body.probabilities) != set(spec['codebook'])
                    or not math.isclose(sum(body.probabilities.values()), 1, rel_tol=0, abs_tol=1e-6)):
                raise HTTPException(422, 'Use an in-bounds interval and a complete codebook probability distribution.')
            valid_windows = []
            for frozen in spec['alignments']:
                pair = db.execute('SELECT * FROM media_sync WHERE id=?', (frozen['id'],)).fetchone()
                if (not pair or pair['state'] != 'active' or pair['fingerprint'] != frozen['fingerprint']
                        or fingerprint(json.loads(pair['payload'])) != pair['fingerprint']):
                    raise HTTPException(409, 'Alignment provenance changed.')
                alignment = json.loads(pair['payload'])
                start, end = alignment['audio_start_ms'], alignment['audio_end_ms']
                if body.media_id == pair['audio_id']:
                    valid_windows.append((start, end))
                elif body.media_id == pair['video_id']:
                    scale = 1 + alignment['drift_ppm'] / 1e6
                    valid_windows.append((start * scale + alignment['offset_ms'] + alignment['uncertainty_ms'],
                                          end * scale + alignment['offset_ms'] - alignment['uncertainty_ms']))
            if spec['alignments'] and not any(body.start_ms >= a and body.end_ms <= b for a, b in valid_windows):
                raise HTTPException(422, 'Multimodal result intervals must fit an alignment validity window.')
            value = body.model_dump(mode='json')
            value['notice'] = 'Invented model output for pipeline testing, not a behavior label or measured result.'
            key = secrets.token_hex(12); checksum = fingerprint(value)
            db.execute('INSERT INTO model_results VALUES(?,?,?,?,?,?,?)',
                       (key, body.run_id, body.media_id, json.dumps(value), checksum, 'active', now()))
            audit(db, 'synthetic_result_recorded', key, now())
        return {'id': key, 'fingerprint': checksum, 'synthetic': True}
