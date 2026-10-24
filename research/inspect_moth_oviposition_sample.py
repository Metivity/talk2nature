#!/usr/bin/env python3
"""Audit aggregate counts in the pinned moth oviposition workbook.

The script reads cached cell values only. It does not evaluate spreadsheet
formulas, execute deposited code, emit source rows, fit a model, or admit data
to training. The original workbook stays in ignored external storage.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import posixpath
import re
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


RESOURCE_ID = "moth-plant-oviposition-data"
SOURCE_DOI = "10.17632/yg7ms8rn37.1"
SOURCE_URL = "https://data.mendeley.com/datasets/yg7ms8rn37/1"
ATTRIBUTION = "Zer, G. (2025). Female Moths Incorporate Plant Acoustic Emissions into Their Oviposition Decision-Making Process. Mendeley Data v1."
LICENSE = "CC0 1.0 (scope: the version-pinned Mendeley Data deposit; retained locally for this bounded review)"
REQUIRED_FIELDS = (
    "Experiment",
    "Season",
    "Observation date",
    "Arena",
    "Repetition",
    "Side examined",
    "Clusters of eggs",
)
TABLE1_EXPECTED = {
    "Wet-dry plant": {"repetitions": 17, "paired_observations": 17, "egg_clusters": 53},
    "Drought sounds_60 per minute": {"repetitions": 38, "paired_observations": 45, "egg_clusters": 67},
    "Deaf females drought sounds_60 per minute": {
        "repetitions": 23,
        "paired_observations": 23,
        "egg_clusters": 39,
    },
    "Plants_60 per minute": {"repetitions": 29, "paired_observations": 39, "egg_clusters": 110},
    "Males": {"repetitions": 19, "paired_observations": 29, "egg_clusters": 48},
}
NS = {
    "main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "office_rel": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "package_rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}


class AuditError(ValueError):
    """The pinned workbook or its aggregate structure did not validate."""


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _pinned_manifest() -> dict[str, Any]:
    catalog_path = _repo_root() / "research" / "resources.json"
    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        resource = next(item for item in catalog["resources"] if item.get("id") == RESOURCE_ID)
    except (OSError, json.JSONDecodeError, KeyError, StopIteration, TypeError) as exc:
        raise AuditError("the catalog is missing the pinned Mendeley v1 resource") from exc
    if resource.get("version") != SOURCE_DOI or resource.get("acquisition") != "sample_approved":
        raise AuditError("the catalog does not approve this exact version for bounded local review")
    if resource.get("rights", {}).get("license") != "CC0-1.0":
        raise AuditError("the catalog no longer records the reviewed CC0 1.0 declaration")
    files = resource.get("files", [])
    if len(files) != 1 or files[0].get("name") != "data.xlsx":
        raise AuditError("the catalog must pin exactly the reviewed data.xlsx sample")
    manifest = files[0]
    if not isinstance(manifest.get("bytes"), int) or not re.fullmatch(r"[0-9a-f]{64}", manifest.get("sha256", "")):
        raise AuditError("the catalog does not contain an exact byte length and SHA-256")
    return manifest


def _column_index(cell_ref: str) -> int:
    match = re.match(r"([A-Z]+)", cell_ref.upper())
    if not match:
        raise AuditError("worksheet contains a cell with an invalid reference")
    result = 0
    for char in match.group(1):
        result = result * 26 + ord(char) - ord("A") + 1
    return result - 1


def _worksheet_path(archive: zipfile.ZipFile) -> str:
    try:
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    except (KeyError, ET.ParseError) as exc:
        raise AuditError("workbook metadata is missing or malformed") from exc
    sheets = workbook.findall("main:sheets/main:sheet", NS)
    if len(sheets) != 1:
        raise AuditError("expected one worksheet in the reviewed sample")
    rel_id = sheets[0].get(f"{{{NS['office_rel']}}}id")
    relation = next(
        (item for item in relationships.findall("package_rel:Relationship", NS) if item.get("Id") == rel_id),
        None,
    )
    if relation is None or relation.get("TargetMode") == "External":
        raise AuditError("worksheet relationship is missing or external")
    target = relation.get("Target", "")
    if target.startswith("/"):
        path = target.lstrip("/")
    else:
        path = posixpath.normpath(posixpath.join("xl", target))
    if not path.startswith("xl/worksheets/") or ".." in path.split("/"):
        raise AuditError("worksheet relationship points outside the workbook sheet directory")
    return path


def _cell_value(cell: ET.Element, shared_strings: list[str]) -> str:
    if cell.find("main:f", NS) is not None:
        raise AuditError("formula cells are not evaluated; this sample must contain static source values")
    cell_type = cell.get("t")
    if cell_type == "inlineStr":
        return "".join(part.text or "" for part in cell.findall(".//main:t", NS))
    value = cell.find("main:v", NS)
    text = "" if value is None else (value.text or "")
    if cell_type == "s" and text:
        try:
            return shared_strings[int(text)]
        except (ValueError, IndexError) as exc:
            raise AuditError("workbook contains an invalid shared-string reference") from exc
    return text


def read_rows(path: Path) -> list[dict[str, str]]:
    """Read a single-sheet XLSX using standard-library ZIP/XML only."""
    try:
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            if len(names) > 100 or any(name.startswith("/") or ".." in name.split("/") for name in names):
                raise AuditError("workbook has an unexpected or unsafe ZIP structure")
            if sum(info.file_size for info in archive.infolist()) > 5 * 1024 * 1024:
                raise AuditError("workbook expands beyond the 5 MiB inspection limit")
            shared_strings: list[str] = []
            if "xl/sharedStrings.xml" in names:
                try:
                    shared_root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
                except ET.ParseError as exc:
                    raise AuditError("shared strings are malformed") from exc
                shared_strings = [
                    "".join(part.text or "" for part in string.findall(".//main:t", NS))
                    for string in shared_root.findall("main:si", NS)
                ]
            sheet_path = _worksheet_path(archive)
            try:
                sheet = ET.fromstring(archive.read(sheet_path))
            except (KeyError, ET.ParseError) as exc:
                raise AuditError("worksheet is missing or malformed") from exc
    except (OSError, zipfile.BadZipFile) as exc:
        raise AuditError(f"cannot read XLSX workbook: {exc}") from exc

    xml_rows = sheet.findall(".//main:sheetData/main:row", NS)
    if not xml_rows:
        raise AuditError("worksheet has no tabular rows")
    matrix: list[list[str]] = []
    for xml_row in xml_rows:
        cells: dict[int, str] = {}
        for cell in xml_row.findall("main:c", NS):
            index = _column_index(cell.get("r", ""))
            if index in cells:
                raise AuditError("worksheet contains duplicate cell references")
            cells[index] = _cell_value(cell, shared_strings)
        width = max(cells, default=-1) + 1
        matrix.append([cells.get(index, "") for index in range(width)])
    headers = matrix[0]
    non_empty_headers = [header for header in headers if header]
    if len(non_empty_headers) != len(set(non_empty_headers)):
        raise AuditError("worksheet has duplicate non-empty column names")
    missing = set(REQUIRED_FIELDS) - set(headers)
    if missing:
        raise AuditError(f"worksheet is missing required columns: {sorted(missing)!r}")
    result = []
    for values in matrix[1:]:
        row = {header: values[index] if index < len(values) else "" for index, header in enumerate(headers) if header}
        if any(row.get(field, "").strip() == "" for field in REQUIRED_FIELDS):
            raise AuditError("a source row is missing an experimental-unit or outcome field")
        result.append(row)
    if not result:
        raise AuditError("worksheet has a header but no data rows")
    return result


def _integer_value(value: str) -> int:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise AuditError("egg-cluster values must be numeric") from exc
    if not math.isfinite(number) or number < 0 or not number.is_integer():
        raise AuditError("egg-cluster values must be finite non-negative integers")
    return int(number)


def summarize_rows(rows: list[dict[str, str]], input_sha256: str) -> dict[str, Any]:
    """Validate paired side records and return aggregate-only condition counts."""
    grouped: dict[tuple[str, ...], Counter[str]] = defaultdict(Counter)
    aggregates: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"rows": 0, "egg_clusters": 0, "repetitions": set(), "paired_observations": 0}
    )
    for row in rows:
        if any(not row.get(field, "").strip() for field in REQUIRED_FIELDS):
            raise AuditError("a source row is missing an experimental-unit or outcome field")
        experiment = row["Experiment"].strip()
        key = tuple(row[field].strip() for field in ("Experiment", "Season", "Repetition", "Observation date", "Arena"))
        grouped[key][row["Side examined"].strip()] += 1
        aggregate = aggregates[experiment]
        aggregate["rows"] += 1
        aggregate["egg_clusters"] += _integer_value(row["Clusters of eggs"])
        aggregate["repetitions"].add((row["Season"].strip(), row["Repetition"].strip()))

    for key, sides in grouped.items():
        if len(sides) != 2 or len(set(sides.values())) != 1 or not next(iter(sides.values()), 0):
            raise AuditError("each keyed arena/date visit must contain balanced rows for exactly two examined sides")
        aggregates[key[0]]["paired_observations"] += next(iter(sides.values()))

    results = []
    for experiment, aggregate in sorted(aggregates.items()):
        observed = {
            "repetitions": len(aggregate["repetitions"]),
            "paired_observations": aggregate["paired_observations"],
            "egg_clusters": aggregate["egg_clusters"],
        }
        expected = TABLE1_EXPECTED.get(experiment)
        if expected is None:
            mapping = "not mapped to a Table 1 condition in this review"
            matches_table1 = None
        else:
            mapping = "Table 1 condition label"
            matches_table1 = observed == expected
        results.append(
            {
                "workbook_condition": experiment,
                "mapping_review": mapping,
                **observed,
                "table1_reported": expected,
                "matches_reported_table1_counts": matches_table1,
            }
        )
    table1_rows = [result for result in results if result["table1_reported"] is not None]
    return {
        "schema_version": 1,
        "source": {"attribution": ATTRIBUTION, "doi": SOURCE_DOI, "url": SOURCE_URL, "license": LICENSE},
        "input": {"file": "data.xlsx", "bytes": None, "sha256": input_sha256, "source_checksum_match": None},
        "method": {
            "unit": "One observation is one balanced pair of examined sides for a Season/Repetition/Observation date/Arena key; repeated balanced pairs under the same key count separately.",
            "processing": "Standard-library XLSX ZIP/XML parsing of static cell values; no deposited code or spreadsheet formulas were executed.",
            "table1_conditions_match": len(table1_rows) == len(TABLE1_EXPECTED) and all(
                result["matches_reported_table1_counts"] for result in table1_rows
            ),
            "table1_conditions_checked": len(table1_rows),
        },
        "aggregate_results": results,
        "limits": [
            "This is an aggregate source-table consistency check, not a reproduction of the paper's statistical models or adjusted contrasts.",
            "The extra workbook condition labeled Bat is not mapped to a reported oviposition outcome in the reviewed article; do not interpret it as a published plant-sound result.",
            "An aggregate count match does not verify all workbook files, code, model assumptions, ecological generalization, or the authors' conclusions.",
            "No raw rows, dates, arena identifiers, or animal-level records are emitted; the sample is not admitted to model training or the private database.",
        ],
    }


def summarize(path: Path | None = None) -> dict[str, Any]:
    """Verify the catalog-pinned source bytes, then return a safe aggregate report."""
    manifest = _pinned_manifest()
    input_path = path or (_repo_root() / "data" / "external" / RESOURCE_ID / "data.xlsx")
    try:
        payload = input_path.read_bytes()
    except OSError as exc:
        raise AuditError(f"cannot read pinned sample {input_path}: {exc}") from exc
    if len(payload) != manifest["bytes"]:
        raise AuditError("received workbook size does not match the pinned catalog")
    digest = hashlib.sha256(payload).hexdigest()
    if digest != manifest["sha256"]:
        raise AuditError("received workbook SHA-256 does not match the Mendeley file-panel value")
    rows = read_rows(input_path)
    report = summarize_rows(rows, digest)
    report["input"]["bytes"] = len(payload)
    report["input"]["source_checksum_match"] = True
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", nargs="?", type=Path, help="optional local path to the already-acquired data.xlsx")
    parser.add_argument("--output", type=Path, help="optional path for the aggregate-only JSON report")
    args = parser.parse_args()
    try:
        report = summarize(args.workbook)
    except AuditError as exc:
        parser.error(str(exc))
    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
