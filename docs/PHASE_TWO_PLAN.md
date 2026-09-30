# Phase two: an observation network with a private research workspace

Decision record, 30 September 2026. Owner: Raviv. Account boundary: raviv@metivity.com / Metivity/talk2nature. This is a product and research proposal, not a validated business or a claim to translate animals.

## The first product to build

**Talk2Nature Field Notes:** a mobile observation companion for a small, invited group studying one species. The useful immediate outcome is a consistent observation history and a reviewable dataset. A participant should know what to observe, record a short permitted sample, annotate visible context, and understand whether the contribution was usable. Their reward is a useful journal and feedback about evidence quality, rather than points for uploading more sound.

The first customer hypothesis is a researcher, sanctuary or avian behavior team that already spends time linking recordings to observations. Test willingness to use and pay for a managed study workflow. A generic species identifier is already well served by tools such as Merlin and BirdNET; a credible advantage would require reducing the cost of acquiring independently labeled, permissioned, cross-individual observations. That advantage is unproven. Community contributions and existing annotation tools should be considered before custom development.

| Product | Immediate value | What it can teach us | Decision |
| --- | --- | --- | --- |
| Field Notes on a phone | Guided observations, short sessions, history and quality feedback | Which contexts people can label reliably; association between sound and independently observed events | Start here; responsive web interface, then native capture when justified |
| Spare-phone listening station | Scheduled, visible recording sessions with local screening and review before upload | Longer temporal structure and events people miss | Second; first test a dedicated Android device after protocol approval |
| Research workbench | Review, provenance, permissions, dataset releases and withdrawal | Where annotations fail; which data is actually admissible | Build first, privately, with synthetic rehearsal |
| Television companion | Household review screen, session progress, later a paired display | Could support a voluntarily learned interface in a separate specialist-led study | No standalone TV recorder initially; microphone capability varies by hardware |
| Animal “chat” | Attractive promise, uncertain scientific validity | Fluent answers can disguise missing evidence | Do not ship unrestricted translations or automated playback |
| Plant/fungal station | Potential environmental or physiological monitoring | Modality-specific hypotheses with proper sensors and controls | Separate later research track |

No app-store release, user recruitment, interviews, animal recording or payments have occurred. Kiki may provide experience or code only after its location and ownership are confirmed.

## A useful mobile flow

1. Invitation into one study; plain-language scope, withdrawal procedure and separate permissions for review, training and public sharing.
2. Pseudonymous animal and device registration; species, individual confidence and device capabilities. Household addresses and precise wildlife locations are unnecessary for the first app.
3. A short, participant-started session. Show recording status, duration, stop and discard controls; default upload remains off until review. Never create stress to obtain labels.
4. Observe first: time, nearby animals, visible behavior, environmental event and an explicit “unknown.” Collect context independently of model predictions to reduce anchoring.
5. Inspect the clip, human speech/privacy concerns and rights. An uncertain speech detector cannot guarantee that a recording is safe to upload. Retain random, consented background windows as well as detected calls so a detector does not silently define the entire dataset.
6. Receive a review outcome and correction request. A submitted sample does not train a model automatically. A contributor can withdraw without needing an admin to interpret their reason.

The implementation in `admin/` rehearses metadata submission and review with synthetic examples only. It has no microphone permission, offline cache, audio upload, contributor accounts or phone background service. It is a responsive owner workbench, not a released mobile app.

## Device constraints change the roadmap

- **Mobile web:** best first route for forms, consent, annotation and short foreground sessions. Do not promise reliable locked-screen or unattended browser capture. Test interruption, tab suspension, storage pressure and permission loss on actual target devices before adding recording. An offline queue must be opt-in, bounded, encrypted where feasible, deletable and never cache private admin responses through a service worker.
- **Android native:** a microphone foreground service can continue capture after an eligible foreground start and permission grant. Android restricts background starts and boot-triggered microphone services. A visible session, persistent notification, user stop action, battery/thermal checks and daily limits belong in the design. This supports a spare-phone candidate, not a guarantee of uninterrupted recording. [Android microphone service requirements](https://developer.android.com/develop/background-work/services/fgs/service-types#microphone).
- **iOS native:** recording audio can use the recording audio-session category and the audio background mode, but interruptions still occur. A blanket claim that iPhones cannot record in the background would be wrong. App review, battery use, lock-screen behavior and interruption recovery need device tests. [Apple record category](https://developer.apple.com/documentation/avfaudio/avaudiosession/category-swift.struct/record).
- **TV:** pair with a phone using a short-lived code in a later version. Default to a display with minimal information, not an owner-admin login left on a shared screen. No assumption that a remote-control microphone supports ambient recording. Any animal-facing display/interface is a separate welfare-reviewed study.

No device choice was supplied yet. The default implementation remains browser-based and owner-only; an Android station is a proposed next experiment.

## Can we train it like a language model?

Partly. Self-supervised learning can discover recurring sound units, predict masked or subsequent acoustic segments and represent temporal structure without a transcription for every clip. This can reduce the amount of labeled audio needed. It does **not** identify a dictionary of intended meanings by itself. Human text is already grounded in human usage; assigning an English sentence to an animal sound introduces an additional scientific inference.

Yovel and Rechavi identify difficulties in grounding generated sounds, ruling out spurious context correlations, and assuming animals communicate about the same subjects people do. The institutional abstract was reviewed; no new full-text review is claimed here. [AI and the Doctor Dolittle challenge](https://doi.org/10.1016/j.cub.2023.06.063), [institutional abstract](https://cris.iucc.ac.il/en/publications/ai-and-the-doctor-dolittle-challenge/).

The proposed learning ladder is:

| Stage | Model and data | Valid output | Advance only when |
| --- | --- | --- | --- |
| 0. Measure | Sensor calibration, event detection, independent behavior labels | Recording quality, candidate events, unknowns | Protocol, consent and sufficient independent units exist |
| 1. Represent | Licensed frozen bioacoustic encoder; simple linear/nearest-neighbor baselines | Similarity and candidate sound categories | Beats naive baselines on a predeclared grouped evaluation |
| 2. Associate | Calibrated acoustic classifier plus separately evaluated context features | Probability of an observed context, with abstention | Improvement survives animal/session/site/device holdouts and confound checks |
| 3. Model sequences | Audio tokens or embeddings with temporal/contrastive prediction and synchronized observations | Repeated patterns and hypotheses about interactions | Adds value over simpler models on prospectively collected data |
| 4. Test meaning | Matched, controlled receiver-response experiments under a scientist's protocol | Evidence for a bounded function in one species/context | Replication, controls and welfare criteria support the inference |
| 5. Bounded exchange | Validated signal-response interface with uncertainty and stop conditions | A limited interaction the animal voluntarily participates in | Clear success criteria against sham/alternative stimuli and independent review |

Stages 4–5 are research proposals, not features enabled by the current code. Generating a plausible call is not permission to play it to an animal. A learned button or screen exchange tests an acquired interface; it should not be described as deciphering natural calls.

**First model decision:** reuse an encoder rather than train a foundation model from scratch. Perch-Hoplite is a candidate, conditional on the exact artifact license and its fit to the chosen species. NatureLM-audio and BirdNET have artifact-specific restrictions; see `MODEL_DATA_DECISION.md`. No weights or real dataset are admitted yet. DolphinGemma's sound modeling and the separately learned CHAT interface illustrate distinct research goals; the official announcement is not evidence of unrestricted dolphin translation. [Google / WDP announcement](https://blog.google/innovation-and-ai/products/dolphingemma/).

An LLM can help navigate the cited library or turn reviewed annotations into readable summaries. It should receive structured observations, provenance, uncertainty and permitted claims. It should not invent animal speech in the first person, label training examples from its own guesses, or see private clips through an external API without a separate data decision. A source-grounded assistant is optional; the observation workflow does not require one.

## First experiment and decision criteria

Proposed question: **does sound improve prediction of one independently observed behavioral context in one selected species, beyond the scene and background alone?** A captive-parrot setting is a candidate, subject to access and scientific advice. “Feeding,” for example, is an observable activity rather than a claim that a call means “I am hungry.” The UI's provisional labels are a rehearsal vocabulary, not a final ethogram.

- Start with a clearly defined positive context and matched negatives, a predeclared analysis window and enough independent animals/households/sessions for the intended claim. Determine sample size after a small label-feasibility study and power/precision planning; hundreds of clips from one animal do not supply hundreds of independent subjects.
- Label from synchronized video or contemporaneous direct observation, before showing model output. Double-label a planned subset, measure agreement and adjudicate disagreements. Preserve uncertainty and label revisions.
- Compare majority, context-only, background-only, acoustic-only and combined models. Include shuffled-label checks, source-duplicate checks and a held-out household/device audit. Feeding sounds or a caregiver's words can make a context easy to classify without decoding a call.
- Group by connected animal/session/source relationships using the existing tool; add study-specific site and device controls. Tune on training/validation only. Report macro F1, class precision/recall, calibration, coverage when abstaining, and uncertainty resampled at the independent study-unit level. Freeze the release and split before final testing.
- Proceed if a collaborator considers the labels meaningful, participants can supply usable observations at acceptable effort, and performance is useful with calibrated uncertainty on the held-out population. Set numeric thresholds with the collaborator before examining results. Report negative results and stop or pivot if the collection burden or confounding dominates.

Novelty must be demonstrated against existing datasets, tools and papers. The reviewed dog Wav2Vec2 paper already used dog-grouped evaluation for several tasks; group splits alone are not a novel scientific contribution.

## Plants, trees and fungi

Keep these in the evidence library and a separate sensing roadmap. The plant paper reports ultrasonic emissions associated with conditions in tomato/tobacco; it does not establish an English-like language. A phone microphone at ordinary audio sample rates is not a substitute for a calibrated ultrasonic acquisition system. [Khait et al., Cell 2023](https://www.sciencedirect.com/science/article/pii/S0092867423002623) (abstract/source summary reviewed this phase).

The fungal paper analyzes electrical spikes and groups them into word-like units under an explicit assumption about communication. Statistical similarity does not establish referents or conversational meaning. Electrode placement, environmental confounds, timescale and replication are separate problems from phone audio. [Adamatzky preprint and abstract](https://arxiv.org/abs/2112.09907) (abstract reviewed this phase). Do not pool electrical, ultrasonic and audible signals into a single “nature language” target without a validated task.

## Delivery gates

| Gate | Deliverable | Evidence required |
| --- | --- | --- |
| A — this foundation | Private owner workbench, synthetic workflow, documented architecture | Auth/access tests, review/release/withdrawal tests, desktop/mobile UI inspection |
| B — live identity and hosted metadata | Dedicated cloud project, real Google owner login, deployed private service | Account verification, owner binding, wrong-account rejection, HTTPS, budget and storage decision, backup/restore test |
| C — invited mobile study | One codebook, consent, participant roles, short capture and review | Scientific collaborator, actual device tests, rights and privacy review, deletion drill, quotas |
| D — empirical baseline | Frozen dataset release and evaluation report | Real admitted data, license checks, leakage audit, calibrated baseline comparison |
| E — interaction research | Bounded, specialist-led experiment | Receiver-response protocol and welfare review; separate approval for playback |

Broad orchestration means keeping these dependencies visible and working the next unblocked gate. It does not authorize opening public recording intake or treating every app idea as a simultaneous build.
