"""Audit the monk-parakeet 2020 annotation-to-selection-table join.

This mirrors the pinned authors' loader at the structural level: keep Raven
rows whose View is "Waveform 1", then left-join Annotation to annotation_ref.
Only aggregate counts are emitted; identifiers, notes, locations and filenames
are never included in the report. This does not validate the corresponding audio.
"""
import argparse
import csv
import hashlib
import io
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _verified_receipt(folder):
    folder = Path(folder)
    receipt = json.loads((folder / 'receipt.json').read_text())
    if receipt.get('schema_version') != 1 or receipt.get('training_admitted') is not False:
        raise ValueError('Expected a non-admitted version-1 source receipt.')
    files = {}
    for artifact in receipt.get('files', []):
        name = artifact.get('name')
        if not isinstance(name, str) or Path(name).name != name or name in files:
            raise ValueError('Unsafe or duplicate receipt filename.')
        path = folder / name
        if path.is_symlink() or not path.is_file():
            raise ValueError('Receipt source file is missing or linked.')
        data = path.read_bytes()
        if (len(data) != artifact.get('bytes')
                or hashlib.sha256(data).hexdigest() != artifact.get('sha256')):
            raise ValueError('Source file differs from its acquisition receipt.')
        files[name] = data
    if not files:
        raise ValueError('Receipt has no source files.')
    return receipt, files


def audit(annotation_folder, selection_folder, loader_folder=None):
    if loader_folder is None:
        loader_folder = ROOT / 'data/external/monk-parakeet-loader-code'
    annotation_receipt, annotation_files = _verified_receipt(annotation_folder)
    selection_receipt, selection_files = _verified_receipt(selection_folder)
    loader_receipt, loader_files = _verified_receipt(loader_folder)
    if annotation_receipt.get('resource_id') != 'monk-parakeet-annotations':
        raise ValueError('Unexpected annotation source resource.')
    if selection_receipt.get('resource_id') != 'monk-parakeet-selection-tables-2020':
        raise ValueError('Unexpected selection-table source resource.')
    if loader_receipt.get('resource_id') != 'monk-parakeet-loader-code':
        raise ValueError('Unexpected loader source resource.')
    source_versions = [receipt.get('resource', {}).get('version') for receipt in
                       (annotation_receipt, selection_receipt, loader_receipt)]
    if not all(isinstance(version, str) and version for version in source_versions):
        raise ValueError('A pinned source version is missing from a receipt.')
    if len(set(source_versions)) != 1:
        raise ValueError('The annotation, selection tables and loader do not share one snapshot.')
    annotation_name = 'annotations-2020.csv'
    if annotation_name not in annotation_files:
        raise ValueError('Reviewed 2020 annotation CSV is missing.')
    loader_name = 'load.selection.tables.R'
    if loader_name not in loader_files:
        raise ValueError('Pinned loader source is missing.')
    reader = csv.DictReader(io.StringIO(annotation_files[annotation_name].decode('utf-8-sig')),
                            delimiter=';')
    if not reader.fieldnames or 'annotation_ref' not in reader.fieldnames:
        raise ValueError('Annotation reference column is missing.')
    refs = []
    for row in reader:
        if None in row or any(value is None for value in row.values()):
            raise ValueError('Malformed annotation CSV row.')
        refs.append((row.get('annotation_ref') or '').strip())
    if not refs or any(not ref.isdigit() for ref in refs):
        raise ValueError('Annotation reference format changed; inspect before joining.')
    ref_counts = Counter(refs)
    if any(count != 1 for count in ref_counts.values()):
        raise ValueError('Annotation reference is not unique in the CSV.')
    ref_set = set(refs)

    table_names = sorted(name for name in selection_files
                         if name.startswith('2020_') and name.endswith('.txt'))
    if not table_names:
        raise ValueError('No pinned 2020 Raven tables were found.')
    table_manifest = [
        {'name': name, 'bytes': len(selection_files[name]),
         'sha256': hashlib.sha256(selection_files[name]).hexdigest()}
        for name in table_names
    ]
    table_refs = defaultdict(set)
    row_counts = Counter()
    total_rows = waveform_rows = empty_annotations = nonnumeric_annotations = 0
    files_with_waveform_rows = 0
    for name in table_names:
        data = selection_files[name]
        table_reader = csv.DictReader(io.StringIO(data.decode('utf-8-sig')), delimiter='\t')
        fields = {field.strip().lstrip('\ufeff'): field for field in (table_reader.fieldnames or [])}
        if 'View' not in fields or 'Annotation' not in fields:
            raise ValueError('Raven table schema changed; inspect before joining.')
        file_rows = 0
        for row in table_reader:
            if None in row:
                raise ValueError('Malformed Raven selection-table row.')
            total_rows += 1
            if (row.get(fields['View']) or '').strip() != 'Waveform 1':
                continue
            waveform_rows += 1
            file_rows += 1
            ref = (row.get(fields['Annotation']) or '').strip()
            if not ref:
                empty_annotations += 1
            elif not ref.isdigit():
                nonnumeric_annotations += 1
            else:
                table_refs[ref].add(name)
                row_counts[ref] += 1
        files_with_waveform_rows += file_rows > 0
    if empty_annotations or nonnumeric_annotations:
        raise ValueError('Waveform annotations are not numeric; inspect before exact-key joining.')

    table_ref_set = set(table_refs)
    matched_refs = ref_set & table_ref_set
    matched_rows = sum(row_counts[ref] for ref in matched_refs)
    return {
        'schema_version': 2,
        'annotation_resource_id': annotation_receipt['resource_id'],
        'annotation_version': annotation_receipt['resource']['version'],
        'selection_resource_id': selection_receipt['resource_id'],
        'selection_version': selection_receipt['resource']['version'],
        'loader_code_resource_id': loader_receipt['resource_id'],
        'loader_code_version': loader_receipt['resource']['version'],
        'loader_code_sha256': hashlib.sha256(loader_files[loader_name]).hexdigest(),
        'analysis_script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'annotation_csv_sha256': hashlib.sha256(annotation_files[annotation_name]).hexdigest(),
        'selection_table_manifest_sha256': hashlib.sha256(
            json.dumps(table_manifest, sort_keys=True, separators=(',', ':')).encode('utf-8')
        ).hexdigest(),
        'annotation_csv_rows': len(refs),
        'unique_annotation_refs': len(ref_set),
        'selection_table_files': len(table_names),
        'selection_table_bytes': sum(artifact['bytes']
                                     for artifact in selection_receipt['resource']['files']
                                     if artifact['name'] in table_names),
        'selection_rows_all_views': total_rows,
        'selection_rows_waveform_1': waveform_rows,
        'tables_with_waveform_1_rows': files_with_waveform_rows,
        'unique_waveform_annotation_keys': len(table_ref_set),
        'annotation_refs_present': len(matched_refs),
        'annotation_refs_unmatched_by_selection_tables': len(ref_set - table_ref_set),
        'annotation_refs_found_in_multiple_files': sum(len(table_refs[ref]) > 1 for ref in matched_refs),
        'annotation_refs_expanding_to_multiple_waveform_rows': sum(row_counts[ref] > 1 for ref in matched_refs),
        'waveform_rows_with_annotation_csv_match': matched_rows,
        'waveform_rows_without_annotation_csv_match': waveform_rows - matched_rows,
        'training_admitted': False,
        'interpretation': (
            'Structural join only. Mirrors the authors\' Waveform 1 filter and '
            'Annotation-to-annotation_ref left join. The report omits raw keys, '
            'filenames, locations and free-text notes; repeated rows and cross-file '
            'keys require review against audio and study context. Input hashes fingerprint '
            'the reviewed CSV and selection-table manifest without publishing filenames.'),
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--annotations', type=Path,
                        default=ROOT / 'data/external/monk-parakeet-annotations')
    parser.add_argument('--selection-tables', type=Path,
                        default=ROOT / 'data/external/monk-parakeet-selection-tables-2020')
    parser.add_argument('--loader-code', type=Path,
                        default=ROOT / 'data/external/monk-parakeet-loader-code')
    parser.add_argument('--output', type=Path, default=ROOT / 'research/monk_parakeet_join_audit.json')
    args = parser.parse_args()
    report = json.dumps(audit(args.annotations, args.selection_tables, args.loader_code), indent=2) + '\n'
    args.output.write_text(report)
    print(json.dumps({'report': str(args.output), 'source_only': True,
                      'training_admitted': False}))
