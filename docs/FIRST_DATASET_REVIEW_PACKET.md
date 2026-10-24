# First-data decision: independent no-data review packet

Updated October 24, 2026. This packet is for a bounded literature-and-methods review before selecting a Talk2Nature benchmark. No reviewer has been contacted, no animal data or models have been acquired, and no benchmark is selected or ready.

## The decision to review

Should Talk2Nature start with a Great Tit song-structure methods exercise, choose a different communication-adjacent task, or defer modeling until the evidence improves? Reviewers may assess one route only. A useful answer can be **go**, **narrow**, or **defer**; it is not a request for endorsement, partnership, animal recruitment, playback, or human-language translation.

The review needs two distinct kinds of expertise: an independent bioacoustics/behavior reviewer to assess the question, labels and biological claim; and an independent ML/statistical reviewer to assess the evaluation unit, grouping, leakage, baselines and uncertainty. One reviewer may identify a limit in their own area and recommend the other review. Independence, source authorship and relevant recent collaboration must be disclosed before the review is described as independent.

## Candidate snapshot

| Route | Bounded question | Current evidence and unresolved gate |
| --- | --- | --- |
| **Great Tit / Wytham — methods path** | Can a method reproduce expert-marked song-note structure on prepared songs from birds excluded from model fitting? | Authors report 109,963 prepared songs and more than 1.16 million annotated notes. The OSF node declares CC BY 4.0 for the dataset record. The complete current API tree has 23 files totaling 12,184,678,510 bytes (14 data and nine docs); an earlier same-day 14-entry traversal only listed the data/ folder. All normalized paths and sizes match the prior snapshot, but the provider SHA-256 for docs/metadata/main.md differs at the same byte size. No payloads or coordinate values were inspected, and provider hashes were not recomputed. The shared package excludes the original roughly 9 TB continuous soundscapes. A 2025 study already applied deep metric learning to repertoire similarity and song culture, so the task must add value. Author documentation places British National Grid nest-box coordinates in `nestboxes.csv` and `main.csv`. Confirm a distinct task, intended file/field scope, nested provenance, bird-held-out split, prior art, compute and wildlife-location minimization before any use. This is not a behavior or meaning dataset. |
| **Zebra finch / ZF-AIM — controlled vocal exchange** | Is a bounded next-caller, call-token or response-timing analysis scientifically useful, and what would a bird-independent test require? | The preprint's methods report 834,309 calls and 21 birds while a results passage reports 20. The described pair split does not establish disjoint evaluation birds. The separate data record's API says CC BY-SA 4.0 while its description says CC BY-NC; it lists four raw examples and does not establish full analyzed-corpus coverage. Keep metadata-only until those rights, corpus and grouping questions are resolved. Predicting a next call is not decoding its meaning. |
| **Egyptian fruit bat — observed-context association** | Does any narrower context-prediction estimand have a defensible held-out unit? | The source corpus has about 293,000 recordings and 91,080 video-derived annotations. In Talk2Nature's filtered subset, the file-plus-known-participant graph has a largest component of 95.56%; exact published fold membership and important session/date/channel/treatment joins remain unverified. This is a split-feasibility warning, not proof that the paper's results are wrong. It is not a receiver-comprehension test. |
| **Budgerigars — Field Companion cohort** | Can a passive phone workflow help carers make observations that an avian researcher would consider useful? | This is a product/usability hypothesis, not a public benchmark. Genuine access, qualified review, an approved protocol, consent, privacy, retention and withdrawal safeguards are not yet established. No participant recruitment or real-data intake is part of this review. |

The first three routes are not interchangeable. Wytham is the leading large-corpus methods candidate; zebra finches are the closest controlled bird vocal-exchange lead; bats offer video-coded context but currently have a difficult grouping structure. Budgerigars are a separate app path. A larger file count does not decide which question is scientifically strongest.

## Questions for reviewers

1. **Novelty and value:** Is the proposed question useful and distinct from the cited prior work? What published analysis must be reproduced or surpassed first?
2. **Labels and unit:** What exactly is the target label and unit of analysis—note, song, call, pair, context event, bird or session? Which labels are observed directly and which are inferred or assigned by people?
3. **Generalization and leakage:** What population should the result generalize to? Which birds, pairs, sessions, sites or devices must be held out together? Is there enough independent group structure for that test?
4. **Baselines and uncertainty:** Which simple label-prior, context-only, identity, timing or acoustic baseline is necessary? Which primary metric and uncertainty procedure respect repeated recordings and class imbalance? What outcome would justify stopping?
5. **Rights and data minimization:** Which exact paper, data, annotations, code, model weights and derived fields are needed? What terms govern each asset? For Wytham, can the proposed task avoid raw continuous soundscapes and exact nest-box locations?
6. **Decision:** Recommend **go**, **narrow**, or **defer** for the specific route you assessed. Name the smallest next check that could change your recommendation and the artifact it needs.

“Cannot assess from the available public record” is a valid conclusion. A reviewer recommendation does not grant rights or authorize acquisition. If the reviewers disagree, preserve both assessments and do not turn the disagreement into a consensus claim.

## Review and data boundaries

The linked evidence notes state review depth, versions, limitations and separate asset-rights status. Please cite the exact note or source sections you assessed, identify your review scope, and disclose authorship or relevant collaboration. A review may be submitted through the [scientific methods review form](https://github.com/Metivity/talk2nature/issues/new?template=scientific-review.yml). That issue is public; do not attach audio, annotations, participant or animal identifiers, private correspondence, unpublished material, credentials or sensitive locations.

This packet authorizes no data acquisition, model execution, animal playback, participant recruitment, private database intake, grant application or partner communication. A positive review would be one readiness input; the project must separately resolve exact rights, approved protocol, frozen grouped evaluation, baselines, a locked test and safe execution before any biological model run. Prediction and acoustic structure remain distinct from meaning or communication.

## Evidence index

- [Current candidate comparison](FIRST_DATASET_DECISION.md)
- [Benchmark candidate run card](BENCHMARK_CANDIDATE_RUN_CARD.md)
- [Wytham song-structure assessment](https://metivity.github.io/talk2nature/research/wytham-great-tit-song-structure-2024/)
- [ZF-AIM no-data review](ZF_AIM_INDEPENDENT_REVIEW.md)
- [Egyptian fruit-bat context review](BAT_CONTEXT_REVIEW.md)
- [Zebra-finch call-perception review](ZEBRA_FINCH_PERCEPTION_REVIEW.md)
- [Research execution board](EXECUTION_BOARD.md)

