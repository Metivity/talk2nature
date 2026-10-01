# Usability and research-library audit — October 1, 2026

Scope: internal inspection of the public app, recording/review/export paths and research navigation. This is not a participant usability study, specialist scientific review or security certification. Native microphone and actual phone lifecycle behavior remain unverified.

## Findings and changes

| Finding | Consequence | Change |
|---|---|---|
| Technical sensitivity settings appear before the first session | A beginner must interpret dB margins before trying the tool | Optional Session settings with sensible defaults and plain sensitivity names |
| Several branded names describe the same task | Harder to choose a first action | “Start listening”, “Try an example”, and “Review a recording”; a direct recording link from Review |
| Decorative mobile hero pushes task choices down | More scrolling before a useful action | Compact phone hero; illustration retained on desktop |
| The example still shows microphone setup | Unclear whether trying it records people | Demo mode shows the no-microphone action and hides microphone consent/start controls |
| Each WAV needs a separate download | Easy to save a journal but lose its audio | One local ZIP with journal, retained WAVs and readme; individual exports remain |
| Invalid alias produces a generic export error | No clear repair path | Open settings, focus and mark the invalid alias, explain the requirement |
| Library search only covers a few summary fields | Reusable methods and code are difficult to find | Search includes lessons, source titles and reuse metadata; area + purpose filters and reset |
| Notes exist without a clear sequence of decisions | Reading does not reliably inform implementation | Four source-linked starting paths: context, detection, model reuse and evidence for meaning |

Do not interpret these internal findings as measured improvement in conversion or usability. A small independent device/user test is still the next product check.

## Research expansion

Six added notes: AVES/AVEX, BIRB, DAS, bat context annotation, animal2vec/MeerKAT and elephant receiver-specific calls with a linked statistical critique. The collection now has 22 notes and 87 source records (including 10 videos). New notes state their actual review depth, reusable component, rights uncertainty and proposed next step. The elephant critique is located, not fully reviewed; it is an explicit reading dependency rather than a claimed refutation. No new model, dataset or third-party article was downloaded into the public site.

`content/research.json` and `content/sources.json` remain the canonical public metadata. `content/learning-paths.json` connects notes into decision paths. The existing private catalog stores fingerprinted public note/source/resource payloads; this import does not admit recordings or change frozen study versions. The eight-entry acquisition catalog in `research/resources.json` remains separate: a newly cited resource is not automatically approved for downloading.

## Video and collaboration expansion

Raviv’s coordination update extended the active milestone. `/watch/` contains ten curated videos: nine YouTube entries and one Cornell-hosted external playback link. Coverage includes ESP’s research vision, CETI films/model introduction, plant sound measurement, BirdNET workflows and field monitoring. Original publisher sites establish provenance; YouTube oEmbed responses verified the exact nine video titles, channel attribution and availability of embed markup. This is not a full viewing/transcript review, guaranteed future availability or confirmation that every player works on every device. Per-video review depth stays visible.

No external video thumbnails, scripts or iframes load initially. Users explicitly load a `youtube-nocookie.com` player, with autoplay disabled and a descriptive iframe title. Direct publisher links remain visible; filtering out a loaded player removes it to stop hidden playback. The Cornell video uses a direct link because no embed was configured. Videos are not copied or relicensed. Media metadata is part of each source record and therefore joins the existing versioned private catalog without a second source inventory.

`/contribute/source/` prepares a source, correction, question or task-interest draft locally. It validates a bounded HTTPS link and fields, presents the exact draft as text, and offers a user-triggered link to the configured GitHub issue composer. Nothing is submitted automatically. Repository issues are enabled; a separate GitHub Discussions forum is not enabled and is not claimed. Added two repository issue templates. Existing issue comments are the discussion venue; no posts, invitations, partner messages or research enrollment were sent. Maintainer review precedes website publication.

## Next research queue

Process these in order, unless a study decision makes another source more useful:

1. **Parrot dataset feasibility:** finish the statistical-method and annotation review already queued. Exit: identify whether independently observed behavior labels exist; otherwise reject it for the context-prediction question while retaining its possible identity use.
2. **Encoder baseline:** pin one candidate AVEX/Perch checkpoint and its code revision. Inspect separate code/weights/data terms, input frequency range and pretraining overlap. Exit: a small permissible evaluation specification, or a documented reason to use another checkpoint. No large training run yet.
3. **Annotation interchange:** inspect DAS export/import documentation and demonstrate a synthetic round trip. Exit: preserved interval boundaries and labels, with proposed labels distinct from reviewed observations.
4. **Detector evaluation:** read animal2vec event metrics and individual/day split details; inspect the MeerKAT deposit and rights. Exit: a continuous-audio evaluation plan including quiet/background intervals, misses and false alarms.
5. **Interpretation controls:** compare the elephant original analysis, the full 2026 reanalysis and any author response; finish the bat identity/context control review. Exit: an explicit claim/control table, not an assumed naming conclusion.

For each future review: find the original source, record date/version and exact sections read, distinguish author findings from our inference, inspect related corrections/critiques, record artifact-specific reuse terms, update the note and its next reading task, run site checks and synchronize the metadata catalog. Prefer one decision-changing review over a large list of unread links. New notes must not silently upgrade an abstract to a full-methods review.

No automated recurring research job was created. Further reviews are a prioritized continuation, not a promise that all literature has been read or that a background researcher is running.

## Remaining usability work

- Five first-time users should attempt example → stop → save → unzip → open WAV without guidance. Record completion, points of confusion and time; no measurements collected yet.
- Verify iPhone/Android downloads, installation, microphone permission and interruption handling on physical devices.
- Session journals and Listen labels are different formats. ZIP improves saving, but direct session-to-annotation transfer and M4A/MP3 support are still absent.
- The private hosted workspace and real-data intake remain gated as documented in HOSTING.md. Public tools keep data in tab memory; operating systems may discard that memory.

## Verification receipt

32 Python and 35 Node tests pass (67 total). The public build checks 43 HTML pages and 1,178 local link references. New tests use Python’s ZIP reader to check archive CRCs, exact WAV hashes and discarded-event provenance; they also check export bounds, snapshot consistency, safe contribution drafts, video identity and the absence of initial iframe/thumbnail requests.

Browser checks: a 43-second synthetic session retained seven clips, discarded one and saved a ZIP; all six included WAV checksums and ZIP CRCs matched. One 2.1-second WAV opened in Review, an observation exported/reimported, and the Python annotation report succeeded. Invalid alias export opened and focused the field without losing clips. The updated app loaded offline and saved another verified synthetic ZIP. No microphone or automatic playback was used. Phone app actions were visible at about 435 CSS pixels from the top, with no horizontal overflow at 390 pixels.

Library search found AVEX with the model-purpose filter; adding Elephants produced the empty state and reset restored all 22 notes. Video initial navigation made only local requests, with no provider request in the observed interval. The TAU player loaded with correct attribution and no autoplay, retained a direct YouTube link, and was removed when filtered out. All nine YouTube entries returned oEmbed identity/embed metadata; complete viewing, captions and all-player playback were not tested. The Cornell fallback page identified the webinar and presenters. The contribution helper rejected HTTP, previewed the correct GitHub composer link, and did not submit a post. Video, research and contribution pages measured no horizontal overflow at 390 pixels; video desktop measured 1280 pixels without overflow.

The private catalog now holds 117 records (87 sources, 22 notes, 8 acquisition resources). Reimport reports zero changes. Only public metadata changed; backend/auth/storage code and real-data gates were untouched. Private backend tests were not rerun or claimed. All research/video review limits remain visible. Proof files are ignored under `tmp/library-qa/`.

Published from `db52103db17f8ee221eb0788c7eb4813750b774f` through successful manual workflow [36883924743](https://github.com/Metivity/talk2nature/actions/runs/36883924743). All 75 deployed files returned HTTP 200 and matched the checked build. Live video, reading-path and AVES/AVEX note navigation was inspected. Proof: ignored `tmp/library-qa/live-files.json` and `tmp/site-preview/knowledge-hub-live.png`. Temporary preview tabs/server were closed and network/viewport overrides restored. The verified video room remains open as the deliverable. The bounded milestone is complete; the research queue and usability work above remain open.
