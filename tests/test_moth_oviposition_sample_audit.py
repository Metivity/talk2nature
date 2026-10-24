import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from research.inspect_moth_oviposition_sample import AuditError, read_rows, summarize, summarize_rows

REPO_ROOT = Path(__file__).resolve().parents[1]
PINNED_SAMPLE = REPO_ROOT / "data" / "external" / "moth-plant-oviposition-data" / "data.xlsx"
AGGREGATE_REPORT = REPO_ROOT / "research" / "moth_plant_oviposition_sample_report.json"


def _synthetic_xlsx(path: Path, unbalanced: bool = False) -> None:
    shared = [
        "Experiment", "Season", "Observation date", "Arena", "Repetition",
        "Side examined", "Clusters of eggs", "Synthetic condition", "S1", "date1", "A1", "R1", "Cue", "Quiet",
    ]
    headers = list(range(7))
    rows = [
        [7, 8, 9, 10, 11, 12, 2],
        [7, 8, 9, 10, 11, 13, 3],
        [7, 8, 9, 10, 11, 12, 1],
        [7, 8, 9, 10, 11, 13, 0],
    ]
    if unbalanced:
        rows.pop()
    def col(index: int) -> str:
        return chr(ord("A") + index)
    sheet_rows = []
    for row_number, values in enumerate([headers] + rows, 1):
        cells = []
        for index, value in enumerate(values):
            cell_type = "s" if row_number == 1 or index < 6 else None
            type_attr = f' t="{cell_type}"' if cell_type else ""
            cells.append(f'<c r="{col(index)}{row_number}"{type_attr}><v>{value}</v></c>')
        sheet_rows.append(f'<row r="{row_number}">{"".join(cells)}</row>')
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "xl/workbook.xml",
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            '<sheets><sheet name="Data" sheetId="1" r:id="rId1"/></sheets></workbook>',
        )
        archive.writestr(
            "xl/_rels/workbook.xml.rels",
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="worksheet" Target="worksheets/sheet1.xml"/>'
            '</Relationships>',
        )
        archive.writestr(
            "xl/sharedStrings.xml",
            '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            + "".join(f"<si><t>{value}</t></si>" for value in shared)
            + "</sst>",
        )
        archive.writestr(
            "xl/worksheets/sheet1.xml",
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            f'<sheetData>{"".join(sheet_rows)}</sheetData></worksheet>',
        )


class MothOvipositionSampleAuditTests(unittest.TestCase):
    def test_parser_reads_a_synthetic_xlsx_without_emitting_source_rows(self):
        with tempfile.TemporaryDirectory() as temporary:
            workbook = Path(temporary) / "synthetic.xlsx"
            _synthetic_xlsx(workbook)
            rows = read_rows(workbook)
        self.assertEqual(len(rows), 4)
        self.assertEqual(rows[0]["Experiment"], "Synthetic condition")
        report = summarize_rows(rows, "a" * 64)
        result = report["aggregate_results"][0]
        self.assertEqual(result["repetitions"], 1)
        self.assertEqual(result["paired_observations"], 2)
        self.assertEqual(result["egg_clusters"], 6)
        self.assertNotIn("rows", result)
        self.assertIsNone(result["matches_reported_table1_counts"])
        self.assertIsNone(report["input"]["source_checksum_match"])

    def test_rejects_unbalanced_side_records(self):
        with tempfile.TemporaryDirectory() as temporary:
            workbook = Path(temporary) / "synthetic.xlsx"
            _synthetic_xlsx(workbook, unbalanced=True)
            rows = read_rows(workbook)
        with self.assertRaisesRegex(AuditError, "balanced rows"):
            summarize_rows(rows, "a" * 64)

    @unittest.skipUnless(PINNED_SAMPLE.is_file(), "third-party sample is intentionally not bundled in CI")
    def test_real_pinned_sample_matches_all_five_table1_aggregate_tuples(self):
        report = summarize()
        self.assertTrue(report["method"]["table1_conditions_match"])
        self.assertEqual(report["method"]["table1_conditions_checked"], 5)
        self.assertEqual(report["input"]["sha256"], "c322198e05f3093fdd929e750db5f00a0b702402c3d4e8a86f666b0eb5a651b6")
        self.assertTrue(all(item["matches_reported_table1_counts"] for item in report["aggregate_results"] if item["table1_reported"]))
        bat = next(item for item in report["aggregate_results"] if item["workbook_condition"] == "Bat")
        self.assertIsNone(bat["matches_reported_table1_counts"])
        self.assertIn("not mapped", bat["mapping_review"])

    def test_published_aggregate_report_is_checksum_pinned_and_row_free(self):
        report = json.loads(AGGREGATE_REPORT.read_text(encoding="utf-8"))
        self.assertEqual(report["input"]["sha256"], "c322198e05f3093fdd929e750db5f00a0b702402c3d4e8a86f666b0eb5a651b6")
        self.assertTrue(report["input"]["source_checksum_match"])
        self.assertTrue(report["method"]["table1_conditions_match"])
        self.assertEqual(report["method"]["table1_conditions_checked"], 5)
        checked = [item for item in report["aggregate_results"] if item["table1_reported"] is not None]
        self.assertEqual(len(checked), 5)
        self.assertTrue(all(item["matches_reported_table1_counts"] for item in checked))
        self.assertTrue(all("rows" not in item for item in report["aggregate_results"]))
        bat = next(item for item in report["aggregate_results"] if item["workbook_condition"] == "Bat")
        self.assertIsNone(bat["matches_reported_table1_counts"])
        self.assertIn("not mapped", bat["mapping_review"])

    def test_reported_checksum_is_checked_before_xlsx_parsing(self):
        with tempfile.TemporaryDirectory() as temporary:
            workbook = Path(temporary) / "wrong.xlsx"
            workbook.write_bytes(b"not the pinned workbook")
            with self.assertRaisesRegex(AuditError, "size does not match"):
                summarize(workbook)


if __name__ == "__main__":
    unittest.main()
