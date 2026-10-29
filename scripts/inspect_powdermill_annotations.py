"""Summarize Powdermill annotations without exporting row-level labels.

The report is a structural suitability check, not a model result, quiet-window
ground truth, or scientific admission. Audio is never opened by this script.
"""
import argparse
import csv
import hashlib
import io
import json
import re
import zipfile
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FOLDER = ROOT / 'data/external/powdermill-bird-soundscapes'
DEFAULT_OUTPUT = ROOT / 'research/powdermill_annotation_report.json'
EXPECTED_FIELDS = (
    'Selection', 'View', 'Channel', 'Begin Time (s)', 'End Time (s)',
    'Low Freq (Hz)', 'High Freq (Hz)', 'Species',
)
MEMBER_RE = re.compile(
    r'^Recording_(\d+)/Recording_\1_Segment_(\d+)\.Table\.1\.selections\.txt$'
)
MAX_UNCOMPRESSED_BYTES = 10 * 1024 * 1024


def inspect(folder=DEFAULT_FOLDER):
    folder = Path(folder)
    receipt_path = folder / 'receipt.json'
    receipt = json.loads(receipt_path.read_text())
    if (receipt.get('resource_id') != 'powdermill-bird-soundscapes'
            or receipt.get('training_admitted') is not False):
        raise ValueError('Expected the non-training Powdermill annotation receipt.')
    artifact = next((item for item in receipt.get('files', [])
                     if item.get('name') == 'annotation_Files.zip'), None)
    if not isinstance(artifact, dict):
        raise ValueError('Annotation archive is missing from the acquisition receipt.')
    data = (folder / artifact['name']).read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != artifact.get('sha256'):
        raise ValueError('Annotation archive differs from its acquisition receipt.')

    totals = Counter()
    by_recording = defaultdict(Counter)
    segment_ids_by_recording = defaultdict(set)
    species_support = defaultdict(set)
    all_species = set()
    try:
        archive = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile as exc:
        raise ValueError('Annotation archive is not a valid ZIP.') from exc
    with archive:
        infos = archive.infolist()
        if sum(item.file_size for item in infos) > MAX_UNCOMPRESSED_BYTES:
            raise ValueError('Annotation archive exceeds the inspection size limit.')
        bad_member = archive.testzip()
        if bad_member:
            raise ValueError('Annotation archive contains a corrupt member.')
        files = [item for item in infos if not item.is_dir()]
        if not files or any(item.file_size > 256_000 for item in files):
            raise ValueError('Annotation archive member inventory is outside the reviewed bounds.')
        for info in files:
            path = PurePosixPath(info.filename)
            match = MEMBER_RE.fullmatch(info.filename)
            if (path.is_absolute() or '..' in path.parts or not match
                    or path.suffix.lower() in {'.wav', '.mp3', '.flac', '.m4a'}):
                raise ValueError('Unexpected path or non-annotation content in archive.')
            recording, segment = match.groups()
            with archive.open(info) as member:
                text = member.read(256_001).decode('utf-8-sig')
            if len(text.encode('utf-8')) > 256_000:
                raise ValueError('Annotation member exceeds the text inspection limit.')
            reader = csv.DictReader(io.StringIO(text), delimiter='\t')
            if tuple(reader.fieldnames or ()) != EXPECTED_FIELDS:
                raise ValueError('Annotation table columns differ from the reviewed schema.')
            rows = 0
            for row in reader:
                if None in row or any(value is None for value in row.values()):
                    raise ValueError('Malformed annotation row.')
                if not any(value.strip() for value in row.values()):
                    continue
                rows += 1
                totals['annotations'] += 1
                label = row['Species'].strip()
                if not label or label == '????':
                    totals['unknown_or_blank_labels'] += 1
                else:
                    all_species.add(label)
                    species_support[label].add(recording)
                try:
                    start = float(row['Begin Time (s)'])
                    end = float(row['End Time (s)'])
                    low = float(row['Low Freq (Hz)'])
                    high = float(row['High Freq (Hz)'])
                    valid = 0 <= start < end <= 300 and 0 <= low <= high
                except (TypeError, ValueError):
                    valid = False
                if not valid:
                    totals['invalid_time_or_frequency_intervals'] += 1
            totals['segments'] += 1
            totals['empty_annotation_segments'] += int(rows == 0)
            group = by_recording[recording]
            group['segments'] += 1
            group['annotations'] += rows
            group['empty_annotation_segments'] += int(rows == 0)
            segment_ids_by_recording[recording].add(int(segment))

    groups = {
        f'Recording_{recording}': {
            'segments': values['segments'],
            'annotations': values['annotations'],
            'empty_annotation_segments': values['empty_annotation_segments'],
            'distinct_segment_numbers': len(segment_ids_by_recording[recording]),
        }
        for recording, values in sorted(by_recording.items(), key=lambda pair: int(pair[0]))
    }
    support_histogram = Counter(len(groups) for groups in species_support.values())
    return {
        'resource_id': receipt['resource_id'],
        'source_sha256': digest,
        'source_url': artifact['url'],
        'source_version': receipt['resource']['version'],
        'archive_members': totals['segments'],
        'table_columns': list(EXPECTED_FIELDS),
        'recording_group_count': len(by_recording),
        'recording_groups': groups,
        'annotation_count': totals['annotations'],
        'unique_identified_species_codes': len(all_species),
        'species_group_support_histogram': {
            str(count): support_histogram[count]
            for count in sorted(support_histogram)
        },
        'unknown_or_blank_labels': totals['unknown_or_blank_labels'],
        'invalid_time_or_frequency_intervals': totals['invalid_time_or_frequency_intervals'],
        'empty_annotation_segments': totals['empty_annotation_segments'],
        'audio_members_present': False,
        'audio_opened': False,
        'training_admitted': False,
        'grouping_assessment': (
            'Recording_N is a usable four-group recording/date key per the source README; '
            'site grouping is not established by the annotation archive. Four groups are '
            'too few for a robust generalization claim.'
        ),
        'limitations': [
            'An empty annotation table is not verified quiet audio: faint, unidentifiable and short-chip sounds were not fully labeled.',
            'The source README describes four continuous recordings on four dates; it does not map these IDs to independent sites.',
            'A recording-held-out result over four groups would be a narrow feasibility check, not broad ecological generalization.',
            'No audio, location coordinates, raw annotation rows, model weights or predictions are included in this report.',
        ],
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--folder', type=Path, default=DEFAULT_FOLDER)
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = json.dumps(inspect(args.folder), indent=2) + '\n'
    args.output.write_text(result)
    print(json.dumps({'report': str(args.output), 'summary': json.loads(result)}, indent=2))
