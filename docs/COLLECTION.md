# Data, code and research collection

First bounded collection, September 30, 2026. Active project: Talk2Nature, Raviv's independent initiative, in `Metivity/talk2nature`. This work is independent of the unfinished Google Sign-In setup.

## Collected and checked

The existing library had 54 source records and 15 evidence notes. This pass adds four sources and one original evidence note, and organizes eight priority resources in `research/resources.json`. Existing same-day reviews are labeled as reused; this is not an exhaustive literature survey.

Nine source files totaling **92,952 bytes** were acquired in three local collections. They include one parrot annotation table, two R scripts, Perch configuration, documentation and license notices. Exact Git commits and upstream Git blob hashes were checked; each receipt also records SHA-256, retrieval time, attribution, rights and the acquisition-time catalog fingerprint. Code was inspected as text, never executed. No audio or model weights were acquired.

| Priority | Resource | Role and decision |
| --- | --- | --- |
| 1 | [Monk parakeet study](https://doi.org/10.1098/rsos.230835) and [code](https://github.com/simeonqs/Evidence_for_vocal_signatures_and_voice-prints_in_a_wild_parrot/tree/293b2c8d0c3b8e21a4eaa0511fe563207095765a) | Best new candidate for a focused feasibility audit. MIT code; selected scripts are incomplete and install packages dynamically. Review dependencies before execution. |
| 1 | [Deposited parrot data](https://doi.org/10.17617/3.RUIM5I) and the linked repository's 2020 annotations | Edmond API declares MIT for released v1.0. Small annotation sample acquired; scientific/training admission remains false. |
| 1 | [Perch-Hoplite](https://github.com/google-research/perch-hoplite/tree/050c57b5dac2f6d28ab1f562fa2000c8dcbc2302) | Apache-2.0 software. Selected configuration/documentation acquired; prefer existing tooling when an experiment is ready. |
| 1 | [Perch 2 CPU candidate](https://www.kaggle.com/models/google/bird-vocalization-classifier/tensorFlow2/perch_v2_cpu) | Parent terms reviewed previously; selected CPU bundle still requires artifact-level review. No weights downloaded. |
| 2 | [BirdVox-DCASE-20k](https://zenodo.org/records/1208080) | CC BY 4.0 detection benchmark. Bird presence labels do not supply behavioral context; excerpt sensor/time origins are withheld. Metadata only. |
| 2 | [BEANS-Next](https://huggingface.co/datasets/EarthSpeciesProject/BEANS-Next) | Mixed component terms and a noncommercial dataset card. Evaluation reference; excluded from this permissive sample collector. Preserve public-test boundaries. |
| 2 | [Japanese tit experiment](https://www.nature.com/articles/ncomms10986) | Reuse the existing methods review to design evidence standards. No new playback study or article redistribution. |

Plants and fungi stay in the existing evidence library and a separate sensing backlog. Their instruments, signals and validation targets do not justify mixing them into a bird-audio training corpus.

## What the parrot sample supports

`research/parrot_sample_report.json` is a reproducible aggregate report, not a training manifest. The table contains 808 annotation rows, 765 populated bird entries, 752 populated behavior entries, 176 distinct nonempty behavior strings and 12 explicit uncertainty flags. Bird entries have not been normalized into verified unique individuals. Blank flags do not prove certainty, and one annotation may link to several calls.

Behavior text includes observable activities and descriptions of vocal events. Treating all of these as independent labels would risk circular evaluation. The repository's separate `context` field describes call/sequence structure; its name alone is not evidence of behavioral ground truth. These findings come from the [pinned source table](https://github.com/simeonqs/Evidence_for_vocal_signatures_and_voice-prints_in_a_wild_parrot/blob/293b2c8d0c3b8e21a4eaa0511fe563207095765a/ANALYSIS/DATA/overview%20recordings/annotations%20-%202020.csv) and its README.

The first useful next experiment is conditional: test whether acoustics add predictive value for a small, independently recoded visible-behavior target. Before training:

1. Inspect the study's full methods and selection-table join code. Check multiple selections per annotation, uncertain identities and missing labels; audit a matched subset against original observation evidence.
2. Define a codebook from visible behavior, with an unknown/exclude option. Audit whether labels were influenced by the call itself and measure independent reviewer agreement where source evidence allows it. A table-only recode cannot establish independent observation reliability.
3. Link timestamps, original recordings and individuals. Construct connected groups across shared birds, sessions and source audio before framing or augmentation. If overlap leaves too few groups, change the question instead of forcing a split.
4. Compare majority/context-only, simple acoustic features and frozen Perch embeddings with a small classifier. Fit preprocessing on training data only; preserve a held-out evaluation and report per-class results, clustered uncertainty and failure cases. Evaluate background/device/site confounding and pretraining overlap.

The original MFCC script scales its combined matrix for a distance analysis. That is not automatically appropriate preprocessing for a new held-out classifier. No performance result, replication, semantic decoding or scientific endorsement is claimed here.

## Acquisition backlog and limits

The three Edmond archives total **100,498,691,932 bytes** (about 100.5 GB decimal), according to its [public metadata API](https://edmond.mpg.de/api/datasets/:persistentId/?persistentId=doi:10.17617/3.RUIM5I). Raw 2020 and 2021 audio alone are about 36.96 GB and 54.55 GB. None was downloaded. Investigate a documented way to obtain a bounded audio subset after the annotation audit; do not launch the full archive transfer by default. The full recording overview includes precise coordinates and is excluded from this sample.

Next acquisition order: selection-table/linkage metadata; a modest matched audio subset with a stated byte budget and privacy/location review; exact model artifact/license; frozen execution dependencies. Expand to other species only when they answer a defined question. Kiki remains an ownership/access dependency; no assets were imported.

## Reproduce

All commands below run from the repository root. Python 3.10+ standard library is sufficient for the collection tool.

```sh
python3 -m talk2nature.collection validate
python3 -m talk2nature.collection plan monk-parakeet-code monk-parakeet-annotations perch-hoplite-code
python3 -m talk2nature.collection fetch monk-parakeet-code monk-parakeet-annotations perch-hoplite-code
python3 scripts/inspect_parrot_annotations.py --output research/parrot_sample_report.json
python3 -m unittest discover -s tests -v
```

`plan` does not access the network. `fetch` requires explicit resource IDs and reviewed acquisition fields. The initial adapter accepts only commit-pinned HTTPS files on `raw.githubusercontent.com`, with expected sizes and Git blob hashes. Per-file limit is 5 MiB; per-invocation limit is 20 MiB, optionally lowered with `--max-bytes`. It refuses redirects, HTML responses, unresolved/restricted rights, changes in size/hash, path traversal and overwrite of an existing collection. Downloads are staged; a failed transfer/check leaves no published sample. It does not extract archives, install packages or execute code. These limits apply to this tool, not other programs on the computer.

If this Python installation lacks a working CA bundle, provide a trusted one with `--ca-file /absolute/path/to/cacert.pem`; never disable TLS verification. This run used the existing environment's `certifi` bundle after the system Python failed certificate verification. No new dependency was added to the research toolkit.

Samples and receipts live under ignored `data/external/`. To avoid accidentally overwriting a reviewed collection, fetching an existing ID stops; inspect its receipt first. Receipts preserve the catalog at retrieval time, while the current catalog can subsequently record inspection findings. Hashes prove correspondence to the reviewed files, not biological truth or freedom from copyright/privacy issues. Retained license fields are documented assessments, not automated legal clearance.

Original summaries, bibliographic metadata and aggregate diagnostics can be tracked in Git. Downloaded third-party source files, annotations, locations, recordings, PDFs and weights stay out of Git and `dist/`. The private admin's synthetic-only rule remains intact; this external public-source inspection is a separate workflow. No cloud charges, partner messages, applications, push or deployment occurred in this collection milestone.
