# Candidate run card: bird detection or parrot identity?

**Status: review proposal only. No data acquisition, model execution, or AutoResearch run is approved.** This card compares two distinct research exercises; it does not claim they measure the same task.

## Decision

Do not treat either candidate as a first animal-communication benchmark. CEB can support a narrow bird sound-event detection reproduction and help validate research software. The monk-parakeet work is a closer communication-science comparator, but its published analysis concerns acoustic identity/convergence and does not test listener comprehension or call meaning. The project's behavior-context question still needs a rights-cleared dataset with independently observed, time-linked behavior and suitable animal-held-out evaluation.

If the independent scientific reviewer endorses a small engineering exercise, **CEB soundscape detection is the better candidate to assess first**: the soundscape component has a clear dataset-level CC BY 4.0 declaration and strong event labels in the published evaluation subset. This is a provisional engineering recommendation, not a claim that its data, split or baseline are ready. Keep the parrot study as a separate method-reproduction candidate.

## Candidate A — CEB sound-event detection

**Question.** On Central European bird soundscapes, can a frozen detection pipeline locate labeled vocal events and identify their annotated species better than a simple non-neural baseline when the evaluation recordings are held out by acquisition group?

**Exact release and rights.** Central European Birds, Zenodo v1.1, DOI [10.5281/zenodo.21821133](https://zenodo.org/records/21821133). The complete record is 49.7 GB. The `train_soundscape` archive is 46.5 GB and has 18,469 files / 62,298 annotations; its labels are point-centered with a fixed ±2.5-second window and many lack a vocalization-type label. The `test_soundscape` archive is 489.8 MB and has 147 recordings / 15,064 strongly labeled events. Soundscape audio and dataset annotations/metadata are declared CC BY 4.0. Exclude `train_xenocanto` from a first pass: each focal recording keeps its own Xeno-Canto terms, and some license entries are blank. Attribute the dataset and retain its provenance if any permitted files are later used.

**What the labels establish.** They support annotated sound-event presence, species and vocalization categories. They do not provide independently observed social behavior, receiver response, or a ground truth for what a call communicates. The source record identifies 40 zero-area annotations and a truncated focal recording; resolve the zero-area rows for any localization analysis and exclude the focal subset from this initial soundscape-only plan.

**Grouping and evaluation proposal.** Use soundscape recordings only. Before selecting rows, inspect the licensed metadata table and establish what its anonymized `project` identifiers represent. The minimum group is the full source recording; keep all clips from one source project/acquisition together across partitions. A project label is only a proxy until a reviewer confirms the recording/site/device structure and checks overlap between the publisher's train and test subsets. The public `test_soundscape` labels are downloadable, so this set is not a private or durable secret holdout. It could be used for a one-time evaluation only if a named independent custodian verifies that the evaluation team has not inspected the labels, preserves the exact release/fingerprint and opens them once after the analysis is frozen. Otherwise treat it as development data and obtain an independent held-out set. Stop if the grouping keys cannot support the intended generalization claim.

**Baseline and measures.** Start with a prevalence/no-skill baseline and a simple log-mel feature classifier. A pretrained model is optional only after the exact binary, training-data overlap and model license are reviewed; do not assume the model-card license clears its inputs. Candidate primary measures are class-macro average precision for event detection and class-macro event F1 with thresholds chosen on validation only. For localization, report time-frequency intersection-over-union and event recall at reviewer-approved matching rules. Estimate uncertainty by resampling independent project/recording groups, not individual calls. Report per-species coverage and false positives per recorded minute; do not collapse these into a translation score.

**Proposed resource ceiling.** If approved, CPU only, no cloud or GPU, at most 2 GB of selected soundscape media, 4 CPU-hours, 8 GB RAM and 5 GB scratch space. The proposed acquisition limit is a planning cap, not proof that a statistically useful sample fits. If the group/label audit shows that it does not, stop and revise the design before acquiring audio.

## Candidate B — monk-parakeet acoustic identity reproduction

**Question.** Can we reproduce the published comparison of acoustic similarity at the individual and site scales from the exact deposited calls and analysis version?

**Exact release and rights.** The associated paper is Smith-Vidaurre et al. (2023), [PLOS Computational Biology](https://doi.org/10.1371/journal.pcbi.1011231). The linked dataset is Figshare v2, DOI [10.6084/m9.figshare.22582099.v2](https://figshare.com/articles/dataset/Smith-Vidaurre_et_al_2023_IdentityInformationEncoding/22582099), whose item metadata declares CC BY 4.0 and lists 22 files totaling 187,820,138 bytes. The article's CC BY notice, data item's license, analysis repository's GitHub MIT notice and linked Zenodo archive's `other-open` license field are separate. Audio-to-selection provenance and per-file rights have not been audited, and the archive has not been acquired. Keep this candidate metadata-only until those exact assets and scopes are reconciled.

**What the paper reports.** Its random forest was trained on 156 contact calls from eight known individuals. The reported 97.44% accuracy is training accuracy. The other 73 calls from nine individuals were used to derive similarity/proximity patterns and clustering, not to report held-out caller-classification accuracy. The paper combines acoustic-similarity methods and compares individual- and site-scale convergence; this is not an unseen-caller translation result.

**Reproduction and split proposal.** First reproduce the paper's stated similarity/convergence analysis, retaining its declared individual/site units and resampling procedure. The exact feature files, audio links, identities, exclusions and code/data version correspondence must be verified before fixing any partition. Do not invent a random call-level split. A new same/different-individual classifier would be a separate question: all calls from an individual must stay on one side of the split, with adequate repeated calls per held-out individual; the current reviewed evidence does not establish that this condition is met.

**Baseline and measures.** For a paper reproduction, match the published SPCC and random-forest-proximity analyses, then compare within- versus between-individual/site similarity using the paper's Earth Mover's Distance and its reported bootstrap approach. Include a simple chance/reference analysis, preserve individual/site as the resampling units and report every deviation. Do not reinterpret the original training accuracy as a held-out score. A new predictive task needs a separately specified baseline and metric after the data audit and reviewer decision.

**Proposed resource ceiling.** If rights and code scope are cleared, CPU only, no cloud or GPU, at most 2 CPU-hours, 8 GB RAM and 5 GB scratch space. This cap is provisional and cannot override a data/rights or scientific stop condition.

## Shared readiness gates

No run begins until all applicable gates have evidence:

1. An independent avian-bioacoustics reviewer and a statistical/ML evaluation reviewer approve the exact question, sampling unit and claim boundary. For the parrot candidate, reviewer experience should include parrot vocal behavior or the specific convergence method.
2. The exact versioned files, source checksums, item/file terms, attribution, privacy, retention and permitted-use scope are documented. Dataset, paper, code, dependencies and model weights remain separate assets.
3. The annotation guide, missingness, source provenance and any reliability evidence are reviewed. A model prediction is never used to create its own evaluation label.
4. The acquisition groups and near-duplicate/source-overlap risks are reviewed. Train/validation/test memberships are frozen and hashed before tuning; test access is controlled and logged. If no defensible independent holdout exists, the result is labeled a reproduction or exploratory analysis, not a benchmark.
5. A baseline, primary/secondary metrics, uncertainty procedure, seed schedule, compute cap, success/stop criteria and report template are registered before any model choice.
6. A local-only environment is reviewed for bounded data access, no credentials, no upload path and no animal playback. Preserve all failures and discarded trials if a later run is approved.

**Reviewer needed:** an independent avian bioacoustics researcher with passive-acoustic evaluation experience; add a parrot vocal-communication specialist for Candidate B. No reviewer is currently assigned and no outreach has been sent.

**Current result:** none. No CEB or parrot media were acquired, no model or paper analysis was executed, no independent reproduction occurred, and AutoResearch remains **NOT READY**. The next safe action is a metadata/grouping review of the CEB soundscape tables under their stated CC BY terms, followed by independent review of whether the resulting group structure supports this limited detection exercise. This card does not authorize that acquisition or any model run.

## Sources and project records

- [CEB v1.1 official record](https://zenodo.org/records/21821133) and [Talk2Nature's metadata-only CEB assessment](https://metivity.github.io/talk2nature/research/central-european-birds-dataset-v1-1/).
- [Monk-parakeet paper](https://doi.org/10.1371/journal.pcbi.1011231), [Figshare v2 dataset](https://doi.org/10.6084/m9.figshare.22582099.v2), and [pinned GitHub analysis release](https://github.com/gsvidaurre/identity-information-post-introduction/tree/v1.0.0).
- [Talk2Nature AutoResearch readiness protocol](AUTORESEARCH_ADAPTATION.md), [current model/data decision](MODEL_DATA_DECISION.md), and [collection/rights log](COLLECTION.md).
