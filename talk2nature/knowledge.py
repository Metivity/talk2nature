"""Deterministic, provenance-aware graph of curated public metadata.

Edges describe citations and catalog relationships, not corroboration or meaning.
This graph is a projection, never a training manifest or an upload endpoint.
"""
import hashlib
import json

SCHEMA = 'talk2nature.knowledge.v1'


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def version_id(key, checksum):
    return f'{key}@{checksum}'


def catalog_graph(entries):
    nodes, edges, current = [], [], {}
    for entry in sorted(entries, key=lambda e: e['key']):
        key, payload = entry['key'], entry['payload']
        if key in current or entry['kind'] not in {'source', 'note', 'resource'}:
            raise ValueError('Duplicate or unsupported public catalog record.')
        checksum = fingerprint(payload)
        identity = version_id(key, checksum)
        current[key] = identity
        # Explicit field allowlist; private payloads and freeform future fields do
        # not silently become public graph properties.
        node = {'id': identity, 'key': key, 'kind': entry['kind'], 'title': entry['title'],
                'fingerprint': checksum, 'visibility': 'public_metadata'}
        for field in ('url', 'reviewed', 'checked', 'review_depth', 'review_stage', 'taxon'):
            if field in payload:
                node[field] = payload[field]
        nodes.append(node)
    for entry in sorted(entries, key=lambda e: e['key']):
        if entry['kind'] == 'note':
            for source_id in sorted(set(entry['payload'].get('source_ids', []))):
                key = f'source:{source_id}'
                if key not in current:
                    raise ValueError('Evidence note cites a missing source.')
                edges.append({'from': current[entry['key']], 'relation': 'cites', 'to': current[key],
                              'basis': 'Explicit source_ids in this note; target is the catalog version at graph build time.'})
    return finish_graph(nodes, edges, 'public_metadata')


def finish_graph(nodes, edges, visibility):
    nodes = sorted(nodes, key=lambda n: n['id'])
    edges = sorted(edges, key=lambda e: (e['from'], e['relation'], e['to']))
    identities = {n['id'] for n in nodes}
    if len(identities) != len(nodes) or any(e['from'] not in identities or e['to'] not in identities for e in edges):
        raise ValueError('Duplicate node or dangling graph edge.')
    body = {'schema': SCHEMA, 'visibility': visibility, 'nodes': nodes, 'edges': edges,
            'notice': 'Connections record provenance, not scientific agreement. Not an admitted training dataset.'}
    return {**body, 'fingerprint': fingerprint(body)}
