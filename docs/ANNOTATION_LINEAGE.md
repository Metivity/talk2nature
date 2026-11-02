# Keep observations, review and model proposals separate

This synthetic methods exercise shows how a researcher can retain independent human annotations, record a later review decision, and inspect an algorithmic proposal without turning those records into one “ground truth” label. It creates no new annotation format for production and contains no audio.

## Run the example

From the repository root:

```sh
python3 -m unittest discover -s tests -p 'test_annotation_lineage.py' -v
```

The versioned package is [`annotation-lineage.synthetic.v1.json`](../examples/annotation-lineage.synthetic.v1.json). It references the existing invented observer files and invented acoustic-unit proposal. The two observers use the same declared synthetic recording metadata, but there is no recording payload. The reviewer entry preserves both files, leaves the shared-event question undetermined, and records no consensus label. The model proposal was not executed and carries no kind, context, behavior, meaning, translation, or confidence claim.

## Why this separation matters

Talk2Nature's [annotation comparison note](ANNOTATION_COMPARISON.md) reports interval overlaps; overlap alone does not establish that two marks describe one biological event. Dubus et al. (2024) studied two specific blue-whale call-detection tasks and tested aggregation against separate expert-annotated evaluation sets. Miller et al. (2026) used adjudication in one Antarctic blue-whale density-estimation workflow, but explicitly within that task. These studies support recording how a review decision was made and evaluating aggregation against a defined target; neither supplies a universal consensus rule.

The October 2026 speech-transfer preprint compares 15 frozen encoders on caller identification and call-type classification. It finds acoustic information transfer, but no semantic decoding. Some caller-identity folds split one recording session into blocks, allowing the same individual in train and test; session-independent sensitivity results are lower. This is why a model proposal belongs in its own provenance-bearing record and why any future evaluation must group by the entity relevant to the claim. See the [source-grounded review](https://metivity.github.io/talk2nature/research/speech-pretraining-transfer-2026/) and [primary preprint](https://arxiv.org/abs/2610.07107).

## Format loss is visible

[`annotation-lineage-loss-report.synthetic.v1.json`](../examples/annotation-lineage-loss-report.synthetic.v1.json) records a non-executed APLOSE/OSEkit preflight against the pinned reference described in [`APLOSE_INTEROPERABILITY.md`](APLOSE_INTEROPERABILITY.md). It marks absolute time, frequency bounds, point/weak/box geometry, codebook mappings, review history and context provenance as unavailable or non-equivalent. The report is not an export, converter, conformance claim or license determination. Rights to third-party example CSVs and any user media remain unresolved.

## Evidence boundary

All records in this exercise are invented metadata. The tests verify file links and separation rules, not biology, scientific agreement, legal rights, APLOSE compatibility or model behavior. No real recording intake, upload, training, playback or research admission is enabled. AutoResearch and real-data admission remain **NOT READY**.

## How an independent review can help

Reviewers can assess whether the provenance boundaries and declared losses are adequate, identify the exact software/version they use, or point out a safer representation. Use the public [scientific methods review form](https://github.com/Metivity/talk2nature/issues/new?template=scientific-review.yml); it creates a public issue and requires GitHub sign-in. Do not include private files, recordings, participant or animal identifiers, unpublished work, personal contact details or sensitive locations. A submitted issue is a review lead, not an endorsement, partnership or approval to collect data.
