# First model and dataset decision

Reviewed September 30, 2026. This is a feasibility decision, not an installed environment, benchmark result or legal clearance. No model weights or animal recordings were downloaded.

## Decision

Prefer a small classifier over frozen Perch embeddings for a first **acoustic context-association experiment**, conditional on a suitable species, question and dataset. Compare it with majority-class, simple acoustic-feature and background/context baselines. Do not build a new foundation model or natural-language animal persona. A voluntary parrot interface would require a different experiment and might not need an acoustic model at all.

This choice keeps the initial implementation small and permits a future commercial route under the listed model terms. It does not establish task performance or an original research contribution. The existing Hoplite workflow already covers embedding search, annotation and classifiers; use or contribute to it where practical.

## Candidate register

| Candidate | Verified reference | Rights and role | Remaining check |
| --- | --- | --- | --- |
| Perch 2, TensorFlow CPU variant | `google/bird-vocalization-classifier/tensorFlow2/perch_v2_cpu/1`; version 1 is selected by the frozen official Hoplite configuration below | CPU candidate for embeddings. Parent model card lists Apache-2.0. | CPU-specific card did not render through the research tool. Inspect the downloaded bundle's terms, checksum and signature before adoption; local performance is untested. |
| Perch 2, TensorFlow GPU variant | `google/bird-vocalization-classifier/tensorFlow2/perch_v2/2` | Official card lists Apache-2.0; TensorFlow >=2.20 and GPU required for this variant. | Use only if measured need justifies GPU work. |
| Perch-Hoplite | Commit `050c57b5dac2f6d28ab1f562fa2000c8dcbc2302` | Apache-2.0 code; preferred inference/tooling route over the older Perch repository. | Reviewed README and model configuration, not a code audit or installation test. |
| NatureLM-audio | Hugging Face revision `77855d9b0acd039f90798dcf0861f626bfefbd6f` | CC BY-NC-SA 4.0 model card; optional research comparator for audio descriptions. | Parent-model terms also matter. No permission for a paid service has been established. |
| Main BirdNET package/models | Official README checked; no binary selected | MIT code; listed model terms CC BY-NC-SA 4.0. Identification comparator if required. | Pin exact model and inspect its own terms before use. |
| BirdNET-STM32 | Separate official license page checked; no release bundle selected | MIT project code, Apache-2.0 trained artifacts. Potential later edge-device route. | Not interchangeable with main BirdNET weights. No hardware need established. |

Perch's listed input is five seconds of mono 32 kHz audio, with a 1,536-dimensional embedding. Preserve original timestamps and call boundaries when framing; do not assign five-second context labels blindly. Scores are not calibrated probabilities. Training-data overlap remains unresolved. The parent card also shows inconsistent spatial-embedding shapes in different sections, so inspect actual signatures if those outputs become relevant; the first baseline only needs pooled embeddings.

Sources: [Perch model card](https://www.kaggle.com/models/google/bird-vocalization-classifier/tensorFlow2/perch_v2), [older repository notice](https://github.com/google-research/perch), [Hoplite at reviewed commit](https://github.com/google-research/perch-hoplite/tree/050c57b5dac2f6d28ab1f562fa2000c8dcbc2302), [frozen model configuration](https://github.com/google-research/perch-hoplite/blob/050c57b5dac2f6d28ab1f562fa2000c8dcbc2302/perch_hoplite/zoo/model_configs.py), [NatureLM revision](https://huggingface.co/EarthSpeciesProject/NatureLM-audio/tree/77855d9b0acd039f90798dcf0861f626bfefbd6f), [BirdNET](https://github.com/birdnet-team/birdnet), [STM32 terms](https://birdnet-team.github.io/birdnet-stm32/license/).

## Data feasibility

| Data route | What was checked | Decision |
| --- | --- | --- |
| Bark transfer-learning study | Primary paper and data-access statement: recordings available by author request. | Potential replication route; no access or redistribution permission obtained. Author contact requires authorization. Does not validate parrot transfer. |
| BEANS / BEANS-Next | Official task configuration, dataset card and displayed metadata. BEANS dog task labels are individual identities. BEANS-Next includes acoustic-description tasks and per-record license fields. | Useful benchmark candidates, not automatic substitutes for synchronized, independently observed behavior. No benchmark run, full metadata audit or overlap audit performed. |
| User-created parrot-app prototype / contributed recordings | A local app workspace was reviewed statically. No recording or dataset was reviewed; package/source provenance, audio rights and usable research observations remain unverified. | Reuse workflow ideas only. Do not copy code/media or treat its call labels and response signals as validated research data. |
| New passive observation study | No recruited animals, protocol or collaborator. | Define with an appropriate scientist after founder context and access are known. |

Update, October 11: the 2023 budgerigar aging study is a useful multimodal near-match, not a call-level context dataset. Calls were recorded from isolated focal birds while visually, but not acoustically, connected to flockmates; social actions were coded from separate home-flock video. The Dryad deposit lists derived call-feature tables and social coding but no original call WAVs. It may support a flock-level vocal-learning/sociality analysis after exact joins and review, but cannot train or test event-level sound-to-behavior prediction. See `content/research.json`, `content/sources.json` and `research/resources.json` for review depth, location, files and separate article/data/software terms.

BEANS-Next metadata revision: `2fc58150c9541698ffc82aaf1f5d5a44993c54bf`. The dataset card lists CC BY-NC-SA 4.0 while its Croissant metadata describes mixed source licenses; retain per-record restrictions. A public test set is not a training set for reporting an independent benchmark result.

Sources: [bark paper](https://aclanthology.org/2024.lrec-main.1432/), [BEANS task configuration](https://github.com/earthspecies/beans/blob/main/datasets.yml), [BEANS-Next card](https://huggingface.co/datasets/EarthSpeciesProject/BEANS-Next), [license metadata](https://huggingface.co/datasets/EarthSpeciesProject/BEANS-Next/blob/main/beans-next.croissant.json).

No reviewed route is yet admitted as Talk2Nature's context dataset. That is a project-specific finding, not a claim that suitable public data does not exist.

Update, September 30: a subsequent bounded collection found and inspected a promising public monk-parakeet annotation table and associated MIT analysis code. It is still not admitted for training: behavior labels, uncertainty, identities and audio linkage need auditing. See `COLLECTION.md`, `research/resources.json` and `research/parrot_sample_report.json`. No recordings or model weights were acquired.

Update, October 11: a targeted fit review changed the role of this candidate. The study asks whether known, individually marked monk parakeets can be identified across call types; it does not test behavior or call meaning. The cross-call-type protocol appears to hold recordings out while retaining known identity classes, so it should not be described as unseen-bird generalization. Use it only as a possible caller-identity reproduction comparator after split/reliability review. It is not the first context dataset. Direct full-text retrieval remained limited and no replication was run; see the dated note in `content/research.json` and `docs/COLLECTION.md`.

## Resume gate and first executable milestone

1. Audit source/package provenance and any available recordings separately; select one species and one observable target with a scientific collaborator. Confirm whether the work concerns natural calls or a learned interface.
2. Document original recording rights, human consent where applicable, individuals, sessions, devices/sites, observation provenance and annotation agreement. Check near duplicates and possible pretraining overlap. Decide what can be published separately from what can be analyzed.
3. Freeze the model artifact and dependency environment; record artifact checksums and measured runtime on a small permitted sample. Verify preprocessing and align every crop with observation timestamps.
4. Use the existing manifest validator; additionally hold out relevant sites/devices/time where needed. If groups or class coverage cannot support the chosen evaluation, revise the question or gather appropriate data before reporting accuracy.
5. Predefine metrics, background controls, cluster-aware uncertainty, calibration and abstention. Report failure cases and all prespecified comparisons. A predictive association alone does not establish meaning or two-way communication.

Until these inputs exist, more model integration would commit the project to an untested task. The current code milestone remains the tested metadata/split foundation.

## October 9 update: agent-assisted research

Karpathy's AutoResearch is a useful model for a tightly scoped experiment loop, but its GPT pretraining code and validation bits-per-byte objective do not fit Talk2Nature's current research state. No model training was run or enabled. The project adopted a controlled, future-facing agent program with pre-run data/rights/label/split/baseline gates and a locked final test set. See [`AUTORESEARCH_ADAPTATION.md`](AUTORESEARCH_ADAPTATION.md); the runnable status remains **not ready**.
