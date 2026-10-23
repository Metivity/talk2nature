# Many animals; one first study

Decision record, October 3, 2026. Talk2Nature / Metivity/talk2nature. This is our proposed research design, not specialist advice, recruitment, a power analysis or an approved experiment.

## Recommendation

Build a general observation app. Start the first scientific feasibility study with **one species of companion parrot**, provisionally **budgerigars**, if several independent households and a qualified avian researcher are available. Actual access is not yet confirmed. Cockatiels are a reasonable alternative if that is the existing community; do not mix them with budgerigars to enlarge the sample. African greys are a separate possible cohort, not automatically the best choice because they mimic human words. Dogs are the fallback if reliable parrot access cannot be arranged.

This is an operational recommendation, not a demonstrated ranking of animal intelligence or scientific promise. No new animal should be acquired, isolated or provoked for this project. Existing carers, ordinary routines and voluntary participation are the intended setting.

### October 23 clarification: two different starting choices

The October 3 recommendation concerns a possible **phone-based companion-animal feasibility cohort**. It does not select the first ML benchmark. Keep the tracks tied to their questions: Egyptian-fruit-bat context prediction is a research question to review, but the current file-plus-emitter grouping audit has a 95.31% largest component and the file-plus-all-known-participant grouping has a 95.56% largest component; neither currently supports a balanced strict held-out-group test at that annotation granularity. Do not describe this as a viable first benchmark unless independent bat-behavior and ML/statistical reviewers approve a different defensible estimand. V33DA and its V33DA++ companion are metadata-only methods candidates for caller attribution, overlap handling and vocal-activity detection; the companion adds overlap and plus/minus two-second context buckets but uses the same ten zebra finches. The pinned trainer/split snapshot remains incomplete, and neither release labels receiver behavior or call meaning. The 2026 ZF-AIM preprint is a high-relevance lead on vocal turn-taking whose data rights remain unresolved. Bat recordings require specialized ultrasonic equipment; zebra-finch releases come from controlled research setups. Neither is a phone cohort. Budgerigars remain a provisional household-app cohort only if real access, an avian reviewer and the required participant/data safeguards are established. No track authorizes recruitment, new data collection, model training or animal playback.

**Device prior art, checked October 23:** Agishev et al. (2026) report a Raspberry Pi-based system that locally monitored vocal activity from ten budgerigars for a year using YAMNet features and a task-specific classifier. The current review is abstract-only; detailed validation, data and code access remain unverified. This means Talk2Nature should not claim that a dedicated listening device or local vocal-activity counter is itself novel. The project still needs to demonstrate a distinct, useful workflow—such as understandable human-entered context and review—without treating activity patterns as messages. See the [source-limited evidence note](https://metivity.github.io/talk2nature/research/budgerigar-edge-vocal-activity-monitoring-2026/).

The [Wytham Great Tit Song Dataset](https://metivity.github.io/talk2nature/research/wytham-great-tit-song-structure-2024/) is a separate **song-structure** resource, not a replacement for the bat context-prediction candidate or the parrot app cohort. Its large, annotated single-population corpus can support questions about note boundaries, song sequences and repertoire variation. It has no independently observed interaction-context or receiver-response labels, so it cannot establish what a call means. A 2025 paper has already used the corpus to study demographic drivers of song culture; any Talk2Nature analysis must identify a useful extension before it is presented as new.

### October 23 update: choose the dataset by the scientific question

| Research question | Candidate and what its labels support | Current decision |
| --- | --- | --- |
| How do song units, sequences and repertoires vary across a known wild population? | [Wytham Great Tit Song Dataset](https://nilomr.github.io/great-tit-hits/): 109,963 annotated songs and more than 1.16 million acoustic units from more than 400 individual birds in one U.K. population. | A strong song-structure/culture resource, not an independently labeled behavior or communication-meaning set. The paper reports CC BY 4.0 for data files and the separate setup repository declares MIT; exact OSF inventory and identity/location sensitivity remain unreviewed. Do not duplicate the published 2025 demographic analysis. |
| Which visible bird produced an already-detected call? | [V33DA](https://huggingface.co/datasets/songbirdini/v33da): 33,625 physically verified events from 10 zebra finches, with audio, video, pose and caller labels; one aviary and no overlapping calls in the main benchmark. | Best bounded candidate for a caller-attribution methods exercise, not meaning. Dataset and included 100-event sample declare CC BY 4.0; software is separately MIT. Keep metadata-only until an exact sample/intake and split plan is approved. |
| Can software find bird calls and species in field soundscapes? | The [Northeastern forest-bird release](https://zenodo.org/records/20038954) has 1,302 ten-minute recordings and about 183,000 annotations. | A field detection/localization reference, not a communication dataset. Checksum-verified metadata confirms 104 sites in both site and recording tables; park counts are 31/24/24/25, while the landing-page summary lists KAWW as 20. The README/paper say 88 bird species; the species table has 96 `IsBird=Yes` rows and 182,633 annotations, so that discrepancy remains unresolved. A four-file metadata sample is local only; no audio or annotation rows were acquired. CC BY 4.0 is declared by the v2 record; site-holdout quality is unreviewed. |
| How are vocal exchanges timed and adapted? | [ZF-AIM preprint](https://doi.org/10.64898/2026.02.12.705387) reports over 1,000 hours of zebra-finch interactions and experiments with an AI-driven acoustic interaction model; the [26.6 GB Zenodo bundle](https://zenodo.org/records/23024019) is described as code, checkpoints and next-call metadata. | Most directly relevant new research lead for exchange structure, but only the abstract and record metadata were reviewed; the data/recording license is unclear. Preprint, not an established Talk2Nature result. No acquisition or playback. |
| Does a call predict independently observed social context? | The Egyptian-fruit-bat record has video-derived context labels and a reported subject-independent evaluation; it is a distinct ultrasonic research task. | Current leading communication-adjacent benchmark question, pending source joins, group-boundary review and outside specialists. |
| Can a phone workflow support companion-animal observation? | A single parrot household or Kiki could inform usability; existing monk-parakeet data mainly address vocal identity, not ordinary home behavior labels. | Keep parrots as the provisional product-discovery path. One household cannot establish species-wide behavior or call meaning. |

There is no single “largest dataset” that answers all four questions. Broad soundscape collections such as [El Silencio](https://zenodo.org/records/17064353) are useful for event/species detection, but their labels do not by themselves reveal social meaning. Start with existing, rights-described data to test a narrow task; do not train a general-purpose animal-language model on a pile of recordings. Use audio models for segmentation and acoustic patterns, then add video/pose or observer-coded context only where the labels support it. Evaluate on held-out animals, households, groups or sessions, and keep predictions separate from observed labels.

**Recommended sequence:** For a first transparent, population-scale audio methods exercise, prioritize a bounded Great Tit song-structure task, after confirming the exact OSF files, terms and location/privacy scope and checking for a useful extension beyond the published demographic analysis. Its many identified birds make it more informative for between-individual generalization than V33DA's ten-bird cohort, but its labels do not test interaction meaning. In parallel, prioritize a full methods, manifest and component-rights review of the zebra-finch ZF-AIM release because it is more directly about vocal exchange and turn-taking; do not acquire its 26.6 GB archive or train from it until those gates pass. Keep V33DA++ as a separate overlap/activity engineering candidate: it adds labeled overlap/context cases but the same ten birds, is listed at 167 GB, and its pinned training/split code is incomplete. Keep Kiki and any parrot app work in the product/usability lane, not as a substitute benchmark. This is a proposed order of work, not authorization to acquire data, train models, recruit participants or play sounds to animals.

The bounded V33DA intake and caller-attribution proposal is documented in the [V33DA sample run card](V33DA_SAMPLE_RUN_CARD.md). It remains metadata-only and authorizes no acquisition or model run.

## Comparison

| Candidate | Practical opportunity | Main obstacle | Decision |
| --- | --- | --- | --- |
| Budgerigars | A species-specific contact-call research and data starting point [1,2]; repeated observation with existing carers is a proposed route. | Multiple callers, mimicry, small movements, household/device confounding; access unconfirmed. | Provisional lead, subject to feasibility. |
| Cockatiels | A possible existing-carer cohort; compare access directly with budgerigars. | We have not yet reviewed a matched reusable context dataset. | Alternative within the parrot track, never pooled by default. |
| African greys | Relevant to the learned-human-sound branch; survey evidence highlights species differences [3]. | Human-word imitation invites stronger meaning claims than the evidence warrants. | Separate future cohort if accessible. |
| Dogs | Existing bark-classification work and grouped-animal evaluation provide a baseline [4]. | Context, household sound and owner behavior can provide shortcuts; naturally occurring events may be uneven. | Strong fallback; distinct codebook. |
| Cats | A small identified dataset documents context and individual/session fields [5]. | Non-commercial terms; elicited-context data are not a passive home protocol. | Useful comparison, not immediate dataset integration. |
| Farm animals | Soundwel offers a separately licensed research starting point [6]. | Farm access, recording conditions and context definitions require specialist work. | Partner-led track later. |
| Frogs and other wild animals | AnuraSet illustrates mixed callers and ecological identification [7]. | Individual identity and independently observed behavior may be difficult to establish. | Monitoring track separate from a companion communication pilot. |
| Bats and marine mammals | Existing library records show valuable science. | Specialized sensing and access make them a poor match for an ordinary-phone first pilot. | Literature and partner-led work. |

Owner popularity is a recruitment hypothesis, not a counted local participant pool. A signed-up, suitable cohort matters more than worldwide pet numbers. The 2022 parrot survey demonstrates community participation but also reports biases; it does not establish Talk2Nature's recruitment reach [3].

## First useful question

Can sound add information about a small, independently observed behavior category on a new animal or household, beyond what background sound, device and setting already reveal?

First test **annotation feasibility**, not translation. Define two or three visible categories with an avian specialist, such as moving between perches, feeding already underway and stationary observation. Permit “not visible,” “overlap,” “uncertain caller” and “other”; never infer hunger, happiness or a reply from a sound. Retain the distinction between natural vocalization, human-word imitation, actual human speech and environmental noise. Do not pre-label calls as questions or answers.

Proposed sequence:

1. Confirm access and species, scientific reviewer, consent scope, media rights and withdrawal plan. A planning target of 5–10 existing households is for feasibility only, not sufficient statistical power or an authorization to recruit.
2. Rehearse the local mobile workflow using invented tones. Test devices and the species codebook before collecting research media.
3. After protocol approval, inspect a small set of fixed-duration, ordinary-routine observations. Use independently reviewed video/context where authorized; the public app does not currently capture video. Human speech and faces require their own handling. Include quiet and uneventful windows, not only triggered clips.
4. Have two reviewers label behavior independently, ideally without audio when assigning visible context. Report agreement, disagreement, missing views, overlapping callers and usable duration. Do not force a training label when evidence is weak.
5. Predefine grouped splits by connected household, animal, device and session. For caller recognition, use a separate within-individual/later-session task and make no unseen-animal identity claim. Determine a larger sample and power/precision needs after the feasibility findings.
6. Compare a majority baseline, timing/context-only baseline, background-only baseline, simple acoustic features and one licensed frozen encoder plus a small classifier. Inspect pretrained-data overlap, calibration, class balance and abstention. Do not train a conversational LLM first.
7. Publish methods, exclusions and negative results with uncertainty. Only a later, welfare-reviewed receiver-response experiment could address a bounded meaning claim; automatic playback remains absent.

Proceed only if independent labels are usable, device recordings are suitable and the cohort supports the intended held-out claim. If caller attribution or label agreement fails, narrow the task to event detection, revise the protocol, or change the candidate species. More clips from one animal do not solve lack of independent animals.

## App and collection scope

Station and the sound notebook share 12 broad choices, including unknown and mixed scenes. A species label is optional and explicitly observer-declared. A session freezes its choice at start; the notebook can preserve and revise it on review. An animal group does not assign every sound in a scene to that animal. Fish, reptiles, invertebrates and other mammals are welcome as observations; the app does not claim suitable sensing or a trained model for all species.

This expansion adds 11 sources, five evidence notes and five reuse resources. Acquired material is a small pinned MIT AnuraSet code/documentation sample, retained outside Git; no new animal audio or household records were acquired. CatMeows remains outside commercial integration. AnuraSet audio/labels wait for the CC0 versus repository cc-by discrepancy to be resolved. Soundwel and budgerigar media wait for a bounded inventory/suitability review. Acquisition never opens the private synthetic-only gate.

A continuing research queue: cockatiel natural-call methods; parrots' non-mimicry behavior labels; dog household confounds; cat owner/session splits; farm-context generalization; invertebrate and fish sensor requirements. This is a focused initial survey, not all literature.

## Sources and review depth

1. [Zhao et al., budgerigar study](https://pubmed.ncbi.nlm.nih.gov/38070505/): primary abstract/highlights.
2. [Zhao data, version 1](https://data.mendeley.com/datasets/j8rpy4dc6c/1): deposit description/license, inventory and one pinned MAT structure inspected in the continuation; full methods pending.
3. [Benedict et al., companion-parrot survey](https://www.nature.com/articles/s41598-022-24335-x): selected results and collection methods.
4. [Abzaliev et al., dog bark study](https://aclanthology.org/2024.lrec-main.1432.pdf): abstract and experimental setup, including grouped folds.
5. [CatMeows 1.0.2](https://zenodo.org/records/4008297): record description, fields and API rights.
6. [Soundwel deposit](https://zenodo.org/records/8252482): description and API rights. Full study methods pending.
7. [AnuraSet paper](https://www.nature.com/articles/s41597-023-02666-2): data records and selected validation; [versioned deposit](https://zenodo.org/records/8342596) and [code](https://github.com/soundclim/anuraset).


## Continuation: practice before recruitment

See [PILOT_PROTOCOL_DRAFT.md](PILOT_PROTOCOL_DRAFT.md) for readiness gates and the candidate visible-behavior codebook. Whole moment mode now retains a 30-second audio window, including quiet samples, with explicit incomplete status on interruption. This reduces threshold selection within a window; observer-selected start times still bias sampling. No video capture or independent annotation interface is implemented.

One 1.49 MB licensed budgerigar container has now been acquired and inspected, superseding the earlier metadata-only state above. It contains 15 call structures and no explicit independent visible-behavior field. Stored `fs=44101`, caller/context linkage and intervention status need review. See [COLLECTION.md](COLLECTION.md) and the aggregate report. It is a structural starting point, not a home-context training set or scientific result.
