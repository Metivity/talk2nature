# First dataset decision: match the corpus to the question

**Status:** decision brief, October 24, 2026. This is a literature and metadata assessment. No animal recordings or model weights were acquired or run, and no candidate has been approved for a Talk2Nature benchmark.

## Recommendation

Keep three goals separate:

1. **Build the data and model workflow:** use Wytham Great Tit as the leading large-corpus *methods* candidate, if an independent reviewer identifies a non-duplicative task. A sensible scope is note/song structure or repertoire measurement with birds held out by individual. It is not a communication-meaning dataset.
2. **Ask a communication-adjacent biological question:** review the Egyptian fruit-bat or zebra-finch candidates with an independent bioacoustics reviewer and an ML/statistical reviewer. Neither has a defensible, rights-cleared, leakage-resistant benchmark plan yet.
3. **Serve companion-animal carers:** keep budgerigars as a provisional Field Companion cohort, conditional on genuine access, an avian researcher and an approved, non-invasive protocol. This is a product/user path, not a substitute for an open benchmark corpus.

**Do not train a general animal-language model.** Large audio collections and language-model interfaces can help detect, cluster, describe or predict acoustic patterns. Those outputs do not establish what an animal intends or understands. A meaning claim needs independent behavioral evidence and a suitable receiver-response test.

## Candidate fit

| Candidate | What the data can help test | Why it is not a communication benchmark yet |
| --- | --- | --- |
| **Wytham Great Tit Song Dataset** | The authors report 109,963 prepared annotated songs, more than 1.16 million acoustic notes and over 400 wild birds. Useful for a carefully scoped song-structure methods exercise on the shared song files. | No receiver-response or meaning labels; one population and dawn-singing setting. A 2025 study already uses deep metric learning for repertoire similarity and song culture, so any task must add value. The OSF node declares CC BY 4.0 for the dataset record; the setup-code repository is separately MIT. The complete October 24 API tree has 23 files totaling 12,184,678,510 bytes (14 under `data/` and nine under `docs/`); the earlier same-day 14-entry traversal omitted the docs folder. The 23 normalized paths and byte sizes match the previous snapshot. Provider SHA-256 matches 22 entries; `docs/metadata/main.md` has the same byte size but a different provider digest, unresolved. No payloads were downloaded or hashes recomputed. The authors say the original ~9 TB continuous soundscapes are not shared in the prepared package. Documentation specifies British National Grid nestbox coordinates in `nestboxes.csv` and `main.csv`, and a study-perimeter file. Coordinate values were not inspected; treat them as potentially sensitive and keep public geography coarse. Confirm a distinct task, intended file/metadata scope, held-out-bird evaluation, compute and safe location minimization before use. |
| **Egyptian fruit-bat vocalization corpus** | About 293,000 short recordings, around 91,000 annotations, and context/interaction fields derived from synchronized video. This is the closest reviewed large corpus for context association. | The recordings were made in a controlled colony setup with specialist ultrasonic microphones. The current Talk2Nature identity/file grouping audit connects about 95% of records into one component, so a strict held-out-group test is not currently supported. Recheck exact data-component terms and the proposed estimand with reviewers. |
| **ZF-AIM zebra-finch release** | A large, controlled vocal-interaction resource with code/checkpoints and metadata for next-call prediction. Relevant to vocal contingency and turn-taking questions. | It is a 2026 preprint/release; the repository catalog records conflicting dataset-rights declarations, uncertain coverage of the analyzed corpus, and no verified bird-independent split. Prediction of a next call is not decoding its meaning. |
| **El Silencio / BirdCLEF+ 2025** | 770 one-minute soundscapes from seven sites, with roughly 15,000 strongly labeled boxes across four taxonomic groups. Useful for multi-taxon event identification, annotation and soundscape pipeline work. | Labels identify calls/sonotypes, not observed behavior or receiver response. The Zenodo dataset record currently has no displayed license, so keep it metadata-only until component rights are resolved. |
| **Household budgerigars** | A practical candidate for a future passive, human-guided Field Companion workflow if carers and an avian researcher are available. | No reviewed large public household dataset supplies the needed phone recordings plus independently observed context. Do not recruit, collect or upload real observations without protocol, consent, rights, privacy, retention and withdrawal review. |

Counts above describe the source records, not independent sample sizes for every proposed analysis. Files, clips, notes, annotations and animals are different units. Random clip splits can leak bird, household, session, device or site identity; a large record count does not cure that problem.

## Household companion-data check (October 24, 2026)

The reviewed cat, dog and parrot materials sharpen the household decision but do not replace it. [CatMeows](https://zenodo.org/records/4008297) describes 440 sounds from 21 cats and includes context plus cat, owner and session identifiers. Its CC BY-NC 4.0 declaration is not general commercial permission, its contexts are elicited, and the files remain unacquired. The full [dog-bark study](https://aclanthology.org/2024.lrec-main.1432/) reports 16,789 segments from 74 dogs during designed home exposures; the selected classifier associates sound with those induced situations, and the paper describes data access by request rather than a public versioned deposit. Its dog-held-out split does not establish household-, session- or stimulus-independent generalization. The two reviewed [parrot surveys](https://www.nature.com/articles/s41598-022-24335-x) and [2026 name-use study](https://doi.org/10.1371/journal.pone.0346830) provide caregiver-reported phrase/context examples, not a natural-call audio corpus or an independent receiver-response benchmark. Their supporting workbooks have not been inspected.

The [budgerigar Dryad deposit](https://doi.org/10.5061/dryad.fttdz08xr) contains derived call features and separately recorded social observations, but no source call WAVs or shared event timestamps. A separate [2026 edge-monitoring paper](https://doi.org/10.3390/ani16203246) reports year-long vocal-activity monitoring of ten budgerigars; only the publisher abstract was reviewed, and activity detection is not context, caller identity or communication meaning. None of these records establishes that one species is the best scientific or product cohort. Keep budgerigars as a provisional household-usability hypothesis only; keep dataset-based benchmark selection separate and gated by the review packet. The source-linked research-library synthesis is live at [Which companion animal is ready for a first study?](https://metivity.github.io/talk2nature/research/companion-animal-cohort-evidence-2026/) and is linked from the first-animal guide.

## What “start learning” should mean

If Raviv wants one bird and one large corpus to explore first, the current provisional choice is **Great Tit song structure with Wytham**, not because great tits are known to be “more communicative,” but because the prepared corpus has dense song and individual annotations for a bounded methods exercise. This is a prepared-song methods path, not a raw continuous-soundscape reproduction: the authors say the original ~9 TB soundscapes are not shared. The OSF node declares CC BY 4.0 for the dataset record and the setup-code repository separately declares MIT; this does not clear nested provenance, precise wildlife locations, or separate 2025 analysis assets. The complete root inventory has 23 files (14 data and nine docs); the earlier 14-entry same-day snapshot was partial. Paths and sizes match the prior snapshot after normalizing leading slashes; one provider digest differs for `docs/metadata/main.md` at the same byte size. Before any analysis, an independent reviewer should identify a question that improves on existing repertoire/culture studies; define the exact files and fields to use; exclude precise nestbox coordinates and review derived identifiers; and approve a held-out-bird evaluation with suitable baselines. No payloads or coordinate values were inspected.

If the goal is a closer link to social context, **bats are the stronger biological-data lead**, but the current grouping audit means the first decision is to resolve the estimand and split, not to train a model. If the goal is to build an app that carers may use, **budgerigars remain the practical cohort hypothesis**, subject to real access and the safeguards above.

## Next gate

1. Use the [consolidated no-data review packet](FIRST_DATASET_REVIEW_PACKET.md) to keep the methods, communication-adjacent and app-cohort questions separate.
2. Ask an avian/bioacoustics reviewer to select or reject the biological question and label unit; ask a separate ML/statistical reviewer to check grouping, leakage, baselines and metrics.
3. Record component-specific rights and intended use for selected inputs; for Wytham, the OSF node declares CC BY 4.0 and setup code is separately MIT, while nested provenance, wildlife-location handling and exact analysis-file scope remain open.
4. Only if those checks pass, freeze the protocol, versioned inputs, grouped split and locked test before a bounded baseline run.

Until then, continue metadata/rights review and synthetic software checks. No outreach is implied by this internal brief; external contact needs action-time authorization. The benchmark remains **NOT READY**.

## Sources

- [Wytham Great Tit Song Dataset and documentation](https://nilomr.github.io/great-tit-hits/)
- [Merino Recalde et al. 2024, dataset article](https://doi.org/10.1016/j.anbehav.2024.02.008) · [OSF data record](https://osf.io/n8ac9/)
- [Prat et al. 2017, Egyptian fruit-bat dataset paper](https://doi.org/10.1038/sdata.2017.143)
- [ZF-AIM Zenodo release](https://doi.org/10.5281/zenodo.23024019) · [related bioRxiv preprint](https://doi.org/10.64898/2026.02.12.705387)
- [El Silencio dataset record](https://doi.org/10.5281/zenodo.17064353) · [BirdCLEF+ 2025 overview](https://ceur-ws.org/Vol-4038/paper_232.pdf)

The candidate review depths, rights findings and current split audits are detailed in [`FIRST_ANIMAL_PLAN.md`](FIRST_ANIMAL_PLAN.md), [`BENCHMARK_CANDIDATE_RUN_CARD.md`](BENCHMARK_CANDIDATE_RUN_CARD.md), [`EXECUTION_BOARD.md`](EXECUTION_BOARD.md) and the catalog under `research/resources.json`. This brief does not claim to replace those record-level reviews.
