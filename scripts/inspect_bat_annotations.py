"""Produce an aggregate-only structural audit of the Egyptian fruit-bat labels.

The source file must match its bounded Figshare acquisition receipt. The report
never includes row values, file IDs, animal IDs, or free-text labels.
"""
import argparse
from collections import Counter
import csv
import hashlib
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FOLDER = ROOT / 'data/external/egyptian-fruit-bat-annotations'
EXPECTED_COLUMNS = [
    'FileID', 'Emitter', 'Addressee', 'Context',
    'Emitter pre-vocalization action', 'Addressee pre-vocalization action',
    'Emitter post-vocalization action', 'Addressee post-vocalization action',
    'Start sample', 'End sample',
]
CONTEXT_CODES = {
    '0': 'Unknown', '1': 'Separation', '2': 'Biting', '3': 'Feeding',
    '4': 'Fighting', '5': 'Grooming', '6': 'Isolation', '7': 'Kissing',
    '8': 'Landing', '9': 'Mating protest', '10': 'Threat-like',
    '11': 'General', '12': 'Sleeping',
}
PRE_ACTION_CODES = {
    '0': 'Unknown', '1': 'Fly in', '2': 'Present', '3': 'Crawl in',
}
POST_ACTION_CODES = {
    '0': 'Unknown', '1': 'Cower', '2': 'Fly away', '3': 'Stay',
    '4': 'Crawl away',
}
PUBLISHED_CONTEXT_COUNTS = {
    'Unknown': 640, 'Separation': 504, 'Biting': 1788, 'Feeding': 6683,
    'Fighting': 7963, 'Grooming': 383, 'Isolation': 5714, 'Kissing': 362,
    'Landing': 16, 'Mating protest': 2338, 'Threat-like': 1065,
    'General': 29627, 'Sleeping': 33997,
}
PUBLISHED_PRE_ACTION_COUNTS = {
    'Unknown': 13553, 'Fly in': 3909, 'Present': 158164, 'Crawl in': 6534,
}
PUBLISHED_POST_ACTION_COUNTS = {
    'Unknown': 13437, 'Cower': 77, 'Fly away': 6745, 'Stay': 155485,
    'Crawl away': 6416,
}


def inspect(folder=DEFAULT_FOLDER):
    folder = Path(folder)
    receipt = json.loads((folder / 'receipt.json').read_text())
    if receipt.get('resource_id') != 'egyptian-fruit-bat-annotations':
        raise ValueError('Receipt does not identify the reviewed Figshare annotation item.')
    if receipt.get('training_admitted') is not False:
        raise ValueError('Source receipt must remain outside training admission.')
    files = [f for f in receipt.get('files', []) if f.get('name') == 'Annotations.csv']
    if len(files) != 1:
        raise ValueError('Receipt must contain exactly one reviewed Annotations.csv file.')
    artifact = files[0]
    data = (folder / artifact['name']).read_bytes()
    sha256 = hashlib.sha256(data).hexdigest()
    md5 = hashlib.md5(data, usedforsecurity=False).hexdigest()
    if (len(data) != artifact.get('bytes') or sha256 != artifact.get('sha256')
            or md5 != artifact.get('md5')):
        raise ValueError('Annotation table differs from its collected size or checksums.')

    reader = csv.DictReader(io.StringIO(data.decode('utf-8-sig')))
    if reader.fieldnames != EXPECTED_COLUMNS:
        raise ValueError('Annotation table schema differs from the reviewed paper; inspect before interpreting.')

    nonempty = Counter()
    contexts = Counter()
    pre_actions = Counter()
    post_actions = Counter()
    file_ids = set()
    intervals = set()
    rows = malformed_rows = 0
    unknown_context_codes = unknown_pre_action_codes = unknown_post_action_codes = 0
    negative_emitter = negative_addressee = unknown_emitter = unknown_addressee = 0
    noninteger_identity_values = noninteger_sample_values = 0
    invalid_intervals = 0

    for row in reader:
        rows += 1
        if None in row or any(value is None for value in row.values()):
            malformed_rows += 1
            continue
        for column in EXPECTED_COLUMNS:
            nonempty[column] += bool(row[column].strip())

        file_id = row['FileID'].strip()
        file_ids.add(file_id)
        try:
            start = int(row['Start sample'].strip())
            end = int(row['End sample'].strip())
            if start < 0 or end <= start:
                invalid_intervals += 1
        except ValueError:
            noninteger_sample_values += 1
            start = end = None
        if start is not None and end is not None:
            intervals.add((file_id, start, end))

        for column, negative_counter, unknown_counter in (
            ('Emitter', 'emitter', 'emitter'),
            ('Addressee', 'addressee', 'addressee'),
        ):
            try:
                identity = int(row[column].strip())
                if identity < 0:
                    if negative_counter == 'emitter':
                        negative_emitter += 1
                    else:
                        negative_addressee += 1
                elif identity == 0:
                    if unknown_counter == 'emitter':
                        unknown_emitter += 1
                    else:
                        unknown_addressee += 1
            except ValueError:
                noninteger_identity_values += 1

        context = row['Context'].strip()
        if context in CONTEXT_CODES:
            contexts[CONTEXT_CODES[context]] += 1
        else:
            unknown_context_codes += 1
        for column in ('Emitter pre-vocalization action', 'Addressee pre-vocalization action'):
            code = row[column].strip()
            if code in PRE_ACTION_CODES:
                pre_actions[PRE_ACTION_CODES[code]] += 1
            else:
                unknown_pre_action_codes += 1
        for column in ('Emitter post-vocalization action', 'Addressee post-vocalization action'):
            code = row[column].strip()
            if code in POST_ACTION_CODES:
                post_actions[POST_ACTION_CODES[code]] += 1
            else:
                unknown_post_action_codes += 1

    if malformed_rows:
        raise ValueError('Malformed CSV rows found; no partial report was produced.')

    contexts = dict(sorted(contexts.items()))
    pre_actions = dict(sorted(pre_actions.items()))
    post_actions = dict(sorted(post_actions.items()))
    reference_matches = {
        'rows_match_paper_91080': rows == 91080,
        'context_counts_match_paper_table_4': contexts == PUBLISHED_CONTEXT_COUNTS,
        'combined_pre_action_counts_match_paper_table_4': pre_actions == PUBLISHED_PRE_ACTION_COUNTS,
        'combined_post_action_counts_match_paper_table_4': post_actions == PUBLISHED_POST_ACTION_COUNTS,
    }
    return {
        'resource_id': receipt['resource_id'],
        'source_version': receipt['resource']['version'],
        'source_url': artifact['url'],
        'source_bytes': len(data),
        'source_md5': md5,
        'source_sha256': sha256,
        'rows': rows,
        'columns': EXPECTED_COLUMNS,
        'nonempty': dict(nonempty),
        'malformed_rows': malformed_rows,
        'unique_file_ids': len(file_ids),
        'rows_beyond_unique_file_ids': rows - len(file_ids),
        'duplicate_file_interval_rows': rows - len(intervals),
        'invalid_or_reversed_sample_intervals': invalid_intervals,
        'noninteger_sample_values': noninteger_sample_values,
        'noninteger_identity_values': noninteger_identity_values,
        'zero_unknown_identity_rows': {'emitter': unknown_emitter, 'addressee': unknown_addressee},
        'negative_ambiguous_identity_rows': {'emitter': negative_emitter, 'addressee': negative_addressee},
        'published_category_counts': {
            'context': contexts,
            'pre_vocalization_action_across_both_roles': pre_actions,
            'post_vocalization_action_across_both_roles': post_actions,
        },
        'unmapped_category_code_rows': {
            'context': unknown_context_codes,
            'pre_vocalization_action': unknown_pre_action_codes,
            'post_vocalization_action': unknown_post_action_codes,
        },
        'matches_published_table_4_counts': reference_matches,
        'training_admitted': False,
        'limitations': [
            'A row is a video-derived vocal-interaction annotation, not a listener-validated message or necessarily an independent animal/session.',
            'Repeated file IDs can represent multiple annotated interactions within one WAV; row count is not a count of independent calls or trials.',
            'Negative emitter/addressee IDs mark role uncertainty in the paper; zero is the unknown code. Raw identifiers are not exported.',
            'Matching published category totals checks transcription and aggregation, not annotation truth, model performance or biological meaning.',
            'No audio, video, FileInfo timing, code, model weights or animal-held-out split was inspected or run.',
            'The public report contains aggregate counts and no row values, file IDs, animal IDs or free text.',
        ],
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--folder', type=Path, default=DEFAULT_FOLDER)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = json.dumps(inspect(args.folder), indent=2) + '\n'
    if args.output:
        args.output.write_text(result)
    else:
        print(result, end='')
