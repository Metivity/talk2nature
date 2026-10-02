# A simple field companion and a traceable research program

Raviv requested this goal on October 2, 2026. Project: Talk2Nature, independent initiative, Metivity/talk2nature. This is a multidisciplinary synthesis and engineering plan, not a consultation with an assembled expert panel. Funding applicant/legal entity remains unconfirmed.

## The decision

Build a useful observation companion first. Connect audio, independently recorded behavior and environmental context through an evidence graph. Start machine learning with one defined passive animal study. Keep plants and fungi as distinct research tracks with suitable instrumentation. The first success is reliable data and a reproducible, bounded result, not a fluent animal translation.

## This release

- A new homepage and shared visual system: original forest artwork, restrained glass, warm paper, large type, generous touch targets and visible scientific status. The generated image is labeled as illustration.
- Listen: open a sound, mark a moment, **Save notebook**. One `.t2n` file contains the exact WAV and observations. Opening it restores both. Identity fields, confidence, technical details, JSON and CSV stay behind disclosures. The download remains manual; the app cannot verify whether the operating system saved it. No hidden browser storage or uploads.
- Nature Station: automatic sound-level event capture already operates during a bounded, visible session. Save session is the main action; journal-only JSON is advanced. Its multi-clip ZIP remains distinct from a Listen notebook.
- Five new evidence notes, nine additional primary-source records, an updated moth note and a fifth reading path. The library now has 27 notes and 96 sources. Exact reading depth is shown; no full-literature or independent-expert-review claim.
- Public evidence map and a deterministic, versioned graph export. Private owner-only graph projects the existing authoritative database, preserving frozen reference versions and omitting withdrawn observations. No new database service or data duplication is needed.
- The competition email's public links are the homepage and `/tools/listen/`. Those URLs stay stable. Its GitHub link pins historical source revision `dddaf17f61df58ec6503ab5e20b21d44ed7995b5`, intentionally unchanged. Updating the website does not change the submitted source snapshot or establish eligibility/acceptance.

## Architecture: connect evidence without losing its origin

The existing stack remains GitHub Pages for public pages; FastAPI for private authorization/workflows; PostgreSQL for hosted metadata; separate private object storage for future media. Hosted runtime and media storage are not live. The new graph is a view of existing records rather than a competing graph database. At this scale, relational integrity and versioned edges are more valuable than running Neo4j alongside PostgreSQL. Add a dedicated graph engine only when measured traversal requirements justify its operational cost.

Implemented graph nodes: public source, evidence note, acquisition resource; private study, session, observation and metadata release. Edges are `cites`, `uses_frozen_evidence`, `follows_protocol`, `observed_in`, `contains`. A citation is not corroboration. Public source versions fingerprint our metadata, not the remote article bytes. Citation targets resolve to the current catalog snapshot; a study reference freezes its exact catalog version. Historical note citations are not silently re-resolved as historical source versions.

The public build reads explicit public files only. The private endpoint `/api/knowledge-graph` uses the same owner authorization and no-store responses as the workbench. It excludes free-text observation notes and participant aliases from graph properties. It is not an admission or training endpoint. Withdrawing a record removes its observation node and incident edges; revoked releases have no member edges. Previously downloaded graph copies still require separate removal.

### Media and derived results: foundation implemented, real intake still designed

The October 2 continuation implemented the synthetic metadata subset in [MEDIA_LINEAGE](MEDIA_LINEAGE.md): audio/video descriptors, synchronization, frozen model specifications/inputs and invented outputs, with withdrawal propagation. The table below describes the fuller real-data design; object storage, media bytes, participant permissions and model execution remain future work.

| Record | Required provenance and constraints |
| --- | --- |
| Media asset | Immutable asset UUID, private object key, content SHA-256, byte count, codec, duration, sample rate or frame timestamps, modality, capture-device alias, session, rights record, retention deadline and deletion state. Never authorize by checksum alone. |
| Synchronization | Paired asset IDs, measured offset in milliseconds, drift estimate, calibration method/version, uncertainty interval and validity window. Unknown is allowed; wall-clock equality is insufficient. |
| Annotation | Media ID, interval or frame range, codebook version, observer/model origin, reviewer decisions, independent-label provenance and visibility. Model predictions must not overwrite human observations. |
| Model run | Code commit, checkpoint hash/license, parameter and environment versions, approved input-release fingerprint, split manifest, seed, metrics and run status. |
| Prediction | Run ID, asset/interval ID, label distribution, calibration status, abstention and out-of-domain flags. Link to the exact input version. |
| Permission and release | Separate private-review, training and publication purposes; protocol/consent versions; review evidence; immutable release membership with revocation. Public approval is additional to private training approval. |

These extensions need an explicit PostgreSQL migration and SQLite parity, transactional foreign keys, restricted runtime permissions and deletion/recovery tests. Do not use arbitrary user-supplied graph edges as facts. Model embeddings are derived data, inherit access/deletion rules and must identify their encoder version. A vector index may support retrieval later; it cannot serve as the consent or provenance system.

### Future contribution workflow

1. A person records locally and sees what will be contributed, including audio/video and metadata.
2. They join an approved study and select separate reuse permissions. Background uploads are opt-in, visibly queued and cancellable.
3. A server issues a short-lived upload grant for a bounded, private object key. Validate size, content, checksum, allowed media and consent server-side; use idempotency keys and retry receipts.
4. Quarantine before research use: remove sensitive locations/EXIF, review human voices/faces, check quality and rights. Automated screening assists a reviewer and cannot guarantee absence of private material.
5. A reviewed, immutable release can enter evaluation/training only for its approved purpose. Public releases need separate publication checks, clear dataset documentation and a suitable license.
6. Withdrawal reaches objects, metadata, indexes, derived features, queued jobs and dependent releases. Reconcile withdrawals after a backup restore. Retraining/removal limits and downloaded-copy limits must be stated before collection.

Do not make every recording public automatically. An open research database should mean a documented, reviewed release with reproducible access conditions. Public metadata can remain open when sensitive media requires restricted access.

## The first machine-learning experiment

**Question:** Does audio add predictive information about a small set of independently observed behaviors, beyond video and environment alone, on held-out individuals and sessions?

Proposed sequence:

1. A species specialist defines one species, passive protocol, stop rules and observable codebook. Choose naturally occurring behaviors. Reviewers label silent video before hearing audio or seeing predictions; use a second reviewer to measure disagreement. A recording is not a conversation just because a sound follows a person.
2. Check audio/video alignment on a controlled synthetic or instrument fixture first. Report offset/drift uncertainty; do not stimulate animals to create a calibration signal.
3. Start with frozen audio embeddings from an existing licensed checkpoint and pose/video features appropriate for the selected species. Review checkpoint, data and code terms separately. A SuperAnimal quadruped model is not a ready-made parrot tracker. See the [multimodal evidence note](../content/research.json) and [primary SuperAnimal study](https://www.nature.com/articles/s41467-024-48792-2).
4. Compare context-only, background-only, simple acoustic, audio-only, video-only and combined baselines. Predict a defined label, not free-text intent. Hold out animals, households/sites and sessions as appropriate; check pretraining overlap. Randomly splitting adjacent clips would reward memorization.
5. Freeze the analysis before evaluating. Report event recall, false alarms per hour, identity/pose error, class-wise precision/recall, calibration, abstention coverage and uncertainty clustered by animal/session. Review time is a product metric. A pilot estimates variance and failure modes; a specialist/statistician determines sample size for confirmatory claims.
6. Only after these baselines, assess paired audio-video contrastive learning or masked prediction. Use time-shifted and environment-matched negative pairs, and compare synchrony to shuffled controls. Contrastive clusters may reflect a cage, microphone or wind rather than a biological signal.
7. An LLM can help search cited research and explain an observation's evidence trail. It should distinguish observation, model hypothesis and experimentally supported interpretation. Fluent text is not a semantic label or a biological ground truth. No autonomous playback loop in this phase.

Reusing pretraining is plausible, as in human-language ML; the essential missing ingredients are grounded targets, suitable observations, known uncertainty and tests of receiver relevance. One universal next-token objective across birds, trees and fungi would hide different sensors, timescales and biological functions.

## Camera and sensor roadmap

Use a phone web app for visible short capture first; retain the existing local mode. A separate consented camera prototype should pair frame timestamps with audio, show a live indicator and stop on interruption. Evaluate camera permission denial, thermal load, orientation changes, dropped frames and actual iOS/Android behavior before release. Auto-identification returns candidates with uncertainty; pose and gestures need species-specific labels. Ordinary images do not reveal internal physiology or guarantee individual identity. Infrared/thermal claims require the corresponding hardware.

For spare-phone operation, a native Android pilot is the next practical engineering candidate, after physical-device tests. Foreground-service/battery/privacy requirements need a current platform review at implementation time. TV is initially a paired display for reviewed results, not an assumed ultrasonic microphone. Smart-speaker integrations are later, separately assessed distribution channels.

## Plants, fungi and the water question

- **Plants:** distinguish airborne acoustics, chemical cues and internal electrical/calcium signaling. The new notes link the [chemical-sensing experiment](https://www.nature.com/articles/s41467-023-41589-9) and [moth–plant study](https://doi.org/10.7554/eLife.104700). Select a real sensor and outcome with a plant physiologist. Do not advertise phone-based plant ultrasound translation.
- **Fungi:** treat electrical measurements as an instrumentation problem first. The [2026 propagation study](https://www.nature.com/articles/s41598-026-47035-2) motivates questions; its eight channels are not eight independent organisms. Plan independent specimens, sterile/substrate controls, electrode drift and environmental logging. No consumer “mushroom translator.”
- **Water/ice:** the likely reference is Masaru Emoto. [The original pilot](https://pubmed.ncbi.nlm.nih.gov/16979104/) and [a published experimental-unit critique, p. 83](https://journalofscientificexploration.org/index.php/jse/article/download/108/46) are now linked in the library. Treat this as a lesson in testing extraordinary interpretations, not an established mechanism or a central research bet.

## Ideas worth testing

| Idea | Why useful | First falsifiable check |
| --- | --- | --- |
| Encounter timeline | Review sound, movement and environment together while keeping raw evidence distinct from interpretation. | Can independent reviewers locate and label a moment faster without losing agreement? |
| Quiet-window audit | Event triggers miss low-amplitude signals; a reviewed reference sample measures what was missed. | Compare trigger recall to a continuous, permitted reference interval. “No detected event” must never become “silence.” |
| Personal context map | Repeated natural scenes may reveal individual variation and challenge universal labels. | Does a within-animal association survive a held-out day, and does it transfer to other animals? |
| Ask for the next useful review | Prioritize ambiguous intervals and conflicting labels, not only confident/interesting clips. | At equal review time, does uncertainty sampling improve held-out performance more than random selection? |
| Sensor honesty card | Show what this device can actually measure, including known noise and frequency limits. | Compare each supported device to a reference fixture before admitting hardware-specific claims. |
| Replication notebook | Bind a conclusion to protocol, labels, model version, controls and a frozen release. | Can another reviewer reconstruct the same table and identify a withdrawn dependency? |

All are proposed experiments. None is a result or endorsement from the researchers cited.

## Expertise and connections

These are prospective review routes identified through published work, not people who agreed to advise or partners we have contacted.

| Needed role | Starting route | Specific first request to prepare |
| --- | --- | --- |
| Animal communication / bioacoustics | [Yossi Yovel, TAU](https://english.tau.ac.il/profile/yossiy), existing project connection map | Critique one passive audio-video question and its inference limits. |
| Behavioral biology | [Lee Koren, Bar-Ilan](https://gondabrain.biu.ac.il/en/node/776) | Review observable labels, species choice and welfare boundaries. |
| ML / movement analysis | Authors and official projects of [DeepLabCut](https://github.com/DeepLabCut/DeepLabCut), [SimBA](https://github.com/sgoldenlab/simba) | Identify the right pretrained baseline and failure tests, with license boundaries. |
| Plant physiology | Masatsugu Toyota and colleagues through the linked primary paper | Assess a feasible passive sensing protocol and an appropriate instrument. |
| Fungal electrophysiology | Authors of the 2026 paper and the measurement caveats already in the library | Obtain independent measurement review, including substrate/electrode controls. |
| Open science / conservation networks | [Existing UN, UNESCO, UNEP/CODES and WILDLABS map](OPEN_SCIENCE_AND_CONNECTIONS.md) | Seek a relevant working group after a reproducible demo and clear protocol exist. |

Next outreach is a short, tailored request for a methods review with an honest demo link; no bulk mailing. Sending it still requires Raviv's explicit instruction. Citation does not imply collaboration.

## Sequence and acceptance

1. **Now: simple, credible public release.** Browser save/reopen, advanced export, responsive navigation, offline shell, link checks and both database adapters. Preserve stable competition URLs. Record deployment receipt in STATUS.
2. **Next engineering milestone: hosted synthetic owner workspace.** Complete the already-pending provider setup without recreating billing. Verify real hosted owner login and non-owner denial, persistence, catalog import, graph, revocation and recovery. Existing approved budget is at most $50/month; no new purchase is made here. See [HOSTING](HOSTING.md).
3. **Then: one consented audio-video pilot.** Protocol review, permission screens, bounded private uploads, migration for media/synchronization, deletion reconciliation and physical phone tests must pass before opening intake.
4. **Then: a reproducible baseline.** Freeze one permitted release and its split. Publish negative and positive results with the comparison baselines above. Decide whether additional modality or scale is justified.
5. **Distribution after usability evidence.** Recruit five usability testers and one qualified scientific reviewer first (targets, not current participants). Prepare a short demo and a reproducible methods note. Offer a concrete first GitHub contribution. Share through relevant acoustics/open-science communities only with authorized outreach. Measure successful save/reopen, submitted actionable feedback, independent reproduction and reviewed contributions before audience size. No invented partners or premature translation marketing.

## Current limits

Shared hosting, real participant intake, media-object storage, trained models, automatic identification and camera capture remain unimplemented. Synchronization metadata and model-run/input/result tables are now implemented for synthetic rehearsal only; see MEDIA_LINEAGE.md. Real-data admission remains closed. The public catalog contains metadata and original summaries, not copied full articles, audio or model weights. Physical-phone installation and microphone behavior still require device testing. This bounded release establishes the user experience, research direction and provenance foundation for the next milestone.
