#!/usr/bin/env python3
"""Create a reproducible, aggregate-only audit of the 2022 Japanese-tit tables.

This deliberately does not fit the deposited statistical models, infer meaning,
or admit the records to training. The source files must be obtained separately
from the versioned Figshare deposit and passed as a local directory.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any


SOURCE_DOI = "10.6084/m9.figshare.18007046.v1"
SOURCE_URL = "https://doi.org/10.6084/m9.figshare.18007046.v1"
ATTRIBUTION = "Suzuki, T. N. & Matsumoto, Y. K. (2022), Figshare item 18007046 v1"
LICENSE = "CC BY 4.0 (scope: the two deposited .txt outcome tables)"
TREATMENTS = ("1A-R", "2A-R", "1R-A", "2R-A")
TREATMENT_DESCRIPTIONS = {
    "1A-R": "one speaker; natural alert-to-recruitment order",
    "2A-R": "two speakers; natural alert-to-recruitment order",
    "1R-A": "one speaker; reversed recruitment-to-alert order",
    "2R-A": "two speakers; reversed recruitment-to-alert order",
}
FIELDS = ("date", "caller_ID", "trt", "2m", "wing", "flock_size", "shrike", "call_source")
MATCH_FIELDS = ("date", "caller_ID", "trt", "flock_size", "shrike", "call_source")


class AuditError(ValueError):
    """Input is not the expected, internally consistent source table pair."""


def _read_table(path: Path) -> list[dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream, delimiter="\t")
            if tuple(reader.fieldnames or ()) != FIELDS:
                raise AuditError(f"{path.name}: expected columns {FIELDS!r}")
            rows = list(reader)
    except OSError as exc:
        raise AuditError(f"cannot read {path}: {exc}") from exc
    if any(None in row or any(value is None for value in row.values()) for row in rows):
        raise AuditError(f"{path.name}: row has a missing or extra field")
    if len(rows) != 64:
        raise AuditError(f"{path.name}: expected 64 flock-trial rows, found {len(rows)}")
    return rows


def _integer(row: dict[str, str], field: str, filename: str) -> int:
    try:
        value = int(row[field])
    except (KeyError, TypeError, ValueError) as exc:
        raise AuditError(f"{filename}: {field} must be an integer") from exc
    if str(value) != row[field].strip():
        raise AuditError(f"{filename}: {field} must use an integer value")
    return value


def _table_index(rows: list[dict[str, str]], filename: str) -> dict[tuple[str, ...], dict[str, str]]:
    index: dict[tuple[str, ...], dict[str, str]] = {}
    for row in rows:
        key = tuple(row[field] for field in MATCH_FIELDS)
        if key in index:
            raise AuditError(f"{filename}: duplicate flock-trial key {key!r}")
        index[key] = row
    return index


def _pinned_file_manifest() -> dict[str, dict[str, Any]]:
    catalog_path = Path(__file__).resolve().parents[1] / "research" / "resources.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    resource = next(
        (item for item in catalog["resources"] if item.get("id") == "japanese-tit-core-merge-2022-data"),
        None,
    )
    if resource is None:
        raise AuditError("the catalog has no pinned Japanese-tit v1 data resource")
    files = {item["name"]: item for item in resource.get("files", [])}
    if set(files) != {"merge_binary.txt", "merge_proportion.txt"}:
        raise AuditError("the catalog's Japanese-tit data manifest is incomplete or unexpected")
    if any(not item.get("md5") or not item.get("bytes") for item in files.values()):
        raise AuditError("the catalog has no provider checksum and size for each data file")
    return files


def summarize(
    data_dir: Path,
    expected_files: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Validate the deposited pair and return only aggregate descriptive counts."""
    binary_path = data_dir / "merge_binary.txt"
    proportion_path = data_dir / "merge_proportion.txt"
    expected_files = expected_files if expected_files is not None else _pinned_file_manifest()
    actual_paths = {binary_path.name: binary_path, proportion_path.name: proportion_path}
    if set(expected_files) != set(actual_paths):
        raise AuditError("the pinned manifest does not match the expected data files")
    for name, path in actual_paths.items():
        try:
            payload = path.read_bytes()
        except OSError as exc:
            raise AuditError(f"cannot read {path}: {exc}") from exc
        expected = expected_files[name]
        if len(payload) != expected["bytes"]:
            raise AuditError(f"{name}: byte length does not match the pinned Figshare manifest")
        provider_md5 = hashlib.md5(payload, usedforsecurity=False).hexdigest()
        if provider_md5.lower() != expected["md5"].lower():
            raise AuditError(f"{name}: MD5 does not match the pinned Figshare manifest")
    binary_rows = _read_table(binary_path)
    proportion_rows = _read_table(proportion_path)
    binary_index = _table_index(binary_rows, binary_path.name)
    proportion_index = _table_index(proportion_rows, proportion_path.name)
    if binary_index.keys() != proportion_index.keys():
        raise AuditError("the binary and proportion files do not describe the same flock-trials")

    by_treatment: dict[str, list[tuple[dict[str, str], dict[str, str]]]] = {
        treatment: [] for treatment in TREATMENTS
    }
    for key, binary in binary_index.items():
        treatment = binary["trt"]
        if treatment not in by_treatment:
            raise AuditError(f"unexpected treatment code {treatment!r}")
        proportion = proportion_index[key]
        flock_size = _integer(binary, "flock_size", binary_path.name)
        binary_outcomes = {
            outcome: _integer(binary, outcome, binary_path.name)
            for outcome in ("2m", "wing")
        }
        proportion_outcomes = {
            outcome: _integer(proportion, outcome, proportion_path.name)
            for outcome in ("2m", "wing")
        }
        if flock_size <= 0:
            raise AuditError("flock_size must be positive")
        if any(value not in (0, 1) for value in binary_outcomes.values()):
            raise AuditError("binary outcome values must be 0 or 1")
        if any(value < 0 or value > flock_size for value in proportion_outcomes.values()):
            raise AuditError("proportion-table outcome count must be between 0 and flock_size")
        for outcome in ("2m", "wing"):
            if binary_outcomes[outcome] != int(proportion_outcomes[outcome] > 0):
                raise AuditError(f"{outcome}: binary and proportion outcomes disagree for {key!r}")
        by_treatment[treatment].append((binary_outcomes, {**proportion_outcomes, "flock_size": flock_size}))

    if any(len(by_treatment[treatment]) != 16 for treatment in TREATMENTS):
        counts = {treatment: len(rows) for treatment, rows in by_treatment.items()}
        raise AuditError(f"expected 16 flock-trials per treatment; found {counts!r}")

    summaries = []
    for treatment in TREATMENTS:
        pairs = by_treatment[treatment]
        birds = sum(proportion["flock_size"] for _, proportion in pairs)
        entry: dict[str, Any] = {"treatment": treatment, "flock_trials": len(pairs), "flock_members": birds}
        for outcome, label in (("2m", "approach_within_2m"), ("wing", "wing_flick")):
            flocks_with_event = sum(binary[outcome] for binary, _ in pairs)
            individuals_with_event = sum(proportion[outcome] for _, proportion in pairs)
            equal_flock_rates = [proportion[outcome] / proportion["flock_size"] for _, proportion in pairs]
            entry[label] = {
                "flocks_with_event": flocks_with_event,
                "flock_rate": round(flocks_with_event / len(pairs), 6),
                "individuals_with_event": individuals_with_event,
                "pooled_individual_rate": round(individuals_with_event / birds, 6),
                "mean_of_flock_rates": round(sum(equal_flock_rates) / len(equal_flock_rates), 6),
            }
        summaries.append(entry)

    return {
        "schema_version": 1,
        "source": {
            "attribution": ATTRIBUTION,
            "doi": SOURCE_DOI,
            "url": SOURCE_URL,
            "license": LICENSE,
        },
        "analysis": "Descriptive aggregation of the two deposited outcome tables; no inferential model or deposited R code was run.",
        "unit": "64 flock-trial rows, 16 per playback treatment; the two files describe the same trials.",
        "treatment_key": TREATMENT_DESCRIPTIONS,
        "input_validation": {
            "matching_trial_metadata": True,
            "binary_and_count_outcomes_consistent": True,
            "treatment_counts": {treatment: len(by_treatment[treatment]) for treatment in TREATMENTS},
        },
        "aggregate_results": summaries,
        "limitations": [
            "These are descriptive summaries of one species- and context-specific playback experiment.",
            "They are not a reproduction of the paper's mixed-effects models or adjusted contrasts.",
            "The results do not distinguish Core-Merge, finite-list, concatenation or other mechanisms.",
            "The tables contain no audio and are not an acoustic training dataset.",
            "No individual-level animal identities, locations, raw rows or audio are emitted by this report.",
        ],
        "input_files": {
            path.name: {
                "bytes": path.stat().st_size,
                "provider_md5": expected_files[path.name]["md5"],
                "provider_md5_match": True,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
            for path in (binary_path, proportion_path)
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data_dir", type=Path, help="Local directory containing the two Figshare v1 .txt files")
    args = parser.parse_args()
    try:
        result = summarize(args.data_dir)
    except AuditError as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
