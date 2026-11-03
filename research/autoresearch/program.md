# Talk2Nature agent research program

**Status: NOT READY — do not start model training.**

This file adapts the experiment-control pattern in [Karpathy's AutoResearch at the reviewed revision](https://github.com/karpathy/autoresearch/tree/228791fb499afffb54b46200aca536f79142f117) to a future Talk2Nature benchmark. See [the adaptation decision](../../docs/AUTORESEARCH_ADAPTATION.md). It is not a training script or permission to access real recordings; no upstream code is included.

## Current task

No ML task, dataset, model or run is approved. The current *candidate* first computational question in [`docs/MODEL_DATA_DECISION.md`](../../docs/MODEL_DATA_DECISION.md) is passive detection of whether any bird sound is present in a ten-second soundscape clip, evaluated across held-out recording domains. The output is a sound-presence proposal only; it is not species, caller, behavior, meaning or communication. The detailed [benchmark candidate run card](../../docs/BENCHMARK_CANDIDATE_RUN_CARD.md) keeps this separate from the communication-adjacent bat and finch research leads.

DCASE 2018 Task 3 is a task-design precedent, not the current data candidate. Its task page describes manually verified labels, while the BirdVox deposit says binary labels were derived automatically from flight-call annotations. The official evaluation audio deposit lists no labels and has a blank license field; the challenge-level CC BY 4.0 statement does not resolve component rights. The baseline uses legacy Python 2.7/Theano/Lasagne dependencies, and its repository-level code license has not been established. No DCASE audio, labels, code or weights were acquired or run.

CEB v1.1 is the leading metadata-only candidate dataset for this detection-engineering question, not an admitted benchmark. Its record declares CC BY 4.0 for soundscape audio and annotations, but the 8.56 MB training annotation table exceeds the project's current 5 MiB collector limit. The official evaluation labels are already public, not a concealed locked test; project identifiers' relationship to acquisition groups remains unverified. No CEB table, audio, code or weights were acquired or run. Follow the [candidate run card](../../docs/BENCHMARK_CANDIDATE_RUN_CARD.md); do not bypass the intake limit or access public test labels for model selection. Any future run needs qualified event-definition review, source/group and duplicate checks, a separate untouched evaluation, and a permitted baseline/comparator.

MammAlps v3 remains a metadata-only noncommercial methods comparator: it pairs video-annotated behavior with audio, but the reviewed evidence does not establish animal-level holdout and its CC BY-NC 4.0 data do not enter the commercial-capable benchmark path. The green-rumped parrotlet Dryad archive remains a metadata-only vocal-development lead; its README, individual/session structure, treatment groups and item-specific license terms remain unverified. These behavior-focused studies do not replace the current sound-presence candidate. Do not substitute either candidate, synthetic fixtures or the structurally inspected budgerigar sample for an admitted project dataset.

## Start conditions

Do not run an agent or model until the project owner and a qualified scientific reviewer have completed the run card in `docs/AUTORESEARCH_ADAPTATION.md`, verified every applicable readiness gate there, and approved a specific local run. If a required gate cannot be evidenced, stop and report it.

## Validation-only selection and locked test

Select checkpoints, epochs, hyperparameters, thresholds, early stopping and seeds using training/validation data only. Do not query the locked final test during an autonomous loop. After the model, preprocessing, thresholds, seed schedule, metrics and report plan are frozen, evaluate the final pipeline on that test and report the result without using it to choose a candidate. The WhAM review documents a published downstream protocol that selected its best classifier checkpoint on the test split; treat that as a cautionary example, not a procedure to copy.

If a test result is viewed and then influences any choice, mark that set as development data. Do not report it as a final generalization estimate; a new independent test set is required. Log whether and when final-test access occurred and any deviation. This policy does not make the current task ready: all other scientific, rights and safety gates still apply.

## Pipeline-comparability gate

The 2025 mammal caller-identity methods comparison reports that outcomes vary with feature extraction and classifier choice; its MFCC/random-forest consistency finding is limited to known-caller tasks in its tested mammal datasets ([Talk2Nature's review](https://metivity.github.io/talk2nature/research/same-data-different-results-bioacoustics-2025/)). Before any future comparison is reviewed for approval, the run card must freeze and identify:

- the exact estimand, including known-caller classification versus unseen-caller transfer when identity is the target;
- the crop/window policy, source and processing sample rates, channels, filters and resampling;
- feature extraction/model/checkpoint version and parameters, tuning procedure, and software/environment fingerprint;
- group/split membership, random seeds, class balance, primary metric and uncertainty method.

Compare candidates on the same question-appropriate frozen groups and report sensitivity to the prespecified pipeline variants. Do not mix preprocessing changes with model changes and then attribute the score difference to the model; if preprocessing itself is under study, declare it as a separate method-comparison experiment before evaluation. MFCC plus random forest is not a default Talk2Nature baseline. This gate refines recordkeeping only; the program remains **NOT READY**, and no model or recording may be run under this section.

## Agent scope after approval

For a future, separately approved run:

- Work only on the named `codex/` experiment branch and exact approved revision.
- Change only the model/configuration files named in the reviewed run card. Do not change data, labels, preprocessing, splits, evaluation, metrics, rights records or this program during a run.
- Run the same frozen baseline, seeds and budget for each candidate. Do not expose or query the locked final test set while iterating; validation alone may guide selection, and a test result never selects a checkpoint or candidate.
- Record every attempted change, metric, uncertainty, runtime, memory use and outcome, including crashes and discarded trials.
- Keep all recordings local in the approved access boundary. Do not upload, publish, share, play sounds to animals, contact people, access credentials, merge, deploy or change permissions.
- Stop when the declared budget or stopping rule is reached. Do not continue overnight or expand scope without fresh human review.

An improvement is a candidate for human review, not a scientific conclusion. Before a result is shared, preserve the exact source/data/model versions, review failures and confounds, and obtain independent reproduction appropriate to the claim.

## Permitted preparation while not ready

Only read public documentation, refine the run card, test existing tools on clearly synthetic fixtures, and identify missing prerequisites. Synthetic checks must be labeled software-only and must not be described as biological accuracy, model performance or evidence of communication.
