# Compare independent annotation exports

Updated November 2, 2026. The browser tool at `/tools/annotation-compare/` compares two Talk2Nature `annotation.v1` exports locally. It is a small research-review aid, not an adjudication system or a training-data pipeline.

## What it checks

- The input documents pass the existing Talk2Nature annotation validator.
- Both documents declare the same WAV checksum, duration, sample rate, channel count and origin.
- The two documents declare different annotator IDs.
- Every pair of events with a positive time overlap is listed. Events may appear in multiple rows; no one-to-one pairing is inferred.
- Both declared sound-kind values are shown and compared by exact string equality. Context values are shown and compared only when both annotators supplied a non-unknown context with an observation source.
- Events with no positive interval overlap are listed separately. No timing tolerance is applied.

The comparison report excludes free-text notes, annotator IDs and filenames. It contains the declared WAV SHA-256 and event identifiers, so inspect it before sharing. Files are parsed in the current browser tab; no request containing the selected files is made, and no browser storage, audio playback or recording is used. Clearing the page or closing it drops the selected documents from memory.

## What it does not infer

A positive interval overlap does not establish the same biological event, call meaning, label truth or inter-rater agreement. Exact category equality is not a validated score. No events are merged, ranked, adjudicated or aggregated; no coefficient, accuracy or ground truth is computed. A missing overlap does not show that no sound occurred. The checksum and recording fields are declared by the files and are not independently verified against audio here.

This boundary follows the scope of Dubus et al. (2024): nineteen novices and one bioacoustics expert annotated two blue-whale call-detection types. The paper assessed novice annotations and task-specific majority-vote and soft-label aggregation against separately annotated evaluation sets; expert labels served as pseudo-ground truth for the study. It supports retaining independent reviewer labels and testing any aggregation against a defined task, not assuming that the majority is biologically right. Those results do not establish behavioral meaning or a universal aggregation rule. Read the [source-grounded project review](../content/research.json) and [primary article](https://doi.org/10.1016/j.ecoinf.2024.102642).

A second, distinct study informs the boundary: Miller et al. (2026) compared three experienced observers and two automated detectors for Antarctic blue whale song calls. Their adjudicated capture-recapture workflow produced more consistent call-density estimates across observers and detectors than treating each human observer as ground truth. They explicitly describe adjudication as helping detector characterization, not replacing manual annotation for detector development. This is a single site-year density-estimation result; it does not establish a universal event-matching rule. The comparison tool follows that lesson by exposing overlaps while leaving every source annotation intact. Read the [focused project review](../research/whale-call-adjudication-2026/) and [primary article](https://doi.org/10.1111/2041-210x.70331).

## Try the invented example

Open the comparison page and choose the committed fixtures:

- [`annotation-observer-a.synthetic.json`](../examples/annotation-observer-a.synthetic.json)
- [`annotation-observer-b.synthetic.json`](../examples/annotation-observer-b.synthetic.json)

They share a declared checksum and contain invented intervals only. The expected output lists two positive-overlap pairs and one event without positive overlap. No animal recording is present. The tests verify that notes and annotator IDs do not enter the report, mismatched checksums fail closed, and one-to-many overlap remains visible.

Maintainer browser check: both fixtures loaded locally; the page rendered two overlap pairs, preserved unmatched event `#12`, downloaded a report without notes or annotator IDs, and cleared both selections. At 390 px and 320 px, the document stayed within the viewport and results were presented as paired A/B cards instead of requiring horizontal panning across the seven-column table; desktop retains the semantic table. Files were selected at desktop width before resizing; no physical phone, assistive technology or independent researcher tested this workflow.

## Limits and next decision

The implementation supports the current `talk2nature.annotation.v1` fields only. It does not import APLOSE or another platform, align independent clocks, accept frequency bounds or point/weak/box geometries, validate study labels, or replace a specialist-approved codebook. A university workflow needing more than this local comparison should name the target software version and file schema first. Any future adapter needs an explicit mapping, a loss report, rights review and a successful synthetic reopen in the target version.

This tool changes no research-admission gate. Real recording collection, recruitment, shared storage and model training remain separate activities requiring their own protocol, rights and review. AutoResearch and real-data admission remain **NOT READY**.
