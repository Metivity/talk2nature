# Align the AutoResearch program with the current benchmark decision

**Date:** November 5, 2026  
**Question:** do the AutoResearch program, benchmark shortlist and regression test agree about which dataset, if any, is selected?

## Evidence reviewed

Compared [`research/autoresearch/program.md`](../../research/autoresearch/program.md), [`docs/MODEL_DATA_DECISION.md`](../MODEL_DATA_DECISION.md), [`docs/BENCHMARK_CANDIDATE_RUN_CARD.md`](../BENCHMARK_CANDIDATE_RUN_CARD.md), and [`tests/test_autoresearch_protocol.py`](../../tests/test_autoresearch_protocol.py). The November 5 decision says no reviewed candidate clears all gates and the first benchmark is deferred. The program still called CEB v1.1 the leading candidate, and the test locked in that stale claim.

The underlying shortlist remains metadata-only: DCASE 2018 is the strongest task-fit lead but has unresolved label-component rights and no supplied evaluation labels; CEB remains prior art but its training-label table exceeds the intake cap, its public evaluation labels are not a hidden test, group independence is unknown, and unannotated intervals are not verified negatives. This milestone reuses those documented reviews; no new primary source or dataset was accessed.

## Change and verification

Updated the AutoResearch program to state that no dataset is selected or admitted, DCASE is only the strongest task-fit lead, and CEB is not selected. Updated the protocol regression test to enforce that decision. The program stays **NOT READY** and forbids training or real-data processing while the gates remain unmet.

Acceptance: `python3 tests/test_autoresearch_protocol.py` passes; full Python, public build and link checks pass; `git diff --check` passes.

## Limits and next decision

This is a consistency correction, not new scientific evidence or a benchmark review. It does not change the candidate task, approve data acquisition, permit model execution or satisfy independent review. Next: only revisit candidate selection after task-matched label provenance, component rights, leakage-safe groups, qualified review and an untouched evaluation are documented together.
