"""Owner-only graph projection of the existing transactional research database.

No extra fact store: withdrawals and frozen reference versions are resolved from
current authoritative rows in one transaction, on SQLite and PostgreSQL alike.
"""
import json
from typing import Annotated
from fastapi import Depends
from talk2nature.knowledge import catalog_graph, finish_graph, version_id


def private_graph(store):
    with store.connect() as db:
        rows = list(db.execute('''SELECT c.*,v.payload FROM evidence_catalog c JOIN evidence_versions v
            ON c.key=v.key AND c.fingerprint=v.fingerprint WHERE c.active=1'''))
        entries = [{'key': r['key'], 'kind': r['kind'], 'title': r['title'], 'payload': json.loads(r['payload'])} for r in rows]
        graph = catalog_graph(entries)
        nodes, edges = graph['nodes'], graph['edges']
        known = {n['id'] for n in nodes}
        for row in db.execute('SELECT * FROM studies ORDER BY id'):
            key = f"study:{row['id']}"
            value = json.loads(row['payload'])
            nodes.append({'id': key, 'kind': 'study', 'title': value['title'], 'visibility': 'owner_only',
                          'fingerprint': row['fingerprint'], 'state': row['state'], 'synthetic': True})
            for ref in db.execute('''SELECT e.*,v.payload FROM study_evidence e JOIN evidence_versions v
                ON e.evidence_key=v.key AND e.fingerprint=v.fingerprint WHERE e.study_id=?''', (row['id'],)):
                target = version_id(ref['evidence_key'], ref['fingerprint'])
                if target not in known:
                    payload = json.loads(ref['payload'])
                    nodes.append({'id': target, 'key': ref['evidence_key'], 'kind': ref['evidence_key'].split(':')[0],
                                  'title': payload['title'], 'fingerprint': ref['fingerprint'],
                                  'visibility': 'owner_only', 'historical': True})
                    known.add(target)
                edges.append({'from': key, 'relation': 'uses_frozen_evidence', 'to': target, 'basis': 'study_evidence foreign key and fingerprint'})
        for row in db.execute('SELECT id,study_id,state FROM study_sessions ORDER BY id'):
            key = f"session:{row['id']}"
            nodes.append({'id': key, 'kind': 'session', 'title': 'Synthetic study session', 'visibility': 'owner_only', 'state': row['state'], 'synthetic': True})
            edges.append({'from': key, 'relation': 'follows_protocol', 'to': f"study:{row['study_id']}", 'basis': 'study_sessions foreign key'})
        observations = set()
        for row in db.execute("SELECT id,state,version FROM observations WHERE state!='withdrawn' ORDER BY id"):
            key = f"observation:{row['id']}"
            observations.add(key)
            nodes.append({'id': key, 'kind': 'observation', 'title': 'Synthetic observation', 'visibility': 'owner_only', 'state': row['state'], 'version': row['version'], 'synthetic': True})
        for row in db.execute('SELECT * FROM observation_links ORDER BY observation_id'):
            key = f"observation:{row['observation_id']}"
            if key in observations:
                edges.append({'from': key, 'relation': 'observed_in', 'to': f"session:{row['study_session_id']}", 'basis': 'Validated observation_links foreign key'})
        for row in db.execute('SELECT id,members,revoked,fingerprint FROM releases ORDER BY id'):
            key = f"release:{row['id']}"
            nodes.append({'id': key, 'kind': 'release', 'title': 'Synthetic metadata release', 'visibility': 'owner_only', 'revoked': bool(row['revoked']), 'fingerprint': row['fingerprint'], 'synthetic': True})
            if not row['revoked']:
                for member in json.loads(row['members']):
                    target = f'observation:{member}'
                    if target not in observations:
                        raise ValueError('Unrevoked release references a missing observation.')
                    edges.append({'from': key, 'relation': 'contains', 'to': target, 'basis': 'Unrevoked release membership; export requires separate release checks'})
        media_ids = set()
        for row in db.execute("SELECT id,observation_id,study_session_id,modality,fingerprint FROM research_media WHERE state='active' ORDER BY id"):
            if f"observation:{row['observation_id']}" not in observations:
                continue
            key = f"media:{row['id']}"
            media_ids.add(row['id'])
            nodes.append({'id': key, 'kind': 'media', 'title': f"Synthetic {row['modality']} descriptor", 'visibility': 'owner_only',
                          'fingerprint': row['fingerprint'], 'synthetic': True})
            edges.extend([{'from': key, 'relation': 'documents', 'to': f"observation:{row['observation_id']}", 'basis': 'Media observation foreign key; descriptor only, no stored bytes'},
                          {'from': key, 'relation': 'captured_in', 'to': f"session:{row['study_session_id']}", 'basis': 'Linked observation session'}])
        alignment_ids = set()
        for row in db.execute("SELECT id,audio_id,video_id,fingerprint FROM media_sync WHERE state='active' ORDER BY id"):
            if row['audio_id'] in media_ids and row['video_id'] in media_ids:
                key = f"alignment:{row['id']}"
                alignment_ids.add(row['id'])
                nodes.append({'id': key, 'kind': 'alignment', 'title': 'Synthetic clock alignment', 'visibility': 'owner_only', 'fingerprint': row['fingerprint'], 'synthetic': True})
                for target in (row['audio_id'], row['video_id']):
                    edges.append({'from': key, 'relation': 'aligns', 'to': f'media:{target}', 'basis': 'Frozen explicit offset, drift, validity and uncertainty metadata'})
        runs = set()
        for row in db.execute('SELECT id,release_id,state,fingerprint,payload FROM model_runs ORDER BY id'):
            key = f"run:{row['id']}"
            nodes.append({'id': key, 'kind': 'model_run', 'title': 'Synthetic model specification', 'state': row['state'],
                          'visibility': 'owner_only', 'fingerprint': row['fingerprint'], 'synthetic': True})
            if row['state'] != 'registered':
                continue
            runs.add(row['id'])
            for pair in json.loads(row['payload'])['alignments']:
                if pair['id'] in alignment_ids:
                    edges.append({'from': key, 'relation': 'uses_alignment', 'to': f"alignment:{pair['id']}", 'basis': 'Frozen alignment fingerprint in model specification'})
            edges.append({'from': key, 'relation': 'uses_release', 'to': f"release:{row['release_id']}", 'basis': 'Reviewed synthetic release and content fingerprint; no model execution'})
            for item in db.execute('SELECT media_id FROM model_inputs WHERE run_id=? ORDER BY media_id', (row['id'],)):
                if item['media_id'] in media_ids:
                    edges.append({'from': key, 'relation': 'uses_media', 'to': f"media:{item['media_id']}", 'basis': 'Frozen model input membership and metadata fingerprint'})
        for row in db.execute("SELECT id,run_id,media_id,fingerprint FROM model_results WHERE state='active' ORDER BY id"):
            if row['run_id'] in runs and row['media_id'] in media_ids:
                key = f"result:{row['id']}"
                nodes.append({'id': key, 'kind': 'model_result', 'title': 'Invented model output', 'visibility': 'owner_only', 'fingerprint': row['fingerprint'], 'synthetic': True})
                edges.extend([{'from': f"run:{row['run_id']}", 'relation': 'produces', 'to': key, 'basis': 'Synthetic output registration; not a scientific observation'},
                              {'from': key, 'relation': 'predicts_on', 'to': f"media:{row['media_id']}", 'basis': 'Frozen input foreign key and bounded interval'}])
        return finish_graph(nodes, edges, 'owner_only')


def register_knowledge(app, store, require_owner):
    Owner = Annotated[dict, Depends(require_owner)]

    @app.get('/api/knowledge-graph')
    def graph(owner: Owner):
        return private_graph(store)
