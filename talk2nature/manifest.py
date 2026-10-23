"""Validate metadata and split connected recordings without identity/session leakage.

This validates declarations, not the truth of consent, licenses or hashes. It does
not load audio, prove independence, detect near duplicates or evaluate a model.
"""
import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path

TEXT_FIELDS = ('recording_id', 'species', 'session_id', 'source_sha256', 'context_label', 'license', 'provenance', 'annotator_id')
BASE_GROUP_DIMENSIONS = ('individual_ids', 'session_id', 'source_sha256')
SPLIT_ALGORITHM = 'connected-groups-v1'
GROUP_DIMENSION_PATTERN = re.compile(r'^[a-z][a-z0-9_-]{0,31}$')
UNKNOWN_GROUP_IDS = {'unknown', 'na', 'n/a', 'none', 'null', 'tbd', 'pending'}


def normalize_group_dimensions(dimensions):
    if dimensions is None:
        return ()
    if not isinstance(dimensions, (list, tuple)):
        raise ValueError('Additional group dimensions must be a list of dimension names.')
    normalized = []
    for dimension in dimensions:
        if (not isinstance(dimension, str) or not GROUP_DIMENSION_PATTERN.fullmatch(dimension)
                or dimension in ('individual_ids', 'session_id', 'source_sha256')):
            raise ValueError('Additional group dimensions must be unique lowercase names and cannot repeat a built-in dimension.')
        if dimension in normalized:
            raise ValueError(f'Duplicate group dimension: {dimension}')
        normalized.append(dimension)
    return tuple(sorted(normalized))


def validate(records, group_dimensions=()):
    if not isinstance(records, list) or not records:
        raise ValueError('Manifest must be a nonempty JSON array of recording records.')
    group_dimensions = normalize_group_dimensions(group_dimensions)
    seen = set()
    for i, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError(f'Record {i} must be an object.')
        for field in TEXT_FIELDS:
            if not isinstance(record.get(field), str) or not record[field].strip():
                raise ValueError(f'Record {i}: {field} must be a nonempty string.')
            if record[field] != record[field].strip():
                raise ValueError(f'Record {i}: trim whitespace from {field}.')
        if record['recording_id'] in seen:
            raise ValueError(f'Duplicate recording_id: {record["recording_id"]}')
        seen.add(record['recording_id'])
        individuals = record.get('individual_ids')
        if not isinstance(individuals, list) or not individuals or any(not isinstance(x, str) or not x.strip() or x != x.strip() or x.lower() in UNKNOWN_GROUP_IDS for x in individuals):
            raise ValueError(f'Record {i}: individual_ids must list known pseudonymous individuals; unknown identities cannot support an individual holdout.')
        if len(set(individuals)) != len(individuals):
            raise ValueError(f'Record {i}: duplicate individual IDs.')
        if record['session_id'].lower() in UNKNOWN_GROUP_IDS:
            raise ValueError(f'Record {i}: session_id must be a known pseudonymous session; placeholders cannot support a session holdout.')
        group_ids = record.get('group_ids', {})
        if not isinstance(group_ids, dict):
            raise ValueError(f'Record {i}: group_ids must map grouping dimensions to pseudonymous ID lists.')
        for dimension, ids in group_ids.items():
            if (not isinstance(dimension, str) or not GROUP_DIMENSION_PATTERN.fullmatch(dimension)
                    or dimension in ('individual_ids', 'session_id', 'source_sha256')):
                raise ValueError(f'Record {i}: invalid additional group dimension name.')
            if (not isinstance(ids, list) or not ids
                    or any(not isinstance(value, str) or not value.strip() or value != value.strip()
                           or value.lower() in UNKNOWN_GROUP_IDS for value in ids)):
                raise ValueError(f'Record {i}: group_ids[{dimension!r}] must list known, trimmed pseudonymous IDs.')
            if len(set(ids)) != len(ids):
                raise ValueError(f'Record {i}: duplicate IDs in group_ids[{dimension!r}].')
        for dimension in group_dimensions:
            if dimension not in group_ids:
                raise ValueError(f'Record {i}: selected group dimension {dimension!r} is missing.')
        if not re.fullmatch('[a-f0-9]{64}', record['source_sha256']):
            raise ValueError(f'Record {i}: source_sha256 must be the lowercase SHA-256 of the original source recording, shared by all its excerpts.')
        if record['license'].lower() in ('unknown','tbd','n/a','pending'):
            raise ValueError(f'Record {i}: unresolved rights cannot enter the evaluation manifest.')
        if record.get('consent_status') not in ('approved','not_required'):
            raise ValueError(f'Record {i}: consent_status must be approved or not_required, with a justification in provenance.')
        if record.get('label_source') not in ('video','direct_observation'):
            raise ValueError(f'Record {i}: context labels must come from video or direct_observation, independently of audio predictions.')
        if record.get('sensitive_location') is not False:
            raise ValueError(f'Record {i}: redact sensitive locations before using this shareable manifest.')
        if not isinstance(record.get('synthetic'), bool):
            raise ValueError(f'Record {i}: explicitly declare synthetic true or false.')
        try:
            timestamp = datetime.fromisoformat(record['recorded_at'].replace('Z','+00:00'))
        except (KeyError,TypeError,ValueError,AttributeError) as exc:
            raise ValueError(f'Record {i}: recorded_at must be an ISO-8601 timestamp with timezone.') from exc
        if timestamp.utcoffset() is None:
            raise ValueError(f'Record {i}: recorded_at needs a timezone.')
    if len({r['synthetic'] for r in records}) > 1:
        raise ValueError('Do not mix synthetic fixtures with real observations.')
    return records


def connected_groups(records, group_dimensions=()):
    """Transitive grouping across built-in and explicitly selected dimensions."""
    group_dimensions = normalize_group_dimensions(group_dimensions)
    parent = list(range(len(records)))
    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    owners = {}
    for i, r in enumerate(records):
        keys = [('individual', identity) for identity in r['individual_ids']]
        keys += [('session',r['session_id']),('source',r['source_sha256'])]
        for dimension in group_dimensions:
            keys += [(dimension, value) for value in r['group_ids'][dimension]]
        for key in keys:
            if key in owners:
                parent[find(i)] = find(owners[key])
            else:
                owners[key] = i
    groups = {}
    for i,r in enumerate(records):
        groups.setdefault(find(i),[]).append(r)
    return [sorted(group,key=lambda r:r['recording_id']) for group in groups.values()]


def split_manifest(records, seed='talk2nature-v1', group_dimensions=()):
    group_dimensions = normalize_group_dimensions(group_dimensions)
    validate(records, group_dimensions)
    groups = connected_groups(records, group_dimensions)
    if len(groups) < 3:
        raise ValueError(f'Only {len(groups)} independent connected group(s). Need at least 3 for nonempty train/validation/test; one animal cannot support an individual holdout.')
    def sort_key(group):
        key = json.dumps([seed,[r['recording_id'] for r in group]],separators=(',',':'))
        return hashlib.sha256(key.encode()).hexdigest()
    groups.sort(key=sort_key)
    n_validation = max(1,round(len(groups)*.15))
    n_test = max(1,round(len(groups)*.15))
    n_train = len(groups)-n_validation-n_test
    assignments = {}
    group_counts = {'train':0,'validation':0,'test':0}
    for i,group in enumerate(groups):
        partition = 'train' if i<n_train else ('validation' if i<n_train+n_validation else 'test')
        group_counts[partition] += 1
        for record in group:
            assignments[record['recording_id']] = partition
    counts = {p:sum(v==p for v in assignments.values()) for p in ('train','validation','test')}
    context_counts = {p:{} for p in counts}
    for r in records:
        bucket=context_counts[assignments[r['recording_id']]]
        bucket[r['context_label']]=bucket.get(r['context_label'],0)+1
    declared_context_labels=sorted({r['context_label'] for r in records})
    context_label_coverage={
        partition:{
            'present':sorted(context_counts[partition]),
            'missing':[label for label in declared_context_labels if label not in context_counts[partition]],
        }
        for partition in counts
    }
    canonical_records=json.dumps(sorted(records,key=lambda r:r['recording_id']),sort_keys=True,separators=(',',':'))
    split_policy={'base_dimensions':list(BASE_GROUP_DIMENSIONS),'additional_dimensions':list(group_dimensions)}
    policy_fingerprint=json.dumps({'algorithm':SPLIT_ALGORITHM,'seed':seed,'grouping':split_policy},sort_keys=True,separators=(',',':'))
    return {'schema_version':3,'seed':seed,'synthetic':records[0]['synthetic'],
            'manifest_sha256':hashlib.sha256(canonical_records.encode()).hexdigest(),
            'split_algorithm':SPLIT_ALGORITHM,
            'split_policy':split_policy,
            'split_policy_sha256':hashlib.sha256(policy_fingerprint.encode()).hexdigest(),
            'group_count':len(groups),'group_counts':group_counts,
            'record_counts':counts,'context_counts':context_counts,
            'context_label_coverage':{'declared':declared_context_labels,'by_partition':context_label_coverage},
            'assignments':dict(sorted(assignments.items())),
            'limitations':['Approximately 70/15/15 by connected groups, not by recording count; with few groups the actual ratio can differ substantially, and partitions are not stratified.',
                           'Reported class counts are diagnostics, not permission to tune against the test set.',
                           'Context-label coverage reports presence only; it does not establish class balance, label reliability, or representativeness.',
                           'Only declared identities, sessions, source hashes and selected pseudonymous dimensions are enforced; verify relationships independently and assess near duplicates.',
                           'Unselected household, site, device, time, treatment and pretrained-model overlap need study-specific evaluation controls.',
                           'No audio has been inspected; rights and hashes are declared metadata, not verified evidence.']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest',type=Path)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--seed',default='talk2nature-v1')
    parser.add_argument('--group-dimension',action='append',default=[],metavar='NAME',
                        help='Additional pseudonymous split dimension, such as household or device. Repeat to require more dimensions.')
    args=parser.parse_args()
    try:
        result=split_manifest(json.loads(args.manifest.read_text()),args.seed,args.group_dimension)
        if args.output:
            if args.output.resolve() == args.manifest.resolve():
                raise ValueError('Output must not overwrite the input manifest.')
            args.output.parent.mkdir(parents=True,exist_ok=True)
            args.output.write_text(json.dumps(result,indent=2)+'\n')
    except (ValueError,OSError) as error:
        parser.exit(2,f'Manifest rejected: {error}\n')
    print(json.dumps({'synthetic':result['synthetic'],'connected_groups':result['group_count'],
                      'split_policy':result['split_policy'],'record_counts':result['record_counts'],
                      'group_counts':result['group_counts'],
                      'context_label_coverage':result['context_label_coverage'],
                      'split_policy_sha256':result['split_policy_sha256'],
                      'output':str(args.output) if args.output else None},indent=2))
    if not args.output:
        print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
