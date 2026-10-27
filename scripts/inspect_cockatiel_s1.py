#!/usr/bin/env python3
"""Aggregate-only structural audit of the pinned PLOS cockatiel S1 workbook."""

from __future__ import annotations

import argparse
import hashlib
import json
import posixpath
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / 'data/external/cockatiel-distress-call-study-data-2018/pone.0205314.s001.xlsx'
DEFAULT_OUTPUT = ROOT / 'research/cockatiel_s1_report.json'
EXPECTED_BYTES = 34661
EXPECTED_SHA256 = '68063b3d8eead819ff776a02f70ded22f66b7de3439e3b2e2bc1efadf6a58f09'
PROVIDER_MD5 = '10f1a76b6fabb6542982817d8d19371b'
DATA_HEADERS = (
    'testbird', 'sextest', 'day', 'stim', 'nature', 'identitycaller', 'sexcaller',
    'typedyad', 'cond', 'Periode', 'activity', 'z1', 'z1_bin', 'z2', 'z3',
    'c1', 'c1_bin', 'c2', 'c3', 'contcall',
)
MAIN_NS = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
REL_NS = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PKG_REL_NS = 'http://schemas.openxmlformats.org/package/2006/relationships'


def _column_index(reference: str) -> int:
    letters = ''.join(character for character in reference if character.isalpha())
    if not letters:
        raise ValueError('Workbook cell has no column reference.')
    value = 0
    for character in letters.upper():
        value = value * 26 + ord(character) - ord('A') + 1
    return value - 1


def _label(value) -> str:
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def _read_sheet(archive: zipfile.ZipFile, member: str, shared: list[str]):
    root = ET.fromstring(archive.read(member))
    if root.findall(f'.//{{{MAIN_NS}}}f'):
        raise ValueError('Formula cells are outside this structural audit.')
    dimension = root.find(f'{{{MAIN_NS}}}dimension')
    rows = []
    for row in root.findall(f'{{{MAIN_NS}}}sheetData/{{{MAIN_NS}}}row'):
        values = []
        for cell in row.findall(f'{{{MAIN_NS}}}c'):
            index = _column_index(cell.attrib.get('r', ''))
            while len(values) <= index:
                values.append(None)
            kind = cell.attrib.get('t')
            value = cell.find(f'{{{MAIN_NS}}}v')
            if kind == 's' and value is not None:
                parsed = shared[int(value.text)]
            elif kind == 'inlineStr':
                parsed = ''.join(text.text or '' for text in cell.findall(f'.//{{{MAIN_NS}}}t'))
            elif value is None or value.text is None:
                parsed = None
            elif kind == 'b':
                parsed = value.text == '1'
            else:
                try:
                    parsed = float(value.text)
                except ValueError:
                    parsed = value.text
            values[index] = parsed
        rows.append(values)
    return (dimension.attrib.get('ref') if dimension is not None else None), rows


def _workbook_sheets(archive: zipfile.ZipFile):
    names = set(archive.namelist())
    workbook = ET.fromstring(archive.read('xl/workbook.xml'))
    relationships = ET.fromstring(archive.read('xl/_rels/workbook.xml.rels'))
    targets = {}
    for relation in relationships.findall(f'{{{PKG_REL_NS}}}Relationship'):
        if relation.attrib.get('TargetMode') == 'External':
            raise ValueError('External workbook relationships are outside this audit.')
        targets[relation.attrib['Id']] = relation.attrib['Target']
    sheets = {}
    for sheet in workbook.findall(f'{{{MAIN_NS}}}sheets/{{{MAIN_NS}}}sheet'):
        target = targets.get(sheet.attrib.get(f'{{{REL_NS}}}id'))
        if not target:
            raise ValueError('Workbook sheet relationship is missing.')
        member = target.lstrip('/') if target.startswith('/') else posixpath.normpath(posixpath.join('xl', target))
        if member not in names or member.startswith('../'):
            raise ValueError('Workbook sheet target is outside the XLSX package.')
        sheets[sheet.attrib['name']] = member
    if set(sheets) != {'Data', 'Legend'}:
        raise ValueError('Unexpected sheet set; review the pinned workbook before parsing.')
    return sheets


def inspect_workbook(path: Path, expected_sha256: str = EXPECTED_SHA256,
                     expected_bytes: int = EXPECTED_BYTES,
                     expected_md5: str = PROVIDER_MD5) -> dict:
    raw = Path(path).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if len(raw) != expected_bytes or digest != expected_sha256:
        raise ValueError('Workbook size or SHA-256 does not match the reviewed file.')
    if hashlib.md5(raw, usedforsecurity=False).hexdigest() != expected_md5:
        raise ValueError('Workbook MD5 does not match the official Figshare manifest.')
    try:
        archive = zipfile.ZipFile(Path(path))
    except zipfile.BadZipFile as error:
        raise ValueError('Workbook is not a valid XLSX ZIP package.') from error
    with archive:
        if archive.testzip() is not None:
            raise ValueError('Workbook ZIP integrity check failed.')
        members = archive.namelist()
        if any(name.endswith('vbaProject.bin') for name in members):
            raise ValueError('Macro-enabled content is outside this structural audit.')
        if any(name.startswith('xl/externalLinks/') for name in members):
            raise ValueError('External workbook links are outside this structural audit.')
        shared = []
        if 'xl/sharedStrings.xml' in members:
            strings = ET.fromstring(archive.read('xl/sharedStrings.xml'))
            shared = [
                ''.join(text.text or '' for text in item.findall(f'.//{{{MAIN_NS}}}t'))
                for item in strings.findall(f'{{{MAIN_NS}}}si')
            ]
        sheets = _workbook_sheets(archive)
        data_dimension, data_rows = _read_sheet(archive, sheets['Data'], shared)
        legend_dimension, legend_rows = _read_sheet(archive, sheets['Legend'], shared)

    if not data_rows or tuple(_label(value) for value in data_rows[0]) != DATA_HEADERS:
        raise ValueError('Unexpected or incomplete Data sheet header.')
    records = [
        dict(zip(DATA_HEADERS, row + [None] * (len(DATA_HEADERS) - len(row))))
        for row in data_rows[1:]
    ]
    if len(records) != 210 or len(legend_rows) != 20:
        raise ValueError('Workbook row counts changed from the reviewed structure.')
    if any(len(row) > len(DATA_HEADERS) for row in data_rows):
        raise ValueError('Data sheet contains unreviewed columns.')

    subjects = {record['testbird'] for record in records}
    subject_rows = Counter(record['testbird'] for record in records)
    conditions = Counter(_label(record['cond']) for record in records)
    nature = Counter(_label(record['nature']) for record in records)
    stimuli = Counter(_label(record['stim']) for record in records)
    missing = {
        header: sum(record.get(header) in (None, '') for record in records)
        for header in DATA_HEADERS
    }
    key_fields = ('testbird', 'day', 'cond', 'stim', 'nature')
    keys = [tuple(_label(record[field]) for field in key_fields) for record in records]
    if None in subjects or len(subjects) != 10 or len(set(keys)) != len(records):
        raise ValueError('Expected ten subjects and unique repeated-window keys.')
    if sorted(conditions.items()) != [('audio', 90), ('postim', 90), ('prestim', 30)]:
        raise ValueError('Unexpected playback-phase row counts.')
    if sorted(nature.items()) != [('aff', 70), ('nonaff', 70), ('wn', 70)]:
        raise ValueError('Unexpected condition row counts.')
    if sorted(stimuli.items()) != [('1', 60), ('2', 60), ('3', 60), ('pre', 30)]:
        raise ValueError('Unexpected stimulus-window counts.')

    return {
        'schema_version': 1,
        'study_doi': '10.1371/journal.pone.0205314',
        'supporting_data_doi': '10.1371/journal.pone.0205314.s001',
        'file': {
            'name': Path(path).name,
            'bytes': len(raw),
            'sha256': digest,
            'provider_md5': PROVIDER_MD5,
            'provider_checksum_verified': True,
        },
        'workbook': {
            'zip_integrity': 'valid',
            'macros_present': False,
            'external_links_present': False,
            'data_sheet_dimension': data_dimension,
            'legend_sheet_dimension': legend_dimension,
            'data_columns': list(DATA_HEADERS),
        },
        'structural_review': {
            'behavioral_windows': len(records),
            'tested_animals': len(subjects),
            'windows_per_animal': {
                'minimum': min(subject_rows.values()),
                'maximum': max(subject_rows.values()),
            },
            'unique_window_keys': len(set(keys)),
            'phase_rows': dict(sorted(conditions.items())),
            'social_condition_rows': dict(sorted(nature.items())),
            'stimulus_window_rows': dict(sorted(stimuli.items())),
            'missing_cells_by_column': missing,
        },
        'interpretation': {
            'scope': 'Structural and aggregate-only workbook audit; no raw rows or animal identifiers are emitted.',
            'unit_warning': 'The 210 rows are repeated windows nested within ten tested birds and study days; they are not 210 independent animals.',
            'data_type': 'Video-coded behavioral outcomes and study condition metadata; no acoustic waveform is present.',
            'model_reproduction': 'Not attempted. Published mixed-model estimates and inferential results were not reproduced.',
            'training_admitted': False,
            'research_admission': False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=DEFAULT_INPUT)
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    report = inspect_workbook(args.input)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({
        'report': str(args.output),
        'rows': report['structural_review']['behavioral_windows'],
        'animals': report['structural_review']['tested_animals'],
        'training_admitted': False,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
