"""Check Listen exports locally and summarize annotation coverage, not meaning.

No audio is read. Checksums, origins, labels and observation sources are declared
metadata. This report never grants consent, approves data or creates a split.
"""
import argparse
from collections import Counter
import json
import math
from pathlib import Path
import re

from .animal_context import validate_animal

SCHEMA = 'talk2nature.annotation.v1'


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def validate(document):
    if not isinstance(document, dict) or document.get('schema') != SCHEMA or document.get('tool_version') != '0.1.0':
        raise ValueError('Unsupported annotation format/version.')
    if 'animal_context' in document:
        validate_animal(document['animal_context'])
    recording = document.get('recording')
    if not isinstance(recording, dict):
        raise ValueError('Missing recording metadata.')
    if not isinstance(recording.get('sha256'), str) or not re.fullmatch('[a-f0-9]{64}', recording['sha256']):
        raise ValueError('Invalid recording checksum.')
    duration = recording.get('duration_seconds')
    if not number(duration) or not 0 < duration <= 120:
        raise ValueError('Recording duration must be positive and at most 120 seconds.')
    if type(recording.get('sample_rate')) is not int or not 8000 <= recording['sample_rate'] <= 192000 or type(recording.get('channels')) is not int or recording['channels'] not in (1, 2):
        raise ValueError('Invalid sample rate/channels.')
    if recording.get('origin') not in ('synthetic', 'user-supplied'):
        raise ValueError('Declare recording origin.')
    for key in ('recording_id', 'session_id', 'individual_id', 'annotator_id'):
        value = recording.get(key)
        if not isinstance(value, str) or not 1 <= len(value) <= 80 or value != value.strip():
            raise ValueError(f'Invalid {key}.')
    events = document.get('events')
    if not isinstance(events, list) or len(events) > 1000:
        raise ValueError('Use at most 1,000 events.')
    ids = set()
    for event in events:
        if not isinstance(event, dict) or type(event.get('id')) is not int or not 0 < event['id'] <= 9007199254740991 or event['id'] in ids:
            raise ValueError('Event IDs must be distinct positive safe integers.')
        ids.add(event['id'])
        start, end = event.get('start_seconds'), event.get('end_seconds')
        if not number(start) or not number(end) or not 0 <= start < end <= duration:
            raise ValueError('Event interval is outside the recording or empty.')
        if event.get('kind') not in ('uncertain', 'vocalization', 'other sound') or event.get('context') not in ('unknown', 'feeding', 'resting', 'moving', 'social interaction'):
            raise ValueError('Invalid sound/context label.')
        if event.get('context_source') not in ('not observed', 'direct observation', 'synchronized video') or event.get('confidence') not in ('uncertain', 'clear'):
            raise ValueError('Invalid observation source/confidence.')
        if event['context'] != 'unknown' and event['context_source'] == 'not observed':
            raise ValueError('Context must come from an independent observation, or remain unknown.')
        if not isinstance(event.get('notes'), str) or len(event['notes']) > 500:
            raise ValueError('Invalid event notes.')
    return document


def coverage(events):
    end, total = 0, 0
    for event in sorted(events, key=lambda e: (e['start_seconds'], e['end_seconds'])):
        total += max(0, event['end_seconds'] - max(end, event['start_seconds']))
        end = max(end, event['end_seconds'])
    return total


def report(document):
    validate(document)
    events, recording = document['events'], document['recording']
    independent = [e for e in events if e['context'] != 'unknown' and e['context_source'] != 'not observed']
    ordered = sorted(events, key=lambda e: (e['start_seconds'], e['end_seconds']))
    overlap_pairs = sum(a['end_seconds'] > b['start_seconds'] for i, a in enumerate(ordered) for b in ordered[i + 1:])
    warnings = []
    if not events: warnings.append('No events have been annotated.')
    if overlap_pairs: warnings.append('Overlapping intervals need review; union coverage counts each instant once.')
    if any(e['context'] == 'unknown' for e in events): warnings.append('Unknown context cannot be used as an independently observed behavior label.')
    if any(recording[k].lower() in ('unknown', 'na', 'n/a') for k in ('individual_id', 'session_id')):
        warnings.append('Unknown animal/session identity prevents an identity/session holdout claim.')
    if recording['origin'] == 'synthetic': warnings.append('Synthetic fixture: no biological result can be inferred.')
    return {
        'report_schema': 'talk2nature.annotation-report.v1',
        'declared_animal_context': document.get('animal_context'),
        'recording_id': recording['recording_id'], 'declared_source_sha256': recording['sha256'],
        'declared_origin': recording['origin'], 'duration_seconds': recording['duration_seconds'],
        'event_count': len(events), 'annotated_union_seconds': round(coverage(events), 6),
        'context_observed_union_seconds': round(coverage(independent), 6),
        'context_counts': dict(sorted(Counter(e['context'] for e in events).items())),
        'kind_counts': dict(sorted(Counter(e['kind'] for e in events).items())),
        'uncertain_event_count': sum(e['confidence'] == 'uncertain' for e in events),
        'overlapping_pair_count': overlap_pairs, 'warnings': warnings,
        'limitations': ['No audio, permission, identity, origin or label truth has been independently verified.',
                        'Coverage describes marked intervals, not all vocalizations or annotation accuracy.',
                        'A valid export is not an admitted dataset, model result or translation.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('labels', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        if args.labels.stat().st_size > 2 * 1024 * 1024:
            raise ValueError('Label files must be smaller than 2 MB.')
        result = report(json.loads(args.labels.read_text()))
        output = json.dumps(result, indent=2) + '\n'
        if args.output:
            if args.output.resolve() == args.labels.resolve():
                raise ValueError('Output must not overwrite the input.')
            args.output.parent.mkdir(parents=True, exist_ok=True)
            # Refuse accidental replacement, including symlinks.
            with args.output.open('x') as target: target.write(output)
        print(output, end='')
    except (ValueError, OSError) as error:
        parser.exit(2, f'Annotation report refused: {error}\n')


if __name__ == '__main__':
    main()
