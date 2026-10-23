"""Produce an aggregate-only structural audit of the Egyptian fruit-bat labels.

The source file must match its bounded Figshare acquisition receipt. The report
never includes row values, file IDs, animal IDs, or free-text labels.
"""
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path
from statistics import median

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
PAPER_SAMPLE_RATE_HZ = 250_000
PAPER_MAX_CALL_SECONDS = 3
PUBLISHED_PAPER_FILTERED_ROWS = 35_074


def _connected_group_summary(rows, participant_fields):
    """Summarize file/participant components without returning identifiers."""
    parent = {}
    rank = {}

    def find(node):
        parent.setdefault(node, node)
        rank.setdefault(node, 0)
        root = node
        while parent[root] != root:
            root = parent[root]
        while parent[node] != node:
            next_node = parent[node]
            parent[node] = root
            node = next_node
        return root

    def union(left, right):
        left_root, right_root = find(left), find(right)
        if left_root == right_root:
            return
        if rank[left_root] < rank[right_root]:
            left_root, right_root = right_root, left_root
        parent[right_root] = left_root
        if rank[left_root] == rank[right_root]:
            rank[left_root] += 1

    for row in rows:
        file_node = ('file', row['file_id'])
        find(file_node)
        for field in participant_fields:
            identity = row[field]
            if identity > 0:
                union(file_node, ('animal', identity))

    components = {}
    for row in rows:
        root = find(('file', row['file_id']))
        component = components.setdefault(root, {'files': set(), 'animals': set(), 'rows': 0})
        component['files'].add(row['file_id'])
        component['rows'] += 1
        for field in participant_fields:
            identity = row[field]
            if identity > 0:
                component['animals'].add(identity)

    sizes = [component['rows'] for component in components.values()]
    largest = max(components.values(), key=lambda component: component['rows'], default=None)
    return {
        'connected_groups': len(components),
        'largest_group_annotations': largest['rows'] if largest else 0,
        'largest_group_annotation_share': round(largest['rows'] / len(rows), 4) if largest and rows else 0,
        'largest_group_files': len(largest['files']) if largest else 0,
        'largest_group_known_animals': len(largest['animals']) if largest else 0,
        'groups_with_one_annotation': sum(size == 1 for size in sizes),
        'median_group_annotations': median(sizes) if sizes else 0,
        'smallest_group_annotations': min(sizes, default=0),
    }


def summarize_paper_subset(rows):
    """Reconstruct the paper's described sample filter; return aggregate counts only."""
    maximum_samples = PAPER_SAMPLE_RATE_HZ * PAPER_MAX_CALL_SECONDS
    selected = []
    excluded_context = excluded_emitter = excluded_duration = 0
    for row in rows:
        try:
            context_code = row['Context'].strip()
            emitter = int(row['Emitter'].strip())
            addressee = int(row['Addressee'].strip())
            start = int(row['Start sample'].strip())
            end = int(row['End sample'].strip())
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError('Paper subset reconstruction requires the reviewed integer annotation columns.') from error
        if context_code not in CONTEXT_CODES:
            raise ValueError('Paper subset reconstruction encountered an unmapped context code.')
        if start < 0 or end <= start:
            raise ValueError('Paper subset reconstruction encountered an invalid sample interval.')
        if context_code in ('0', '8'):
            excluded_context += 1
            continue
        if emitter <= 0:
            excluded_emitter += 1
            continue
        if end - start > maximum_samples:
            excluded_duration += 1
            continue
        selected.append({
            'file_id': row['FileID'].strip(),
            'emitter': emitter,
            'addressee': addressee,
            'context': CONTEXT_CODES[context_code],
        })

    file_counts = Counter(row['file_id'] for row in selected)
    context_counts = Counter(row['context'] for row in selected)
    emitters = {row['emitter'] for row in selected}
    addressees = {row['addressee'] for row in selected if row['addressee'] > 0}
    participants = emitters | addressees
    known_pairs = {
        tuple(sorted((row['emitter'], row['addressee'])))
        for row in selected if row['addressee'] > 0 and row['addressee'] != row['emitter']
    }
    addressee_status = Counter(
        'identified' if row['addressee'] > 0 else 'unknown' if row['addressee'] == 0 else 'ambiguous'
        for row in selected
    )
    multi_context_files = defaultdict(set)
    for row in selected:
        multi_context_files[row['file_id']].add(row['context'])

    return {
        'filter': {
            'excluded_context_codes': ['0 (Unknown)', '8 (Landing)'],
            'required_emitter_code': 'positive integer; zero is unknown and negative codes are ambiguous',
            'maximum_duration_samples_inclusive': maximum_samples,
            'sample_rate_hz': PAPER_SAMPLE_RATE_HZ,
            'maximum_duration_seconds': PAPER_MAX_CALL_SECONDS,
        },
        'source_rows': sum((excluded_context, excluded_emitter, excluded_duration, len(selected))),
        'excluded_for_context': excluded_context,
        'excluded_for_emitter_identity': excluded_emitter,
        'excluded_for_duration': excluded_duration,
        'retained_annotations': len(selected),
        'published_retained_annotations': PUBLISHED_PAPER_FILTERED_ROWS,
        'matches_published_count': len(selected) == PUBLISHED_PAPER_FILTERED_ROWS,
        'unique_file_ids': len(file_counts),
        'annotations_beyond_unique_files': len(selected) - len(file_counts),
        'files_with_multiple_annotations': sum(count > 1 for count in file_counts.values()),
        'files_with_multiple_contexts': sum(len(contexts) > 1 for contexts in multi_context_files.values()),
        'unique_positive_emitters': len(emitters),
        'unique_positive_addressees': len(addressees),
        'unique_positive_participants_across_roles': len(participants),
        'rows_by_context': dict(sorted(context_counts.items())),
        'addressee_status_rows': dict(sorted(addressee_status.items())),
        'unique_distinct_participant_pairs': len(known_pairs),
        'grouping_feasibility': {
            'source_file_only': _connected_group_summary(selected, ()),
            'source_file_plus_emitter': _connected_group_summary(selected, ('emitter',)),
            'source_file_plus_all_known_participants': _connected_group_summary(selected, ('emitter', 'addressee')),
        },
        'training_admitted': False,
        'limitations': [
            'A matching filtered row count is not a row-by-row comparison with the paper\'s unavailable retained-row manifest or fold files.',
            'The grouping summaries keep each source FileID and each positive participant identifier together; they are aggregate topology diagnostics, not validated splits.',
            'Unknown or ambiguous participant roles may hide additional grouping links; sessions, dates, channels, treatments and chambers require other source metadata.',
            'No audio, video, model code, model weights or model predictions were used.',
            'Context remains video-derived observer annotation, not listener-validated meaning or comprehension.',
        ],
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
    role_ids = {'emitter': set(), 'addressee': set()}
    participant_pairs = set()
    rows_with_two_identified_participants = 0

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
                if identity != 0:
                    role_ids[negative_counter].add(abs(identity))
            except ValueError:
                noninteger_identity_values += 1

        try:
            emitter_id = abs(int(row['Emitter'].strip()))
            addressee_id = abs(int(row['Addressee'].strip()))
        except ValueError:
            emitter_id = addressee_id = 0
        if emitter_id and addressee_id and emitter_id != addressee_id:
            rows_with_two_identified_participants += 1
            participant_pairs.add(tuple(sorted((emitter_id, addressee_id))))

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
    adjacency = {}
    for left, right in participant_pairs:
        adjacency.setdefault(left, set()).add(right)
        adjacency.setdefault(right, set()).add(left)
    component_sizes = []
    visited = set()
    for animal_id in adjacency:
        if animal_id in visited:
            continue
        stack = [animal_id]
        visited.add(animal_id)
        size = 0
        while stack:
            current = stack.pop()
            size += 1
            for neighbor in adjacency[current] - visited:
                visited.add(neighbor)
                stack.append(neighbor)
        component_sizes.append(size)
    all_known_ids = role_ids['emitter'] | role_ids['addressee']
    reference_matches = {
        'rows_match_paper_91080': rows == 91080,
        'context_counts_match_paper_table_4': contexts == PUBLISHED_CONTEXT_COUNTS,
        'combined_pre_action_counts_match_paper_table_4': pre_actions == PUBLISHED_PRE_ACTION_COUNTS,
        'combined_post_action_counts_match_paper_table_4': post_actions == PUBLISHED_POST_ACTION_COUNTS,
    }
    paper_subset = summarize_paper_subset(csv.DictReader(io.StringIO(data.decode('utf-8-sig'))))
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
        'participant_pair_structure': {
            'unique_known_ids_across_both_roles': len(all_known_ids),
            'unique_ids_in_emitter_field': len(role_ids['emitter']),
            'unique_ids_in_addressee_field': len(role_ids['addressee']),
            'rows_with_two_identified_participants': rows_with_two_identified_participants,
            'unique_interacting_pairs': len(participant_pairs),
            'connected_components_among_pair_linked_ids': len(component_sizes),
            'largest_pair_component_ids': max(component_sizes, default=0),
            'known_ids_without_a_pair_edge': len(all_known_ids - set(adjacency)),
        },
        'paper_subset_reconstruction': paper_subset,
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
            'The participant-pair graph uses absolute nonzero IDs from both role columns to retain known participants when role assignment is uncertain; it is an aggregate structure check, not a verified subject-independent split.',
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
