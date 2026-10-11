# Prioritized research and machine-learning backlog

This is a decision queue, not a claim to have reviewed the entire field. The founding inventory and its subsequent additions include documentation, organizations and grants as well as papers. Full text is not copied into the public website.

## Reading order

1. Japanese tit call-order experiments (source 1): read methods, playback controls and receiver outcomes. Extract what a bounded semantic claim actually requires.
2. Parrot voluntary interfaces (sources 38–39): retrieve the primary nine-parrot study; inspect selection, choice, intervention and welfare measures with an avian specialist. Compare local prototype ideas only after source provenance, bundled-media rights and the study question are resolved.
3. Bark transfer-learning paper (source 21): inspect individual/session partitioning and class definitions; learn from leakage risks without assuming dog results transfer to birds.
4. BirdNET, Perch and NatureLM (sources 4, 7–8, 12–14): freeze exact code/checkpoint versions; inspect data provenance, licenses, preprocessing and baseline costs. Do not download weights or promise commercial suitability yet.
5. BORIS and Arbimon (sources 10–11): try a real researcher-supplied workflow. Write a concrete integration issue or choose an upstream contribution.
6. CETI structure/behavior studies (sources 2–3, 24): distinguish acoustic sequence organization from a semantic interpretation and determine suitable event-level evaluation.
7. Plants and fungi (sources 15–18): keep as a separate evidence track. Review measurement artifacts and receiver experiments before any product concept.

Each completed review should record citation/DOI, exact version, access date, sections reviewed, task, sample/unit of analysis, labels, split, controls, result, uncertainty, limits, data/code access, license and relevance to our experiment. State when an abstract or announcement is all that was accessible. Independent expert review has its own status.

## Reading checkpoint — September 30, 2026

Items 1–3 now have method notes on the website. Consult `content/research.json` for study designs, outcomes, limitations and precise reading locations; references and full-text access links are in `content/sources.json`. Bird-syntax interpretation also links to a scholarly commentary. No scientific specialist has reviewed our notes.

Decision: individual-held-out context evaluation and transfer from pretrained acoustic representations already exist. Do not claim those ingredients as novel. Any grant proposal must establish a specific additional contribution. A voluntary parrot-interface study, if selected, needs its own design and outcome measures rather than inheriting claims from natural-call classification.

Review follow-up: the parrot paper’s Table 2 displays differences that need checking before quantitative reuse. For example, P3 shows 75% live and 0% playback, but the displayed difference is -8%; P5 shows 58% and 50%, but -75%. These appear inconsistent with their columns. Our note reports the broad author conclusion with limitations and does not reproduce these differences or independently validate the statistical analysis. Do not contact the authors without authorization.

## What exists and what remains unresolved

| Capability | Existing starting point | Next project decision |
| --- | --- | --- |
| Detect / identify sounds | BirdNET, Merlin and other mature systems | Reuse if needed; do not mistake identification for semantic understanding. |
| Extract reusable features | Perch and other audio representations | Select a permitted, frozen checkpoint and baseline on real target data. |
| Describe biological audio | NatureLM-audio | Test grounded accuracy and abstention; respect exact model terms. |
| Annotate behavior / recordings | BORIS, Arbimon and existing review tools | Demonstrate an actual unmet workflow need before building a platform. |
| Associate sound and observed context | Many species-specific studies | Define a narrow task and evaluate beyond individual/device/background cues. |
| Support a bounded meaning claim | Carefully controlled receiver experiments in some species | Requires a suitable scientist and protocol; not demonstrated by our tooling. |
| Translate all natural communication | Not established by reviewed evidence | Long-term question; not a launch promise or first benchmark. |

## Initial code boundary

Implemented: metadata declarations, transitive grouping across individual/session/source hash, reproducible split assignment and manifest fingerprint, class-count diagnostics. Synthetic fixtures exercise failure cases.

Still needed for a real experiment: data rights, recording ingestion/checksums, synchronized observations, ontology, annotator agreement, near-duplicate detection, selected licensed model, background/context baselines, meaningful metrics, calibration, cluster-aware uncertainty and independent data. The current split is not a substitute for any of those.

## Organizations to understand before contacting

- Israeli science: Yovel laboratory, Lee Koren's research and related bioacoustic groups. Confirm the relevant current paper/question rather than send a generic partnership request.
- Parrot cognition/interfaces: Alex Foundation and the Glasgow/Northeastern research teams described in the audit.
- Open bioacoustics: Earth Species Project, BirdNET, Perch, BORIS and Arbimon maintainers. Start with existing documentation and contribution norms.
- Field networks: Interspecies Internet and conservation groups with a specific data or annotation problem.

No one in this list has been contacted or has agreed to participate. Prepare a concise research brief before any authorized outreach.

## October 11 update: MeerKAT can guide detection methods, not the first context benchmark

The published animal2vec/MeerKAT paper is now reviewed beyond its earlier abstract/README-only entry. Its 1,068-hour continuous-audio collection, 184 hours of complete event labels, noisy intervals and event precision–recall evaluation are useful references for detector design. Its label target is call/event classification, not independently observed behavior or receiver understanding.

The peer-reviewed paper states separate terms: MeerKAT data and animal2vec checkpoints are CC BY-NC 4.0; the code is MIT. Data/checkpoints are therefore not admitted to the shared commercial-capable path. Public sample names deliberately hide individual and time order, and the paper's sample-level folds were not verified as animal/session-held-out. Do not download or run the package for this project. Next, reuse the metric and continuous-quiet-window lessons in a rights-cleared evaluation specification; only consider a separately governed academic reproduction after exact inventory and grouping metadata are authorized and reviewed.

## Model and data checkpoint

See `docs/MODEL_DATA_DECISION.md` for exact candidate references, separate code/model terms and dataset-fit decisions. Perch-Hoplite is the current candidate tooling route; no model has been installed. The public library now includes a benchmark-label note. Further implementation depends on a concrete species/question and usable observations, not another general model survey.

October 9 decision: adopt the experiment-control pattern from Karpathy's AutoResearch, not its language-model trainer. The project-specific agent program is explicitly not ready because no admitted, independently behavior-labeled dataset or frozen benchmark exists. See [`AUTORESEARCH_ADAPTATION.md`](AUTORESEARCH_ADAPTATION.md) and [`research/autoresearch/program.md`](../research/autoresearch/program.md).

## October 11 checkpoint — animal-operated interfaces

The targeted review of CHI 2024's parrot touchscreen ergonomics study (source 122; note `parrot-touchscreen-ergonomics`) now records the screened/trained sample, task, welfare provisions, study-specific multi-tap rule, outcome counts, paper license and unresolved data/code access. Evidence came from the University of Glasgow record and abstract, the authors' lab summary and selected indexed text from the repository-hosted PDF. The direct 19 MB PDF fetch failed, so the complete article and remaining tables were not inspected; this remains a bounded source review, not independent expert review.

Decision: treat this as guidance for evaluating a possible parrot-operated enrichment interface, not for the current human-operated passive recorder, acoustic ML benchmark, animal communication or universal touchscreen defaults. Any such interface needs a separate welfare-reviewed protocol and individual/species-aware usability work. Next source step is to verify the remaining paper details and whether data or code can be lawfully obtained, then seek qualified independent review before prototyping. No animal data were acquired or used.

## October 11 checkpoint — monk-parakeet dataset fit

The targeted review of the 2023 monk-parakeet voiceprint study confirms a useful identity-method comparator, not a communication or context benchmark. The paper reports 5,599 vocalizations from 229 marked birds and individual signatures in three of five analyzed call types. Figure 4's cross-call-type evaluation appears to test caller identity for known individuals, not unseen-bird generalization; that is a design interpretation. The linked 2020/2021 annotation schemas differ, and free-text behavior labels are not independently verified context ground truth. Direct article retrieval was CAPTCHA/timeout limited; the supplement and observer-reliability workflow remain unreviewed. No recordings or weights were acquired, and no model was run.

Decision: do not select this as the first context-prediction dataset or claim it demonstrates call meaning. If a caller-identity reproduction is chosen, inspect the split and reliability scripts and refresh component-specific data terms first. For the first context benchmark, prioritize a rights-cleared dataset with timestamp-linked audio and independently observed target behavior. See `COLLECTION.md`, `MODEL_DATA_DECISION.md` and the `parrot-data-feasibility` evidence note.

## October 11 checkpoint — budgerigar vocal/sociality near-match

Reviewed the primary abstract and targeted Methods text plus the Dryad deposit inventory and reuse policy. The study paired longitudinal contact-call features with home-flock social observations, but not at the same events: contact calls were recorded from individually isolated focal birds, while behavior labels came from separate flock videos. The Dryad file list includes derived call features, social-event coding, interobserver material and example video, but no original call audio. Dryad data are CC0 under its repository policy; the article and included software remain separate artifacts. No files were downloaded.

Decision: retain as a protocol and annotation-schema comparator, not the first acoustic context benchmark. A small aggregate flock-level question is only a future option after exact joins, independent review and a suitable holdout. The immediate data requirement remains synchronized rights-cleared audio with independent event timestamps.

## October 11 checkpoint — funding-call fit and date refresh

Rechecked the official Israel Innovation Authority and NLnet pages. Tnufa's October 8 deadline has passed; its page did not show a later date on October 11. Pre-Seed's page now lists November 9, 2026 at 12:00 Israel time. This is a conditional lead only: the route requires an Israeli-incorporated commercial-R&D company, a recognized investor commitment of at least 15% of the requested round, at least 75% R&D spend, and the stated prior-funding/revenue limits. The applicant entity, investor and eligibility facts remain unconfirmed.

NLnet's November 3 call is active, but neither open fund fits the current project: Restack excludes AI-related projects except a narrow, over-one-million-user infrastructure case; CodeSupply funds software-package supply-chain metadata, not Talk2Nature's biological research catalog. NLnet says its GenAI policy is being revised, warns that mostly LLM-generated work is currently ineligible, and advises projects using LLMs to wait for the updated policy. The Restack FAQ asks applicants to author their own proposal and disclose/explain any GenAI use. Recommendation: do not spend proposal effort on either NLnet fund for the current scope; revisit only if scope and policy materially change. No application was submitted and no external contact was made. Public opportunity records link official sources 26, 27, 35, 150–152.

## October 11 checkpoint — Egyptian fruit-bat context archive

Add the 2017 synchronized audiovisual dataset and 2023 sequence follow-up to the review queue. The descriptor's sampled 435-annotation quality audit and independent video-derived labels make this a strong protocol comparator. Published 2016/2023 context-classification scores are not semantic decoding; neither reported split establishes held-out-animal generalization. The raw Figshare item remains rights-unresolved, while Mendeley v3's CC BY 4.0 declaration needs file/provenance review. Keep both metadata-only. The next useful work is direct item/file-rights verification and a leakage-safe split audit, followed by a bounded baseline proposal only if rights and access permit it.

### October 11 follow-up — Mendeley version history

Reviewed the exact version 3 landing page and official v1/v2 and v2/v3 comparisons. V1 contains metadata only; v2 and v3 describe phrase.rar example WAVs, 326 sequence encodings, encodings for more than 28,000 syllables and context annotations; all three versions display CC BY 4.0. The description says the example WAVs come from the separate Prat et al. 2017 archive. The accessible page exposes no per-file manifest or audio provenance, so its deposit license does not clear upstream audio rights. Mendeley's official API documentation describes a versioned public file-list route, but it was not queried; no files were downloaded, and both resources remain metadata-only. Next: inspect v3 file metadata through the documented route if accessible, verify source-archive rights, and seek expert review before proposing a benchmark.
