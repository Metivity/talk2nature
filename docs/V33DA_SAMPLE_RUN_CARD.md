# V33DA sample and caller-attribution run card

**Status: review proposal only.** No V33DA media, code or model has been acquired or run. This card does not authorize sample acquisition, training, recruitment, playback or admission to the private database. AutoResearch remains **NOT READY**.

## Why start here

If Talk2Nature wants one small, technically testable ML exercise from an existing animal dataset, V33DA is a strong candidate for **caller attribution**: given an already-detected, isolated call and the birds visible at that moment, can the system rank the bird that produced it? The dataset card reports 33,625 physically verified call events from 10 zebra finches, three experiments, 16 days and about 74 hours, with synchronized audio, video, pose and accelerometer-derived caller labels. The accelerometer is the label source and must not be a model input. The main release excludes overlapping calls and comes from one aviary/recording geometry.

This is useful infrastructure research, not animal-language translation. The labels do not establish behavior, addressee, receiver response, intent or meaning. The 10 birds—not the 33,625 events—are the important limit on claims about new animals.

## Pinned source and component rights

- Dataset card: [V33DA at the reviewed Hugging Face revision](https://huggingface.co/datasets/songbirdini/v33da/tree/975ddf36a1f0c0bffc512bf2c2e6aa40bb2a1913).
- Reference code and included sample: [repository at commit `e988b985e38909b40b2705cdad994e3d9307181e`](https://github.com/marisbasha/v33da/tree/e988b985e38909b40b2705cdad994e3d9307181e).
- The pinned dataset card declares CC BY 4.0; the nested README separately declares CC BY 4.0 for its 100-event media sample, described as about 60 MB. The repository's top-level MIT license applies to software, not that sample. Dependencies, manuscript, model weights and the V33DA++ companion release are separate components.
- Talk2Nature's catalog remains metadata-only. The pinned Git tree verifies paths, sizes and Git blob IDs; SHA-256 checks are recorded for the three small text files only. No Parquet or media bytes, per-media checksums or media provenance were reviewed. The three text files were fetched into memory, hashed and discarded; no media, Parquet, code or model weights were acquired or run.

These are upstream license declarations, not independent legal clearance. Keep attribution and change notices if a later approved reuse occurs. A permissive declaration does not establish that every modality, third-party element or intended commercial use has been cleared.

## Metadata-only inventory and split review — October 23

The complete Git tree below `data/v33da_sample/` at the pinned code commit is recorded in [`research/v33da_sample_manifest.json`](../research/v33da_sample_manifest.json). The source API returned a complete, non-truncated tree; its root tree SHA is `f7d865dcc79047819781e696c53dbb72a7e3b18b`. This is a path/size/Git-blob inventory, not a copy of the data. Git blob IDs are not SHA-256 hashes.

| Component | Files | Bytes |
| --- | ---: | ---: |
| Microphone audio WAV | 100 | 8,001,360 |
| Accelerometer WAV | 100 | 5,790,852 |
| Aligned video clips MP4 | 100 | 47,831,719 |
| Camera calibration | 30 | 15,838 |
| Sample table and root metadata | 4 | 864,207 |
| **Total** | **334** | **62,503,976** |

The root README describes 100 events stratified across BP01/BP02/BP05. Path-derived event keys match across the 100 audio, 100 accelerometer and 100 video files, with 34/33/33 keys across those experiments. That checks filenames only; no Parquet row, timestamp join, media content or calibration was inspected. The largest listed file is 1,345,906 bytes, so each file is below the current 5 MiB collector cap; the complete sample exceeds its 20 MiB per-invocation cap and has not been acquired.

Three small text files were fetched from the pinned code commit over verified TLS and hashed in memory. Their hashes match the Git blob IDs in the pinned tree; no copies were retained. The Parquet and media remain untouched.

| Text file | Bytes | SHA-256 | Git blob SHA-1 |
| --- | ---: | --- | --- |
| `README.md` | 5,025 | `28ed4902b9478954d2ef657008a422862fa34941e5feb7039357b121174cd882` | `54373063fbfa71de14da4aa40406f6750651f1ac` |
| `metadata.json` | 2,214 | `6f2173f6a3fdfbdef04a19f7194dda025e0b6078bc9bf167f7970f2810027dbd` | `768c45a07706559a2b13d7a19bdbd12160f9ad82` |
| `split_summary.json` | 823 | `885d448c71875e4e4b56849eeedb6dfec14076515a55de366a1a2e7ace1d185e` | `4d9b8586690763592a2c657201af39ce5bff9969` |

The sample's `metadata.json` and `split_summary.json` report the **full release's** 33,625 rows and split counts. The root README says `v33da_sample.parquet` contains 100 rows, but the Parquet was not read. The split summary is therefore not a sample-specific partition and the 100-event convenience sample is not a locked test set. The pinned card says color names are experiment-local and all 10 released birds are distinct. Its caller table lists three BP05 callers (brown, purple, yellow), while sample metadata also includes red under `bird_names` without an event-count group. Red could be a visible non-caller candidate or stale metadata; its role and per-event candidate membership are unverified. Do not infer a fourth caller, and do not calculate a chance baseline until candidate sets are verified.

The full-release generalization split described in the sample's summary metadata is:

| Partition | BP01 events | BP02 events | BP05 events | Total |
| --- | ---: | ---: | ---: | ---: |
| Train | 12,881 | 8,610 | 0 | 21,491 |
| Validation | 3,338 | 2,967 | 0 | 6,305 |
| Test | 0 | 0 | 5,829 | 5,829 |

The pinned card says colors are local to each experiment and all 10 released physical birds are distinct. The event counts by physical caller are:

| Experiment | Physical caller (experiment-local color) | Events | Split role |
| --- | --- | ---: | --- |
| BP01 | blue / peach / red / white | 5,735 / 2,277 / 3,963 / 4,244 | Train + validation (exact per-bird allocation not verified) |
| BP02 | blue / peach / red | 4,923 / 4,589 / 2,065 | Train + validation (exact per-bird allocation not verified) |
| BP05 | brown / purple / yellow | 56 / 2,140 / 3,633 | All three held out in experiment test |

Thus BP05 contains three unseen physical callers in the reported experiment-held-out split. It is still a bundled shift: experiment, group composition, year/date and cage/recording conditions change together, so the split cannot isolate which factor explains an outcome. One held-out bird contributes only 56 events. These are event counts, not independent sample sizes.

The session-disjoint counts are BP01 train/validation/test 12,881/1,008/2,330; BP02 4,455/4,155/2,967; BP05 2,029/1,706/2,094. That regime uses the same birds on different sessions and does not test unseen-bird generalization. Leave-one-bird-out support is advertised, but exact fold membership and implementation remain unverified. No split from these summaries is adopted for Talk2Nature.

## Companion dataset screen — V33DA++ (October 23)

The pinned V33DA++ card (revision `bb31f73e2191278dd4965af01502c42380cd597d`) describes three buckets: 3,784 reviewer-verified overlapping-call rows; 33,625 single-vocalizer events with plus/minus two seconds of context; and 3,784 overlap events with the same context. The padded overlap bucket repeats the overlap events, so the provider's 41,193-row total is not a count of unique events. The release uses the same ten birds and recordings as V33DA. It is a method candidate for vocal-activity detection, source separation and audio-visual synchronization, not for receiver-response or call-meaning prediction. The provider lists 167 GB total.

The dataset card declares CC BY 4.0; preprocessing tools, reference code, paper and weights retain separate terms. The current linked GitHub revision is still `e988b985e38909b40b2705cdad994e3d9307181e`. Its training entry point imports `v33da.data` modules absent from the tree, and its split-preparation script materializes session/experiment date splits but no independently auditable leave-one-bird-out assignment. No data, media or code were acquired or run. This screen adds no authorization to download or train; keep V33DA++ metadata-only and AutoResearch **NOT READY**. See the source-linked [V33DA++ evidence note](../content/research.json).

## Bounded sequence

1. **Metadata preflight complete, no acquisition.** The pinned sample tree and README have been checked through source metadata and the complete sample-only inventory is recorded. The Parquet/media contents, sample-to-full-release membership and per-file media provenance remain unverified.
2. **Intake ceiling.** Any later proposed sample intake must fit the existing collector's 5 MiB per-file and 20 MiB per-invocation limits. Do not bypass those limits with direct downloads, alternate tools or archive splitting. The advertised ~60 MB sample does not fit in one approved batch; do not fetch it wholesale. No acquisition is authorized by this card.
3. **Loader smoke test, if separately approved.** A bounded subset may test parsing, checksums, timestamp alignment and candidate/label joins. A 100-event sample is not a performance benchmark and cannot support a generalization claim. Keep all downloaded source files and receipts in ignored `data/external/`; do not add them to Git, the website or `examples/`.
4. **Baseline proposal, not yet run.** After alignment, microphone geometry and pose calibration are independently checked, compare candidate-count chance with a simple CPU candidate-ranker using acoustic features and permitted candidate-relative pose. Compare audio-only with audio-plus-pose. Do not begin with a conversational LLM or a large pretrained model. Freeze the estimand, candidate construction and metrics before examining test results.
5. **No scale-up by default.** Any full-release analysis needs its own storage, rights, compute, evaluation and reviewer decision. The upstream card reports an 18.8 GB release; this project has not downloaded it.

## Leakage and split plan

Keep the accelerometer target channel, caller-label fields, stable bird identity/name/color, filenames, source paths, experiment/date/session identifiers and radio telemetry out of the initial predictor. Radio telemetry may encode which bird is which; it is not an admissible shortcut to acoustic caller attribution. Use only the call audio and a justified, calibrated representation of which candidates were visible and where they were, after the source joins have been verified.

The unseen-bird claim requires every event from one physical bird to remain in one partition. Also group shared sessions/source recordings and audit duplicates before freezing folds. The pinned reference describes an experiment/date split that holds out BP05, bundling bird, group, date/year and cage changes; one BP05 bird has only 56 events. The README advertises leave-one-bird-out support, but its precise implementation and fold membership have not been verified. Therefore, do not describe the advertised split as verified or as a clean causal explanation of any performance difference. A held-out-experiment result can be reported only as a bundled shift test.

Use top-1 candidate attribution as the primary metric, show candidate-count chance, report per-bird and per-experiment results, and describe uncertainty at bird/session level. With only 10 birds, uncertainty and coverage will be limited; do not choose a pass threshold until an independent avian and ML/statistical reviewer approves the question and evaluation. A smoke test produces no scientific score.

## Stop gates

Stop before acquisition or modeling if the exact sample manifest/checksums cannot be verified; if any component's rights or attribution are unclear; if labels cannot be joined to candidate pose without oracle fields; if physical-bird grouping or duplicate-source checks fail; if the only feasible sample is above the reviewed byte cap; or if an independent reviewer finds the estimand or held-out claim unsound. A failure can still be documented as a useful methods result.

## What this means for the broader project

Use the general Field Companion to support observations about many animals, but make scientific claims one species and one task at a time. Keep three tracks separate: V33DA for caller attribution; the Egyptian-fruit-bat work for the currently documented communication-adjacent context-prediction question; and budgerigars for a possible household usability/feasibility cohort if real access and an avian researcher are secured. None substitutes for the others. The older [zebra-finch vocal-repertoire collection](https://figshare.com/articles/dataset/Vocal_repertoires_from_adult_and_chick_male_and_female_zebra_finches_Taeniopygia_guttata_/11905533) is a possible later audio-only comparison: it lists individual, date and 11 call-type labels under CC BY 4.0, but is not an independent visible-behavior or meaning dataset and notes expected annotation-name discrepancies.

**Next gate:** independent avian and ML/statistical review of the caller-attribution estimand, candidate identity mapping, full-release split, sample metadata discrepancy and proposed byte budget. Then decide whether a narrowly bounded intake is scientifically useful and separately authorized. Do not acquire data or run a model merely because a public download exists.
