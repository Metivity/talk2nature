# Talk2Nature agent research program

**Status: NOT READY — do not start model training.**

This file adapts the experiment-control pattern in [Karpathy's AutoResearch at the reviewed revision](https://github.com/karpathy/autoresearch/tree/228791fb499afffb54b46200aca536f79142f117) to a future Talk2Nature benchmark. See [the adaptation decision](../../docs/AUTORESEARCH_ADAPTATION.md). It is not a training script or permission to access real recordings; no upstream code is included.

## Current task

No ML task is approved. The working scientific question in `docs/GOAL.md` remains a candidate: whether audio adds predictive information about a small set of independently observed behaviors beyond context baselines on appropriately held-out animals and sessions. The species, target, real-data release, reviewer and evaluation remain unresolved. MammAlps v3 is a metadata-only noncommercial methods comparator: it pairs video-annotated behavior with audio, but the reviewed evidence does not establish animal-level holdout and its CC BY-NC 4.0 data do not enter the commercial-capable benchmark path. The green-rumped parrotlet Dryad archive is another metadata-only lead, this time about vocal development; its README, individual/session structure, treatment groups and item-specific license terms remain unverified, and the corticosterone study does not answer the current context-prediction question. Do not substitute either candidate, synthetic fixtures or the structurally inspected budgerigar sample for an admitted project dataset.

## Start conditions

Do not run an agent or model until the project owner and a qualified scientific reviewer have completed the run card in `docs/AUTORESEARCH_ADAPTATION.md`, verified every applicable readiness gate there, and approved a specific local run. If a required gate cannot be evidenced, stop and report it.

## Validation-only selection and locked test

Select checkpoints, epochs, hyperparameters, thresholds, early stopping and seeds using training/validation data only. Do not query the locked final test during an autonomous loop. After the model, preprocessing, thresholds, seed schedule, metrics and report plan are frozen, evaluate the final pipeline on that test and report the result without using it to choose a candidate. The WhAM review documents a published downstream protocol that selected its best classifier checkpoint on the test split; treat that as a cautionary example, not a procedure to copy.

If a test result is viewed and then influences any choice, mark that set as development data. Do not report it as a final generalization estimate; a new independent test set is required. Log whether and when final-test access occurred and any deviation. This policy does not make the current task ready: all other scientific, rights and safety gates still apply.

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
