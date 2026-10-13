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

## October 11 update: animal2vec / MeerKAT is a rare-event reference

The 2026 peer-reviewed paper reports 1,068 hours of meerkat audio and 184 hours of complete event labels, and evaluates event/call-category prediction with precision–recall metrics. This is useful for detector design and for understanding sparse, noisy, multi-label audio. It does not answer the project's first acoustic-context question: the labels are sound/event categories, and the focal tag is source attribution based partly on intensity, spectral change and context, not a communication-meaning label.

Treat the components separately: the paper links the MeerKAT dataset and checkpoints under CC BY-NC 4.0 and animal2vec code under MIT. The dataset and weights remain outside the shared commercial-capable corpus. The sample-level five-fold design was not verified as animal/session grouped; randomized filenames intentionally conceal identity and chronology, which the authors say may be requested. No data, code or weights were acquired or executed. The evidence note and `research/resources.json` preserve separate versions, rights and review limits. AutoResearch remains **NOT READY**.

## Resume gate and first executable milestone

1. Audit source/package provenance and any available recordings separately; select one species and one observable target with a scientific collaborator. Confirm whether the work concerns natural calls or a learned interface.
2. Document original recording rights, human consent where applicable, individuals, sessions, devices/sites, observation provenance and annotation agreement. Check near duplicates and possible pretraining overlap. Decide what can be published separately from what can be analyzed.
3. Freeze the model artifact and dependency environment; record artifact checksums and measured runtime on a small permitted sample. Verify preprocessing and align every crop with observation timestamps.
4. Use the existing manifest validator; additionally hold out relevant sites/devices/time where needed. If groups or class coverage cannot support the chosen evaluation, revise the question or gather appropriate data before reporting accuracy.
5. Predefine metrics, background controls, cluster-aware uncertainty, calibration and abstention. Report failure cases and all prespecified comparisons. A predictive association alone does not establish meaning or two-way communication.

Until these inputs exist, more model integration would commit the project to an untested task. The current code milestone remains the tested metadata/split foundation.

## October 9 update: agent-assisted research

Karpathy's AutoResearch is a useful model for a tightly scoped experiment loop, but its GPT pretraining code and validation bits-per-byte objective do not fit Talk2Nature's current research state. No model training was run or enabled. The project adopted a controlled, future-facing agent program with pre-run data/rights/label/split/baseline gates and a locked final test set. See [`AUTORESEARCH_ADAPTATION.md`](AUTORESEARCH_ADAPTATION.md); the runnable status remains **not ready**.

## October 11 update: MammAlps is a comparator, not the first project dataset

The MammAlps v3 camera-trap release provides synchronized animal audio/video and video-annotated behavior across five wild mammal species. It is useful for designing modality ablations and explicit unknown labels, but its dataset license is CC BY-NC 4.0, its published split is day-level rather than verified animal-level, and the review did not establish annotator agreement or audio blinding. The 87.9 GB archive, one-park/short-season scope and reported A100 training setup also make it a poor first fit for Talk2Nature's current commercial-capable, bounded baseline. No files or code were acquired or run. The candidate is now documented in `research/resources.json`; the full fit and review limits are in the linked MammAlps evidence note and `docs/COLLECTION.md`. No reviewed dataset is admitted, and AutoResearch remains **NOT READY**.

## October 11 update: parrotlet vocal-babbling archive

The Dryad record lists 2.60 GB of audio-video-derived developmental material for wild green-rumped parrotlet nestlings, including spectrographic measurements and metadata. Its 2017–2018 study included corticosterone supplementation. It may inform a future parrot vocal-development question, but the reviewed material does not establish the annotation schema, independent behavior labels, individual/session groups, audio-video synchronization or a safe grouped evaluation. The paper describes the babbling repertoire as not yet integrated into functional contexts; it does not demonstrate semantic decoding. Dryad's current terms state CC0 by default unless a different term was indicated during submission, but no item-specific exception was surfaced in this review. The exact item terms therefore remain unresolved. The archive remains metadata-only; no data were downloaded. It is not admitted to the current context benchmark or AutoResearch. See the dated evidence note and `docs/COLLECTION.md` for source limits.

## October 11 update: Prompting-MammAlps video retrieval

The separate 2026 Prompting-MammAlps release retrieves camera-trap videos from text queries over explicit visible-behavior labels. It does not test acoustic context or animal meaning. The data are CC BY-NC 4.0, the code repository has no declared license and the reported SALMA checkpoints were not located. Its day-level split does not establish held-out-animal generalization, and the headline scores use different query subsets. Keep the dataset metadata-only and outside the commercial-capable benchmark; do not acquire or run the unlicensed code. It is a design reference for separating query, label and retrieval evaluation only.

## October 12 update: Earth Species bat notebooks are not the EUSIPCO reproduction

Reviewed the four Egyptian-fruit-bat notebooks at [Earth Species Library commit `6382c52`](https://github.com/earthspecies/library/tree/6382c52bf553569528e0a790efe16e5ae42f0094/egyptian_fruit_bat), dated June 28, 2021. The 2021 snapshot predates the 2024 EUSIPCO paper. Its preprocessing notebook `99a` says `FileInfo.csv` maps annotation `FileID` values to source filenames; it also says a suitable train/validation split is unclear and creates no such split. Notebook `02` instead defines an emitter/speaker-identification task using the first second of audio and a shuffled, stratified five-fold split over annotation rows, taking fold zero. Notebook `99b` forms a smaller 10-emitter × 1,000-call subset and retains emitter identity rather than context. These are useful access/preprocessing examples, not the EUSIPCO context model or its three subject-independent folds.

Rights remain unresolved by component. Notebook `99a` declares the dataset CC BY 4.0 but its code license “to be linked”; the visible root inventory at the pinned commit has no `LICENSE` file. The notebook's broad dataset statement does not replace the direct, item-level Figshare records already cataloged for the 2017 archive and its components. The `99a` historical output reports a 30.1 MB `FileInfo.csv` download through Figshare file ID `8900695`; Talk2Nature has not verified whether that identifier is the same artifact as its separately cataloged 31.6 MB Figshare item. Nothing was downloaded or executed. Therefore, the notebook establishes a dependency for that specific preprocessing route, but not for reconstructing EUSIPCO's missing splits. Keep the candidate metadata-only, preserve the 5 MiB collector cap, and seek independent bat-bioacoustics review before deciding whether a bounded FileInfo integrity plan is justified. AutoResearch remains **NOT READY**.

## October 11 update: Egyptian fruit-bat context candidate

The 2017 archive is unusually relevant for research design because it pairs audio with video-derived context labels and reports a sampled annotation quality check. Published context accuracies from 2016 and 2023 are acoustic associations with observer-coded context; the studies do not establish receiver comprehension or general translation. Their vocalization/sequence folds do not demonstrate held-out-animal performance, so they are not a ready Talk2Nature benchmark.

Keep the Figshare archive metadata-only until its direct raw-file terms are verified. The 2017 article's CC0 waiver applies to metadata, while NLM's CC0 notice for item 4556074 is secondary evidence. Mendeley Data v3 separately declares CC BY 4.0, but exact file contents and upstream audio provenance need review before acquisition. No files or code were downloaded or run. AutoResearch remains **NOT READY**; any later pilot must freeze deduplication, animal/session-grouped splits, independent labels, simple controls and a locked test before execution.

## October 12 follow-up: public data-preparation code is not the paper's verified split release

The official EUSIPCO paper says its code and subject-independent partitions would be released upon acceptance. A fresh check of the first author's linked public GitHub account found 13 listed repositories but no visibly matching paper repository; this is a bounded negative search, not proof that a release does not exist in a coauthor, lab, archive or unindexed location. Separately, the Earth Species Library's Egyptian-fruit-bat folder lists dataset download, preprocessing and PyTorch data-loader notebooks, and its overview mentions a pretrained ResNet context-prediction example. It describes a 91,080-record unbalanced set and a 10,000-record balanced subset. The reviewed material does not establish that this is the EUSIPCO authors' code or contains their exact folds. The current Talk2Nature resource record therefore treats it as a discovery/preprocessing lead only. Repository code license, archive-copy provenance, item-level dataset terms and model-weight rights remain unresolved; no notebook, archive, code or weights were acquired or executed. Do not treat the resource as a reproduction or request/download large archives until provenance and terms are verified.

## October 12 update: source separation is an upstream audio question

Bermant's BioCPPNet paper is a useful cross-species methods reference for one narrow stage: separating overlapping vocalizations into estimated source waveforms before downstream analysis. Its study creates mixtures from known animal vocalizations and reports SI-SDR plus a caller-identity classifier for macaques, bottlenose dolphins and Egyptian fruit bats. The reported bat test includes an open-speaker condition with three held-out individuals, but this does not establish performance on uncontrolled phone or field recordings.

This method does not predict interaction context or decode communication. In a future pipeline, keep detection, source separation, caller attribution, observable context and receiver-response experiments as separate tasks with separate labels and evaluations. Do not present a cleaned or separated signal as a translated animal utterance.

The article page states CC BY 4.0 for the article; the linked code repository's visible root inventory at reviewed commit 7092851cbd9a32116e6453583823d5334ab11f1b has no LICENSE file. The article separately identifies public macaque and Egyptian-fruit-bat data and restricted dolphin recordings. No code, audio, generated mixtures or weights were acquired or run. Keep each component metadata-only until rights and fit are verified. See content/research.json, content/sources.json and research/resources.json. AutoResearch remains NOT READY.

## October 12 update: bat identity structure is observable; the paper split is not

The small Figshare Metadata.pdf item was reviewed locally. It records 20 date-bounded treatment periods with group composition and channels, subject/maternal fields, and the annotation columns. The separate 91,080-row Annotations.csv item already has a receipt-verified aggregate audit. A new participant-pair graph covers the entire annotation item: 48 IDs across both role fields, 70,001 rows with two identified participants, 136 distinct pairs, three connected components (largest 31 IDs), and 13 known IDs without a pair edge. Negative IDs preserve a known individual with role uncertainty; zero is unknown. Raw values are omitted from `research/figshare_bat_annotation_report.json`.

These counts do not describe the paper’s filtered 35,074 records or verify its reported folds. The paper’s exact partitions remain unavailable, and the necessary file/time/channel metadata is in a separate 31.6 MB `FileInfo.csv` item with `md5=null`, above the project’s 5 MiB acquisition cap. Do not train or increase the cap. First obtain qualified bat-bioacoustics review on whether all interacting individuals, treatments, sessions, channels and chamber periods must be grouped; only then prepare a bounded integrity plan if FileInfo is necessary. AutoResearch remains **NOT READY**.


## October 12 follow-up — NatureLM-audio and its component rights

The public `naturelm` evidence note now covers the ICLR 2025 paper, current official task limits, the large training/evaluation dataset cards, and a NeurIPS 2025 workshop follow-up on prompt brittleness and model merging. NatureLM-audio is a useful reference for audio-plus-instruction classification and captions, not a translation system. The workshop paper’s reported >200% relative gain is a narrow 425-example, 40-class closed-set unseen-family result; it is not a general communication result or a Talk2Nature reproduction.

The new resource records keep eight components separate: article, code, weights, training dataset, BEANS-Zero data and code, and the follow-up paper and code. NatureLM weights are labeled CC BY-NC-SA 4.0 with Llama 3.1 terms also applicable; the 26.4M-row training card and 50.5 GB BEANS-Zero card use a generic `other` license label, and the training viewer exposes varying row-level license values. The original model code and merging implementation have MIT license files, while the BEANS-Zero evaluation repository had no LICENSE at the checked root URL. None of these data, weights or code artifacts were downloaded or run.

Decision: do not add this foundation model to the public phone workflow or paid product. Keep it as a metadata-only research comparator. The initial benchmark remains a small, independently labeled question with a frozen split and simple baselines; revisit NatureLM only after qualified review, rights resolution and exact-version/compute planning. AutoResearch remains **NOT READY**.

## October 13 follow-up — BEANS-Zero as a comparator, not a communication benchmark

The pinned dataset card reports 91,965 examples in a single test split and a license field per sample. It says the composite is not intended for commercial use; its Hub-level license remains `other`. The live file tree lists 50.5 GB, while the pinned companion code README estimates about 100 GB for full non-streaming download. Keep this size discrepancy unresolved until the provider reconciles it. At pinned code commit `31d4487ee6452ae6c31853d45fd38b7d4150372d`, the root inventory has no LICENSE and `pyproject.toml` declares no license; do not reuse the evaluator absent explicit permission.

The benchmark is a useful cross-taxon reference for classification, detection, call type, life stage and captioning, but does not test interaction context or receiver comprehension. Keep the data and code metadata-only. A first Talk2Nature benchmark still needs a narrow behavior-linked question, permitted data, qualified review, independent labels, grouped/frozen evaluation, baselines and locked test data. Sources 245–246 and the updated `naturelm` note record the review. AutoResearch remains **NOT READY**.
