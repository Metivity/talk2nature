# Independent review scope: bird sound-event benchmark

**Status:** public request for independent methods review in [GitHub issue #721](https://github.com/Metivity/talk2nature/issues/721). No reviewer response or endorsement has been received. Scope refreshed November 5, 2026.

## Purpose

Ask whether detecting the **presence of bird sound in a bounded passive soundscape window** is a useful first computational task for Talk2Nature, and compare DCASE 2018 Bird Audio Detection with ArcticBirdSounds as candidate data routes. DCASE defines binary presence/absence labels on 10-second clips, but label provenance differs across sources and evaluation labels remain private in the reviewed public record. ArcticBirdSounds is a richer temporal-classification lead, but its event annotations do not establish that every unannotated interval is a true negative. This remains an ecological sensing task, not species identification, caller identity, behavior inference, a test of call meaning, receiver understanding, or conversation. The companion-parrot observation study remains separate.

The window duration and event definition are intentionally undecided pending review. A catalog of annotated events does not establish that every unannotated interval is a true negative; do not infer absence or completeness from missing annotations.

No audio, annotation rows, precise locations, code, or model weights are included in this scope. The brief does not authorize data acquisition, row-level inspection, model execution, recruitment, playback, or research claims. The reviewer is asked to assess scientific design; their opinion would not replace separate rights, ethics, privacy, or security review.

## Evidence already reviewed

- The ArcticBirdSounds article describes 20 recording hours from 2018–2019, 12,933 temporal annotations, and 49 sound classes; its data statement says CC BY 4.0. The refreshed current OSF node API declares CC BY 4.0 for the dataset, consistent with the paper. This dataset-level declaration does not license the separate OSF code folder, article/supplement, linked GitHub code, model assets or upstream inputs. The aggregate audit verifies filename/site grouping, but has not established annotation exhaustiveness or valid negatives for bird-vocalization presence.
- The official [DCASE 2018 Task 3 specification](https://dcase.community/challenge2018/task-bird-audio-detection) defines 10-second bird-sound presence/absence labels, cross-dataset validation and states CC BY 4.0 for all challenge datasets. Label provenance is mixed: the [BirdVox-DCASE-20k deposit](https://zenodo.org/records/1208080) says its labels were automatically derived from source annotations, while Stowell et al. (2019) describe manual annotation for Warblr and freefield1010. The [evaluation deposit](https://zenodo.org/records/1298604) contains audio only and shows no license value; the challenge paper says test labels were kept private. The task page additionally says its public preview score used approximately 1,000 randomly selected Chernobyl/Warblr clips; teams could submit up to 20 variants and choose four for final scoring. The preview subset is therefore feedback-touched, not an untouched Talk2Nature test. The task also allowed per-dataset adaptation to evaluation-set aggregate statistics. The official [baseline repository](https://github.com/DCASE-REPO/bulbul_bird_detection_dcase2018) documents Python 2.7/Theano/Lasagne; no top-level code license was established in the listing reviewed.
- The refreshed filename-manifest and bounded ZIP-directory audit finds 2,280 schema-valid annotation/FLAC pairs across 19 plot/year groups, against 2,400 segments and 20 groups reported in the paper. All pairs map by the documented year+plot key to six coarse site labels. A separate uncompressed-WAV directory has 1,600 entries and omits 680 matched FLAC keys. This supports constructing a candidate site partition; it does not prove independent field sessions or class support. The article materials identify six study locations; current manifests resolve six coarse site labels for the CSV/FLAC pairs, while the uncompressed WAV manifest maps to five groups. The article and supplement also differ on the location count. No class-by-site cross-tab has been reviewed.
- ECOGEN's published five-class use reports a per-class 75/25 split, not a site/plot/session holdout; its Methods and table totals differ by one sample. The ArcticSoundsNET paper reports training a binary BirdNET detector with approximately 18 hours of ArcticBirdSounds. These are prior-use and model-lineage warnings, not independent baseline evidence.
- BirdSet is a separate scale resource with noncommercial aggregate terms and source-specific licensing. Wytham great-tit caller identity and companion-parrot behavior are different tasks and remain separate from this proposal.

## Questions for the reviewer

1. Is bounded-window bird-vocalization-presence detection a useful first software task for Talk2Nature? What narrow event definition is biologically and operationally defensible?
2. Does DCASE's mixed label provenance support the specific “any bird sound” positive/negative target? For manually annotated and automatically derived components, what are the known label scope, uncertainty and failure modes? Can any DCASE group support an independent evaluation after the historical preview and repeated-submission selection, given that reviewed public records expose no evaluation labels? How should the original permission for dataset-statistics adaptation affect any reproduction?
3. Compared with DCASE, could ArcticBirdSounds support a better pilot through finer temporal labels and plot/year grouping, or do coverage, missing-pair and class-by-site gaps make that impractical? What minimum aggregate evidence could change the decision without opening audio or annotation rows?
4. What grouping unit would support a credible unseen-site or unseen-session test? Which groups may be dependent because of plot, year, recorder, deployment, or repeated observations?
5. Which metrics and simple baselines fit event presence and its class imbalance? For example, what event-level precision/recall, false-positive rate or false alarms per hour, and abstention behavior should be reported? Do not select a window size, threshold or metric before considering sampling and annotation coverage.
6. Which prior-use and pretrained-model overlap checks are decision-critical? In particular, should ArcticSoundsNET's ArcticBirdSounds-trained detector be excluded, and what would be needed to assess BirdNET/Perch pretraining overlap?
7. Given the manifest and licensing discrepancies, should the project defer this dataset until source and file rights are reconciled? What evidence would be sufficient before even an aggregate-only audit?

## Decision requested

Please recommend one disposition and explain the evidence needed:

- **Proceed to a narrowly scoped aggregate metadata audit** (specify exact fields and why they can change the decision).
- **Continue with published metadata only** (specify the missing evidence and whether it is realistically obtainable).
- **Defer ArcticBirdSounds and select another task/data route** (explain why).

If an audit is recommended, specify the allowed fields, grouping definition, output aggregates, suppression needed to avoid exposing sensitive locations, and stop conditions. No row-level extraction or model run is implied. No personal or wildlife location coordinates should be included in any response.

## Current project position

The current recommendation is to scope passive bird-sound presence detection first. DCASE 2018 is the strongest task-match precedent, not a selected or admitted dataset; mixed label provenance, component rights, independent grouping and a locked test remain unresolved. Its public-preview subset is feedback-touched; public records reviewed here do not reveal an unused, labeled test. Treat its historical score as background only. ArcticBirdSounds is a secondary, finer-event metadata lead. Powdermill is a structural smoke test; High Sierra Nevada lacks a recording-to-lake join; BirdSet is large but noncommercial and heterogeneous; Wytham is a separate closed-set identity reproduction; and the budgerigar study requires its own access, review, consent, rights, privacy, and withdrawal plan. AutoResearch remains **NOT READY**.

## Source and project records

- [ArcticBirdSounds data paper](https://doi.org/10.1002/ecy.4047)
- [ArcticBirdSounds OSF record](https://osf.io/b9trx/) and [current node metadata API](https://api.osf.io/v2/nodes/b9trx/)
- [ECOGEN study](https://doi.org/10.1111/2041-210X.14239)
- [ArcticSoundsNET study](https://doi.org/10.1016/j.ecoinf.2025.103270)
- Internal audit: `research/arcticbirdsounds_metadata_report.json`, `research/arcticbirdsounds_archive_directory_report.json`
- Current decision: `docs/FIRST_ANIMAL_PLAN.md`; evidence note: `birdset-powdermill-first-compute-candidate` and `arcticbirdsounds-grouped-split-preflight` in `content/research.json`

This public review brief accompanies [issue #721](https://github.com/Metivity/talk2nature/issues/721). No reviewer response has been received. It does not authorize row-level inspection, recruitment, dataset admission, training, or deployment.
