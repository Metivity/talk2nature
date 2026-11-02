# APLOSE and Talk2Nature: annotation export crosswalk

**Status:** research and format preflight only. No adapter, APLOSE installation, upload, real recording, or parser execution is included. The comparison uses Talk2Nature's current `talk2nature.annotation.v1` contract and official OSEkit documentation/source pinned below. It does not claim APLOSE conformance or lossless interoperability.

## What was reviewed

- APLOSE v3.15.0 was the latest stable release reported by GitHub on November 2, 2026. Its repository README describes an annotation phase and a verification phase, including checks of detector outputs, with annotations stored and exportable.
- OSEkit source was inspected at commit [`39170854efa35e6a17ce1da5e15e6c73109d14b9`](https://github.com/Project-OSmOSE/OSEkit/commit/39170854efa35e6a17ce1da5e15e6c73109d14b9). The inspection covered `Detection.from_dict`/`from_csv`, its field handling, the published APLOSE results example's header and one example row, and the OSEkit MIT license. The example CSV was inspected transiently; it was not retained, copied into this repository or treated as a rights-cleared dataset.
- Talk2Nature's source contract is [`talk2nature.annotation.v1`](../web/assets/listen-model.mjs) with synthetic shape coverage in [`notebook.test.mjs`](../tests/notebook.test.mjs). An annotation JSON file describes a selected WAV and human-entered intervals; it is not a research-admission manifest.
- APLOSE's README says MIT and also says “This software must not be sold”; its linked LICENSE is standard MIT text permitting sale. That conflict remains unresolved. The example CSV's reuse terms were not verified.

The SoftwareX paper was reviewed only at its publisher-indexed abstract because the full text returned HTTP 403. No APLOSE/OSEkit runtime, user account, installation, security posture, storage policy or institutional workflow was tested.

## Field comparison

| Information | APLOSE / OSEkit example | Talk2Nature today | Interoperability status |
| --- | --- | --- | --- |
| Recording reference | `project`, `filename`; optional annotation ID and update-of ID | recording/session identifiers plus source WAV SHA-256, duration, sample rate, channels and origin | Not a shared ID namespace. A filename is not a checksum; preserve both source identities and an explicit crosswalk. |
| Event time | CSV exposes relative `start_time`/`end_time` and absolute `start_datetime`/`end_datetime`; the inspected OSEkit parser reads the absolute datetime fields | `start_seconds`/`end_seconds` relative to the selected WAV | Conversion needs a verified file/time origin and timezone. Do not infer a UTC instant from relative offsets alone. |
| Label | `annotation` or `label` becomes the parser's detection label | Bounded `kind`, `context`, `context_source`, `confidence` and free-text `notes` | No automatic label-to-kind mapping. A researcher-approved codebook is needed; keep the original label and its source. |
| Frequency | Minimum and maximum frequency bounds are read by the OSEkit parser; the CSV also has start/end frequency fields | No frequency-bound fields in `annotation.v1` | Cannot round-trip frequency geometry. Do not invent bounds or silently discard them. |
| Geometry/type | `WEAK`, `POINT` and `BOX` types appear in the format; weak rows can span a spectrogram, points have zero-duration examples, and boxes carry frequency bounds | Human-marked intervals require `end_seconds > start_seconds`; no point or frequency box geometry | Not representable losslessly. Preserve the original source file or report the unsupported object. |
| Reviewer provenance | Annotator, expertise, confidence, phase, update lineage and verification decisions can be represented; OSEkit interprets nonstandard columns as verification fields | One annotator ID per label document and an event confidence; no per-event multi-review history or adjudication state | Disagreement and verification history cannot be collapsed into one Talk2Nature event. Preserve separate annotator records if a future protocol supports them. |
| Context | Comments and acoustic signal descriptors are available in the export | Human-entered context plus how it was observed, uncertainty and notes | A comment is not an independently observed behavior/context field. Keep evidence types distinct. |

The parser's `from_csv` reads rows into detections; this does not make every exported column semantically equivalent across tools. The example and parser are versioned reference points, not a compatibility guarantee for every APLOSE release.

## Decision and acceptance gate

**Decision:** no converter or APLOSE connector now. A bare CSV adapter would lose or misstate frequency bounds, point/weak geometry, absolute-time provenance, reviewer disagreement and context provenance. It could also accept an unversioned label as if it were a Talk2Nature sound-kind or biological meaning.

If a university documents a specific need, the next experiment is a synthetic-only crosswalk with a named APLOSE version and exact export file. Before any code is called interoperable, it must:

1. Preserve original file identity and checksum while distinguishing Talk2Nature IDs from APLOSE project/filename/annotation IDs.
2. Check an explicitly supplied timezone and file start against APLOSE relative and absolute time fields; otherwise mark conversion unavailable.
3. Retain original labels and per-annotator/review rows without mapping them to context, meaning or aggregate truth.
4. Report unsupported frequency bounds, `WEAK`/`POINT`/`BOX` geometry, updates and verification fields in a machine-readable loss report; fail closed for any requested lossless export.
5. Reopen the result in the exact target software version and have the requesting researcher review the preserved and lost fields.
6. Resolve applicable software terms and the example-data rights before any code reuse, sample redistribution, hosted service or real data flow.

This preflight does not change the passive, local-first Field Companion, approve upload, admit research data or authorize use of APLOSE code/data. AutoResearch and real-data admission remain **NOT READY**.
