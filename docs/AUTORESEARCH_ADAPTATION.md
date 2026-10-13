# Adapting AutoResearch to Talk2Nature

Reviewed October 12, 2026 against upstream commit `228791fb499afffb54b46200aca536f79142f117`. This is a workflow decision, not an ML benchmark, training run or scientific result.

## Decision

Adopt the disciplined experiment-control pattern behind Andrej Karpathy's [AutoResearch](https://github.com/karpathy/autoresearch/tree/228791fb499afffb54b46200aca536f79142f117), but do **not** import its trainer or start autonomous animal-data experiments yet. At the pinned revision, an agent changes `train.py`, runs on a single NVIDIA GPU within a fixed five-minute training budget, and optimizes validation bits-per-byte while `prepare.py` keeps data preparation and evaluation fixed. Its [program file](https://github.com/karpathy/autoresearch/blob/228791fb499afffb54b46200aca536f79142f117/program.md) scopes the agent and logs kept, discarded and crashed trials.

That pattern is useful once Talk2Nature has a defensible benchmark. The objective is different: a language-model loss is not an animal-behavior measure, and the best score on a repeatedly inspected validation set is not scientific evidence. Our current [model/data decision](MODEL_DATA_DECISION.md) says no Talk2Nature dataset is admitted for the proposed context task, no model is installed, and the inspected budgerigar sample does not supply the independent visible-behavior labels that task needs. MammAlps v3 and the separate Prompting-MammAlps retrieval release are documented as noncommercial methods comparators; the latter is video-only, its code license is undeclared and its split does not establish animal-held-out evaluation. Neither release meets the project's commercial-capable reuse path. The private `model_runs` workflow is synthetic metadata rehearsal and does not execute models ([lineage boundary](MEDIA_LINEAGE.md)).

Therefore the immediate integration is a project-specific agent protocol in [`research/autoresearch/program.md`](../research/autoresearch/program.md), not a copied training framework. It is marked **NOT READY** and forbids model execution until its entry gates are met. Synthetic fixtures may test software plumbing only; they cannot be reported as model performance or animal findings.

## What to borrow and what to change

| AutoResearch idea | Talk2Nature adaptation |
| --- | --- |
| Give the agent a concise `program.md` | Define one reviewed task, allowed code files, stop conditions and human decisions outside the agent loop. |
| Freeze the data-preparation and evaluation harness | Freeze and fingerprint the admitted dataset, label/codebook version, preprocessing, group split, metric implementation and environment before model tuning. The current splitter is not enough by itself: household/site/device and near-duplicate controls may also be required. |
| Run a baseline before changing the model | Reproduce a simple majority/context/background baseline and a relevant existing-tool baseline before neural model tuning. Preserve exact revisions and permissions. |
| Keep or discard changes against a fixed metric | Preserve every outcome, including crashes and discarded trials. Compare prespecified metrics and uncertainty; do not keep a one-seed winner just because its score is lower. |
| Bound experiment time and complexity | Fix a compute/data-exposure budget and record hardware, time, memory and seeds. A five-minute run is not automatically fair or comparable for a different task or machine. Prefer simpler methods when evidence is comparable. |
| Repeat a loop autonomously | Keep autonomous work inside a disposable local branch and approved data boundary. No network upload, animal playback, permissions changes, data/label/split/evaluation edits, automatic merge, publication or deployment. Human review decides what counts as a scientific finding. |

For scientific evaluation, training and validation may guide development, but a separate locked test set must stay unseen until the protocol, model and analysis are frozen. Checkpoint, epoch, hyperparameter, threshold, early-stopping and seed selection must use training/validation data only. Run the frozen final pipeline on the locked test only after all choices and the reporting plan are fixed; do not use that result to select among candidates or launch another optimization cycle. If anyone inspects test results and changes the pipeline, treat that set as development data and obtain a new independent test set before making a generalization claim. Record final-test access and any deviation in the run ledger. The WhAM review is a concrete caution: its paper describes best-checkpoint selection using test-set performance, so those reported scores are not an untouched final holdout estimate ([review note](../content/research.json)). Report results at the animal/session/site unit appropriate to the question, include uncertainty and failures, and distinguish prediction from association, meaning and communication.

## Readiness gates

The agent program stays inactive until a qualified reviewer and project owner confirm all applicable items:

1. One narrow species-specific question, observable target, study unit and stopping/welfare rules are specified. The first phase remains passive; no automated playback is permitted.
2. Recording and annotation rights, consent or a documented reason it is not required, allowed use, retention and access are verified for the exact dataset release.
3. Labels come from independent observation, not from audio/model output; label definitions, missingness and reviewer agreement are documented.
4. Exact source hashes and a frozen release are available. Split groups prevent the relevant individual, session, original recording and site/device/household leakage; near-duplicates and likely pretraining overlap have been assessed.
5. The evaluation harness and locked test set are independent of the agent. Checkpoint, hyperparameter, threshold, early-stop and seed selection are validation-only; final-test access occurs only after the pipeline and report plan are frozen. Metric, uncertainty method, seed schedule, compute cap and success/stop criteria are registered before tuning.
6. A permitted baseline and at least one appropriate existing-tool comparator have been reproduced. Exact code, checkpoint and dataset terms are reviewed separately.
7. The run has a local-only environment with no credentials, no upload path, bounded disk/compute, recoverable checkpoints and a human reviewer. Any requirement for hosted processing gets a separate storage/security approval.

If any gate fails, record the blocker and do not train. The next useful scientific work is to settle the target and data/reviewer path, then establish the smallest honest baseline; it is not to acquire a GPU or launch an overnight agent.

## Run card and ledger

Before a future run, fill and review this card. Missing values mean no run:

```text
experiment_id:
question_and_hypothesis:
species_and_target:
protocol_and_codebook_version:
dataset_release_id_and_fingerprint:
rights_consent_and_retention_review:
train_validation_test_split_fingerprints:
checkpoint_selection_rule: validation_only
locked_test_access_policy: final_frozen_pipeline_only
baseline_revisions:
primary_metric_and_uncertainty:
seed_schedule:
compute_and_data_exposure_caps:
permitted_files_to_change:
environment_and_model_artifact_fingerprints:
success_stop_and_failure_rules:
independent_reviewer:
approval_date:
```

After readiness, keep a durable ledger with one row per trial: experiment ID, trial ID, commit, dataset and split fingerprints, model/environment fingerprint, seed, hypothesis, change, metrics, baseline delta, runtime, peak memory, outcome (`keep`, `discard`, or `crash`), reason and reviewer. Record whether the locked test was accessed; it must remain unopened during iteration, and no test-set metric may select a checkpoint, threshold, seed or candidate. Preserve failed runs. Do not store private recording paths, participant identifiers or raw media in a public ledger.

## Sources and scope

- [Karpathy's AutoResearch README](https://github.com/karpathy/autoresearch/blob/228791fb499afffb54b46200aca536f79142f117/README.md) and [agent program](https://github.com/karpathy/autoresearch/blob/228791fb499afffb54b46200aca536f79142f117/program.md) were reviewed October 12, 2026. The README declares MIT, but the pinned root has no `LICENSE` file and GitHub API metadata reports no recognized license. Code permissions therefore remain unresolved; do not copy or redistribute the trainer. Talk2Nature adopted only an original experiment protocol and did not copy code or dependencies. The public, metadata-only record is in [`research/resources.json`](../research/resources.json).
- Current Talk2Nature gates: [model/data decision](MODEL_DATA_DECISION.md), [data collection and rights](COLLECTION.md), [media/model lineage](MEDIA_LINEAGE.md), and [first-animal protocol](PILOT_PROTOCOL_DRAFT.md).

This is an internal project workflow proposal. It is not a claim that an AI agent is a scientist, that the project can translate animal communication, or that a future benchmark has been approved.
