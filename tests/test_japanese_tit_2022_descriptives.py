import csv
import hashlib
import tempfile
import unittest
from pathlib import Path

from research.japanese_tit_2022_descriptives import AuditError, FIELDS, TREATMENTS, summarize


class JapaneseTitDescriptiveAuditTests(unittest.TestCase):
    def _write_fixture(self, directory: Path, mismatch: bool = False) -> None:
        binary_rows = []
        proportion_rows = []
        for treatment_index, treatment in enumerate(TREATMENTS):
            for trial in range(16):
                flock_size = 3
                approach = int(trial < treatment_index + 1)
                wing = int(trial < 2 * (treatment_index + 1))
                metadata = {
                    "date": f"2022/01/{trial + 1:02d}",
                    "caller_ID": str(trial + 1),
                    "trt": treatment,
                    "flock_size": str(flock_size),
                    "shrike": "A" if trial % 2 == 0 else "B",
                    "call_source": "solo" if trial % 2 == 0 else "mix",
                }
                binary_rows.append({**metadata, "2m": str(approach), "wing": str(wing)})
                proportion_rows.append(
                    {
                        **metadata,
                        "2m": str(approach if not mismatch or trial else 0),
                        "wing": str(int(wing > 0)),
                    }
                )
        for filename, rows in (
            ("merge_binary.txt", binary_rows),
            ("merge_proportion.txt", proportion_rows),
        ):
            with (directory / filename).open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
                writer.writeheader()
                writer.writerows(rows)

    def _manifest(self, directory: Path):
        result = {}
        for filename in ("merge_binary.txt", "merge_proportion.txt"):
            payload = (directory / filename).read_bytes()
            result[filename] = {
                "bytes": len(payload),
                "md5": hashlib.md5(payload, usedforsecurity=False).hexdigest(),
            }
        return result

    def test_emits_aggregate_only_summaries_for_all_four_treatments(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            self._write_fixture(directory)
            result = summarize(directory, self._manifest(directory))

        self.assertEqual(result["input_validation"]["treatment_counts"], {t: 16 for t in TREATMENTS})
        self.assertEqual(len(result["aggregate_results"]), 4)
        self.assertIn("one speaker", result["treatment_key"][TREATMENTS[0]])
        first = result["aggregate_results"][0]
        self.assertEqual(first["treatment"], TREATMENTS[0])
        self.assertEqual(first["approach_within_2m"]["flocks_with_event"], 1)
        self.assertEqual(first["approach_within_2m"]["individuals_with_event"], 1)
        self.assertNotIn("rows", result)

    def test_rejects_mismatched_binary_and_count_outcomes(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            self._write_fixture(directory, mismatch=True)
            with self.assertRaises(AuditError):
                summarize(directory, self._manifest(directory))

    def test_rejects_provider_checksum_mismatch(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            self._write_fixture(directory)
            manifest = self._manifest(directory)
            manifest["merge_binary.txt"]["md5"] = "0" * 32
            with self.assertRaises(AuditError):
                summarize(directory, manifest)

    def test_reports_missing_source_files_as_an_audit_error(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(AuditError, "cannot read"):
                summarize(Path(temporary))


if __name__ == "__main__":
    unittest.main()
