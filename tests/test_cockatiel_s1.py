import hashlib
import io
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from scripts.inspect_cockatiel_s1 import DATA_HEADERS, inspect_workbook


def _cell(reference, value):
    if value is None:
        return f'<c r="{reference}"/>'
    if isinstance(value, (int, float)):
        return f'<c r="{reference}" t="n"><v>{value}</v></c>'
    return f'<c r="{reference}" t="inlineStr"><is><t>{value}</t></is></c>'


def _column_name(index):
    name = ''
    while index:
        index, remainder = divmod(index - 1, 26)
        name = chr(65 + remainder) + name
    return name


def _sheet(rows):
    xml_rows = []
    for row_index, row in enumerate(rows, 1):
        cells = ''.join(_cell(_column_name(column) + str(row_index), value)
                        for column, value in enumerate(row, 1))
        xml_rows.append(f'<row r="{row_index}">{cells}</row>')
    max_column = _column_name(max(len(row) for row in rows))
    return ('<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            f'<dimension ref="A1:{max_column}{len(rows)}"/><sheetData>{"".join(xml_rows)}</sheetData>'
            '</worksheet>')


def _synthetic_xlsx():
    rows = [list(DATA_HEADERS)]
    natures = ('aff', 'nonaff', 'wn')
    for subject in range(1, 11):
        for day_number, condition in enumerate(natures, 1):
            day = f'j{day_number}'
            rows.append([f'subject{subject}', 'female', day, 'pre', condition,
                         None if condition == 'wn' else 'caller',
                         None if condition == 'wn' else 'female',
                         None if condition == 'wn' else 'homo', 'prestim', f'{day}_pre',
                         0, 15, 0, 10, 5, 0, 0, 10, 5, 0])
            for phase in ('audio', 'postim'):
                for stimulus in (1, 2, 3):
                    rows.append([f'subject{subject}', 'female', day, stimulus, condition,
                                 None if condition == 'wn' else 'caller',
                                 None if condition == 'wn' else 'female',
                                 None if condition == 'wn' else 'homo', phase,
                                 f'{day}_{stimulus}', 1, 15, 0, 10, 5, 0, 0, 10, 5, 0])
    legend = [['testbird', 'Identity of the tested bird']]
    legend.extend([[number, f'private label {number}'] for number in range(1, 20)])
    out = io.BytesIO()
    with ZipFile(out, 'w') as archive:
        archive.writestr('xl/workbook.xml', '''<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Data" sheetId="1" r:id="rId1"/><sheet name="Legend" sheetId="2" r:id="rId2"/></sheets></workbook>''')
        archive.writestr('xl/_rels/workbook.xml.rels', '''<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Target="worksheets/sheet1.xml"/><Relationship Id="rId2" Target="worksheets/sheet2.xml"/></Relationships>''')
        archive.writestr('xl/worksheets/sheet1.xml', _sheet(rows))
        archive.writestr('xl/worksheets/sheet2.xml', _sheet(legend))
    out.seek(0)
    return out.read()


class CockatielS1Tests(unittest.TestCase):
    def test_structural_audit_is_aggregate_only_and_counts_repeated_windows(self):
        data = _synthetic_xlsx()
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'fixture.xlsx'
            path.write_bytes(data)
            report = inspect_workbook(
                path, hashlib.sha256(data).hexdigest(), len(data),
                hashlib.md5(data, usedforsecurity=False).hexdigest())
        structure = report['structural_review']
        self.assertEqual(structure['behavioral_windows'], 210)
        self.assertEqual(structure['tested_animals'], 10)
        self.assertEqual(structure['windows_per_animal'], {'minimum': 21, 'maximum': 21})
        self.assertEqual(structure['unique_window_keys'], 210)
        self.assertEqual(structure['phase_rows'], {'audio': 90, 'postim': 90, 'prestim': 30})
        self.assertEqual(structure['social_condition_rows'], {'aff': 70, 'nonaff': 70, 'wn': 70})
        self.assertFalse(report['interpretation']['training_admitted'])
        self.assertFalse(report['interpretation']['research_admission'])
        serialized = str(report)
        self.assertNotIn('subject1', serialized)
        self.assertNotIn('private label', serialized)

    def test_pinned_checksum_and_unreviewed_workbook_shapes_are_rejected(self):
        data = _synthetic_xlsx()
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'fixture.xlsx'
            path.write_bytes(data)
            with self.assertRaisesRegex(ValueError, 'size or SHA-256'):
                inspect_workbook(path)
            with self.assertRaisesRegex(ValueError, 'not a valid XLSX'):
                path.write_bytes(b'not an xlsx')
                inspect_workbook(
                    path, hashlib.sha256(path.read_bytes()).hexdigest(), path.stat().st_size,
                    hashlib.md5(path.read_bytes(), usedforsecurity=False).hexdigest())


if __name__ == '__main__':
    unittest.main()
