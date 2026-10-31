Warning: truncated output (original token count: 187321)
Total output lines: 3511

# Project status

## October 31 — refresh the Zero Command source gate

On clean public baseline `e1cef8a` (PR #628), reran `node --test tests/zero-command.test.mjs tests/native-zero-command.test.mjs tests/review-audio.test.mjs`; **14/14 passed**. The focused suites cover browser observation assets, deliberate/confirmed human-review playback, hidden-page cleanup, pending-permission focus recovery, Android notification/output constraints, and prevention of silent service restart.

This is a source regression check, not physical-device or assistive-technology acceptance. No microphone, animal, playback, recording, upload or participant data was used. Named iPhone/Safari, Android/Chrome, installed web app, native Android, VoiceOver/TalkBack and independent newcomer runs remain **not run** or open as applicable. The checklist and next acceptance step are in [`ZERO_COMMAND_DEVICE_CHECKLIST.md`](ZERO_COMMAND_DEVICE_CHECKLIST.md) and [`GOAL.md`](GOAL.md). No site deployment occurred.

## October 31 follow-up — Zero Command evidence note reconciled

PR [#627](https://github.com/Metivity/talk2nature/pull/627) merged to `main` as [`3ca40d1`](https://github.com/Metivity/talk2nature/commit/3ca40d199c7e618cb17465bf3521e9e6e174c15e). All Public checks passed, including repository, browser-tool, native Android and preview-site checks. It clarifies that the earlier locked-host attempt was unverified at that time and that a later local synthetic browser rehearsal did verify cancellation through the visible “Playback cancelled. This recording was not played” status. The app-level discard result, physical-device behavior, assistive-technology output and newcomer comprehension remain unverified. This was a documentation change only; no Pages deployment occurred.

The five-track goal remains **active**, with Zero Command as the immediate product milestone. Next gates are the reviewed clean-main Pages release and live verification when an authorized Metivity dispatch session is available, followed by separate named-device and assistive-technology checks. Until then, continue other project tracks and report unavailable checks as **not run**.

## Current focus — Zero Command acceptance

The active project goal prioritizes a consistent no-animal-output acceptance gate for the browser Field Companion and native Android Station. Added [`ZERO_COMMAND_DEVICE_CHECKLIST.md`](ZERO_COMMAND_DEVICE_CHECKLIST.md) as a runnable, privacy-minimal checklist with separate browser/native expected outcomes and explicit `not run` reporting. Source verification passed: the five focused Node suites passed **38/38**, and Android core/session/start-state checks passed. These checks do not establish device behavior. No physical-device run is claimed. Keep the microphone-free invented example first; live capture deliberate and stoppable; playback manual and confirmed. Device and independent-newcomer acceptance remain unverified. No animal data is needed for this gate. See [`GOAL.md`](GOAL.md) and [`ZERO_COMMAND.md`](ZERO_COMMAND.md).

**Keyboard-only rehearsal on merged `main` (`328ec47`):** a clean local noindex build was opened at `/app/station/?mode=demo`. Keyboard navigation reached the invented-example action; its focus ring was visibly clear. Enter started the microphone-free synthetic session and placed focus on End rehearsal; Enter stopped it and moved focus to review. Keyboard navigation reached Discard session; after confirming discard, the Station returned to Ready and focus moved to its heading. The browser accessibility tree exposed the no-microphone label and listen-only disclosure. No microphone permission or live capture was used. This is desktop-browser keyboard evidence, not screen-reader or physical-device validation; VoiceOver, TalkBack, novice comprehension and named-device behavior remain open.

**Rendered playback-cancellation rehearsal:** in a clean local `mode=demo` preview, selected Sound highlights, ran the synthetic session for 38.7 seconds, and reviewed one of six generated clips. Pressing Play opened the expected safety confirmation; dismissing it returned focus to Play and announced “Playback cancelled. This recording was not played.” The focused source tests passed **7/7**. No microphone permission, live capture, playback, download or upload occurred. Browser control timed out during final discard while the Mac was locked; the local preview server was stopped. A later inventory no longer listed the temporary preview tab, so it is no longer open; the app-level discard result was not verified. No real animal material was involved.

**Local integrity refresh (October 31):** reran the five focused Node suites (**38/38**), `python3 web/build.py` (162 pages plus 404, local noindex) and `python3 scripts/check_site.py` (163 HTML documents, 11,320 links); all passed. `git diff --check` passed. These are source/build checks only. The later rendered cancellation rehearsal above verified the browser cancel path with synthetic material, not physical-device playback behavior. Named-device, assistive-technology and independent-newcomer checks remain open.

## Current public-main researcher-kit verification

Reproduced [`RESEARCHER_START.md`](RESEARCHER_START.md) from a new depth-one clone of public `main` at [`6e5ae42`](https://github.com/Metivity/talk2nature/commit/6e5ae428cd402ce7168b7908d83a8c2d59073387), using Python 3.12.5, Node 22.22.1 and Git 2.53.0 with no package installation. The synthetic annotation command and standard/dyadic split examples succeeded; their output hashes match the expected values in the guide. Full suites passed: Python **244 tests, one intentional skip**; Node **171/171**. The local build/check passed (**162 pages plus 404; 163 HTML documents / 11,320 links**). The explicit-origin public-format build/check passed (**163 HTML documents / 11,483 links / 162 reachable public routes**). The fresh clone remained tracked-clean, with generated split files ignored. This confirms maintainer reproducibility of synthetic software examples at the current public revision only; it does not demonstrate independent use, usability, or biological validity. The initial attempt passed an unsupported `--base-url` argument to `check_site.py`; the correct `dist`-directory check then passed. Refresh the external reproduction evidence only when a user submits a report; do not infer adoption from this maintainer run.

## October 31 — OpenWhistle dataset-license cross-check

Rechecked the official OpenWhistle README and `LICENSE-DATA`, the immutable Hugging Face Croissant RAI metadata for the pretraining and classification datasets, their API card license fields and the separate Wav2Vec2 model card. Both Croissant records declare CC BY 4.0 even though the API `cardData.license` fields are null; the pinned repository `LICENSE-DATA` also declares CC BY 4.0 for dataset releases. The model card still says its license is unspecified; no code license was identified at the reviewed repository root. Added exact, versioned source records **560–561** and clarified [`BENCHMARK_CANDIDATE_RUN_CARD.md`](BENCHMARK_CANDIDATE_RUN_CARD.md) and the public OpenWhistle note. The dataset declarations do not resolve consent/provenance, paper-to-file matching, candidate novelty, or whole-animal generalization. No data, code, or weights were acquired or run. Keep OpenWhistle metadata-only and AutoResearch **NOT READY** until independent cetacean and ML/statistical review supports a bounded, non-duplicative, leakage-aware task.

**Local mobile-browser rehearsal (October 31):** on a clean current-main noindex build, emulated a 390 × 844 viewport and measured no horizontal overflow (document width 390 px). Completed the invented example, added one human-entered movement note, stopped, saved the local ZIP, and reopened that same file in Compare. Compare read it as an invented, partial whole-moment practice session with 13.8 seconds of retained audio and one observation; the audio element remained paused and had no autoplay. The file opened without extraction and was closed from Compare afterward. This verifies one emulated browser workflow only: no physical phone, Safari/Android device, real microphone, keyboard/screen-reader review, or independent novice was tested. The exact generated ZIP was inspected as synthetic and removed from Downloads after the rehearsal. No deployment or animal-data work occurred.

**Playback-cancellation source check (October 31):** on clean public `main` at `6e5ae42`, the focused Node suites `tests/review-audio.test.mjs` and `tests/zero-command.test.mjs` passed **7/7**. The harness verifies declining the just-in-time confirmation does not invoke `audio.play()`, replay requires a new confirmation, and the source playback boundary has no autoplay path. A current-main rendered preview exposed the manual player and warning. The rendered cancellation action is **unverified**: CUA reported that the host Mac is locked, and fresh click and keyboard dispatches timed out before a prompt or player state could be read. This is an interaction-tool limitation, not an app pass/fail result. Re-run the cancel path when an unlocked browser or named device is available; device and assistive-technology results remain open.

**Fresh live release read-back (October 31):** the public app home currently leads with “Try an example · no microphone,” but `/app/station/` still shows the older “Try without a microphone” and “Mark my voice” controls. The TLS-verified `scripts/check_live_site.py --base-url https://metivity.github.io/talk2nature --attempts 1` check fails at the Station's missing “Listen-only by design.” disclosure. Its current source also requires the observational “Mark heard speech” control and natural-speech guidance. This is a mixed/stale live release, not a device acceptance result. The connected GitHub toolset still has no manual workflow-dispatch action, so deployment and post-deploy verification remain open; do not treat the local branch as live.

**Pages dispatch identity check (October 31):** the repository's Pages workflow is `workflow_dispatch` only. The connected GitHub tools expose no dispatch operation. Local `gh auth status` reports active account `raviv-lgtm`; the stored `Metivity` CLI account is invalid. Because this task's publishing identity is Metivity, no workflow was started under the other account. Recheck only after an action-capable Metivity session is available; deployment and post-deploy verification remain open.

## October 31 continuation — reproduce the researcher quick-start from current public main

**Question:** can a new checkout of the currently merged project run the documented, package-free research examples and discoverable site checks?

**Evidence and verification:** fresh depth-one clone of public `main` at `b715fe3ce38ee4fb8b35f30e12a38ee482df92fd`; Python 3.12.5, Node 22.22.1, Git 2.53.0. The annotation example reported the expected invented 8-second sample, two marked events, 2 seconds of marked coverage and zero observed context. Both split examples completed and matched expected standard/dyadic hashes; their shared policy hash also matched. Python passed **244 tests (1 intentional skip)**; Node passed **171/171**. Local noindex build/check: **162 pages plus 404; 163 HTML / 11,320 links**. Explicit-origin public-format build/check: **162 pages plus 404; 163 HTML / 11,483 links / 162 reachable public routes**. Generated split files stayed ignored under `tmp/reproduction/`; the clone remained tracked-clean.

**Limits and decision:** this is maintainer rerun evidence using synthetic fixtures only. It does not demonstrate independent reproduction, newcomer success, scientific validity, animal communication or model readiness. No third-party media, animal data or model weights were acquired or run. Updated `docs/RESEARCHER_START.md`; next evidence needed is an independent researcher or newcomer completing a task and reporting barriers. Keep AutoResearch and real-data admission **NOT READY**.

## October 31 continuation — resolve the fungal dataset DOI record, not the data

Rechecked the current PMC full text, official Mendeley Data v1 record and DataCite metadata. They agree on dataset DOI `10.17632/srkxbkh6sp.1`; DataCite returns 404 for the differing DOI string `10.17632/srkkxbh6sp.1` printed in a previously reviewed publisher PDF. Updated source IDs 165, 166 and 559, the collection catalog and the public research note to record this metadata-level resolution. The Mendeley page's visible Files section is empty. No dataset, supplement or code was acquired, and no analysis or model was run. File contents, provenance, biological replicate structure, supplementary code references and component terms remain unverified; keep the catalog metadata-only and AutoResearch **NOT READY**.

**Zero Command release guard:** extended `scripts/check_live_site.py` so release verification fails if the live Station still shows “Mark my voice” or omits the accessible, naturally occurring speech-only guidance. Focused live-site tests pass **11/11**, including a stale-copy regression. The full Python suite passes **244 tests (1 intentional skip)**; Node passes **171/171**. The local noindex build produced **162 pages plus 404**; the site checker passed with **163 HTML pages and 11,320 links**; `git diff --check` passed.

**Goal update:** keep the five-track goal active. Current sequence: (1) run the reviewed public Pages deployment through an authorized workflow and confirm the live Station has the observational speech marker and setup copy; (2) complete named-device Zero Command acceptance with an invented/no-animal rehearsal; (3) request separate authorization before a novice walkthrough; and (4) obtain the fungal dataset manifest and independent mycology/electrophysiology review before any acquisition, while continuing bounded library and contributor-reproducibility work. A fresh TLS-verified run against `https://metivity.github.io/talk2nature/` fails on the live Station route because the expected “Listen-only by design” disclosure is missing; this check does not certify the live speech-marker copy. The Pages deployment for PR #622 and physical-phone evidence remain unresolved; no deployment or external contact occurred in this continuation.

## October 31 release receipt — zero-command startup and research onboarding

PR [#617](https://github.com/Metivity/talk2nature/pull/617) merged into `main` as [`be69a8f`](https://github.com/Metivity/talk2nature/commit/be69a8fcfc1429fac84288d02faa75998ee045c1). Public checks [#41175930357](https://github.com/Metivity/talk2nature/actions/runs/41175930357) passed the repository, browser-tool, native Android and preview-site steps. The merge includes the Station pending-permission focus fix, refreshed clean-clone researcher instructions, source-grounded research/atlas reconciliation, and first-use wording resilient to release lag.

**Current-source rehearsal:** rebuilt this exact `main` revision locally as a noindex site (162 pages plus 404; site check 163 HTML documents / 11,303 links). In a local browser, the invented Station action opened a synthetic session without showing a microphone permission request; **End rehearsal** produced a clearly labeled partial invented recap (2.8 seconds, 0 notes). Selecting **Save this moment** displayed the local-file guidance. The browser then required **I saved the file**; this pass did not verify the downloaded file on disk or reopen it in Compare, so the same-file Save-to-Compare acceptance is still open. No real recording, animal, playback or data admission was involved. This is desktop-browser evidence only.

**Release and next gate:** live Pages still serves the prior Station copy, while `main` contains the newer **Try invented example · no microphone** action and **Listen-only by design** disclosure. No Pages deployment occurred; its workflow is manually dispatched. No physical iPhone or Android device is attached (`xcrun devicectl list devices`: no devices found; `adb` is unavailable), so the named-device rehearsal remains unverified. Keep screen-reader and separately authorized newcomer checks open. The five-track goal remains active; AutoResearch and real-data admission remain **NOT READY**.

## October 31 continuation — align contributor instructions across the deployed/source copy gap

TLS-verified live-page check: `/app/` primary action is **Try an example · no microphone**; `/app/station/` action is **Try without a microphone** and the deployed page still lacks the **Listen-only by design.** disclosure. Current repository source labels the practice button **Try invented example · no microphone**. GitHub issue [#115](https://github.com/Metivity/talk2nature/issues/115) remains open, unassigned, with 0 comments/0 reactions; its exact steps match the currently deployed copy. Changed README and CONTRIBUTING to name the no-microphone practice action by purpose, and adjusted the regression to assert placement/order while keeping source-specific control labels checked against templates. `test_site.py`: **109/109**; candidate noindex build checker: **163 HTML / 11,303 links**; public-format checker: **163 HTML / 11,466 links / 162 reachable routes**; `git diff --check` passes. No external contact or deployment; no inference of user uptake. Keep issue #115 copy synced to the deployed revision until a Pages release is verified.

## October 31 continuation — keep the researcher guide synchronized with public main

Re-ran the clean-clone kit as recorded above and replaced the guide's older “latest check” with exact evidence from current public `main`. The candidate also builds after the documentation change: the site-test module passes **109/109**, the noindex checker reports **163 HTML / 11,303 links**, and the explicit-origin checker reports **163 HTML / 11,466 links / 162 reachable public routes**. This candidate's eight route additions are distinct from public `main`'s five; all **154** deployed sitemap routes remain. The candidate is still a local commit on `codex/route-reconcile-cc30c`, unpushed and undeployed. No device, screen-reader, independent-user or scientific validation is implied.

## October 31 continuation — re-run the public researcher kit from a clean clone

Cloned the current public `main` at `cc30c724753c83233d4b5a42f805a73235c2ac3f` with depth 1, without installing dependencies, then ran every command in `docs/RESEARCHER_START.md`. The synthetic annotation report and standard/dyadic split counts and hashes matched the documented output. Full Python **243 passed, 1 skipped**, Node **167/167**; collection validator **291 valid resources**. Local noindex build: **159 pages + 404**, **160 HTML / 10,974 links**. Explicit-origin build: **159 pages + 404**, **160 HTML / 11,134 links / 159 reachable public routes**. TLS-verified sitemap comparison retained all **154 live routes** and found five new research routes in the candidate. Generated outputs were removed and the fresh clone's tracked tree is clean. Updated [`docs/RESEARCHER_START.md`](RESEARCHER_START.md) with the run. This is a maintainer rerun of invented fixtures, not an independent contribution, user adoption or scientific validation. No push, external contact or deployment occurred.

## October 31 continuation — reconcile from current public main without losing routes

Compared three states separately: the dirty local WIP (`4d140ec`), the current public source at `cc30c72`, and the deployed sitemap. A clean clone of public `main` builds **159 routes**; it contains every one of the live **154** URLs and adds five research routes (Arbimon workflow, BeVo, BORIS, DCASE and animal-agency/ethics). The local WIP's **82-route** build is stale and would omit 77 live routes; it is not the integration or deployment base. Do not infer live-route gaps from that WIP when a clean current-main source exists.

Created the local review branch `codex/route-reconcile-cc30c` from `cc30c72`, then merged in 3 local-only research notes, 17 unique source records and 19 unique resource records without replacing any current-main records. Added a browser Station keyboard-focus fix: move focus to Stop before awaiting permission/startup, and restore focus to the visible heading after cancel/failure before a session exists. The candidate must pass the project/catalog/site checks and route comparison before it can be considered for release. No publication or deployment occurred.

**Candidate checks:** Node **170/170**; Python **243 passed, 1 skipped**; collection validator **310 valid resources**; local noindex build **162 pages + 404**, checker **163 HTML / 11,303 links**; explicit-origin public build **162 pages + 404**, checker **163 HTML / 11,466 links / 162 reachable routes**; `git diff --check` passes. New Station UI behavior tests hold mocked microphone permission pending, cancel it, verify the late grant remains cancelled, and check focus restoration after both cancel and denial; the fixture cannot call a real microphone. Compared candidate sitemap against the live sitemap over verified HTTPS: all **154/154** live routes are retained, with **8** added research routes. Adding the source-cited coarse Arctic region anchors updates the candidate atlas to **47 mapped notes / 51 places**. These checks cover source, mocked behavior, metadata, generated pages and links; they are not a physical-phone, screen-reader, independent-novice or scientific acceptance test. Candidate is committed locally on `codex/route-reconcile-cc30c`; it has not been pushed or deployed. **Next:** complete named-device zero-command review when available; then review this candidate and use the authorized manual Pages flow only after release review. No deployment occurred.

## October 31 post-merge readback — source checks green; Pages not updated

PR [#613](https://github.com/Metivity/talk2nature/pull/613) merged to `main` as `622a4095c857b81a1eb4af972e2b35a6b8ecd999`. GitHub Actions run [#41170094342](https://github.com/Metivity/talk2nature/actions/runs/41170094342) completed successfully; repository, browser-tool, Android and preview-site jobs all passed. A fresh TLS-verified live check still fails at `/app/station/` on the missing **Listen-only by design.** disclosure, confirming Pages has not published the change. No workflow dispatch or deployment occurred. The manual Pages workflow has no dispatch action in the connected GitHub tool. Next: dispatch the manual workflow from an action-capable authorized Metivity session, then verify the live route. Physical-device and independent-novice acceptance remain open.

## October 31 continuation — verify Zero Command copy after deployment

Extended the live Pages verifier to check the phone app's primary invented/no-microphone action, the Station's listen-only and explicit Start/Stop disclosure, and the `/app/station/` route's SEO metadata. Added regressions for stale first-action copy and missing Station disclosure. Focused tests passed **8/8**; full Python **241 passed, 1 skipped**; Node **167 passed**. The public-format build has **159 pages plus 404** and the site checker reports **160 HTML / 11,135 links / 159 reachable public routes**. The stronger verifier passes on the generated candidate.

Fresh live HTTP readback shows `/app/` has the correct invented-example primary action but `/app/station/` still lacks the required disclosure; the live check therefore fails on that route. An open installed-app tab showed an update-available notice and older home copy, a separate cached view. No deployment, recording or animal interaction occurred. Next: publish clean `main` via the authorized Metivity Pages workflow when its session is available, then require the live verifier to pass. Named-device and independent-novice acceptance remain open.

## October 31 follow-up — assert the initial Zero Command control state

Extended `scripts/check_live_site.py` to check the deployed Station's initial controls: the recording-permission checkbox must be unchecked, microphone Start must be disabled, and the enabled practice action must say **Try invented example · no microphone**. Added regression cases for a checked permission, enabled microphone Start and missing/renamed practice action. This verifies the static first-load HTML state; it does not validate JavaScript behavior, OS permission behavior or an actual phone.

**Verification:** full Python suite **243 passed, 1 skipped**; Node suite **167/167**; public build **159 pages plus 404**; site checker **160 HTML / 11,135 links / 159 reachable public pages**; route-backed post-deploy verifier passed on the generated candidate; `git diff --check` passed. A TLS-verified direct fetch of the live Station still serves the old copy and fails the updated disclosure contract. No deployment, microphone, recording, animal interaction or external contact occurred. The candidate is in a clean-main-based worktree; the five-track goal remains active.

Read-only accessibility-tree inspection of the deployed Companion and demo routes showed Ready state, Whole moment selected, permission unchecked, microphone Start disabled and the synthetic rehearsal available; no action was activated. The deployed button still says **Try without a microphone**. An already-open app tab displayed an update-ready notice, consistent with a cached shell. This is desktop browser evidence only.

**Next:** dispatch the manual Pages workflow from the authorized Metivity session, then read back the workflow result and live Station route. The connected GitHub plugin can inspect the repository but does not expose workflow dispatch, and the current local CLI is not authenticated for the authorized publishing identity. No run was started. Physical-device and independent-novice acceptance remain open.

## October 31 continuation — reaffirm Zero Command and keep the goal active

Zero Command is the default Field Companion posture: user-started passive observation, an invented first action requiring no microphone, no animal-directed sound, no inferred reply, and no silent upload or research admission. The five-track project goal remains **active**. Next is a named-device no-animal rehearsal followed by an independent novice walkthrough; neither is complete yet. Use invented material only and preserve the real-data and AutoResearch **NOT READY** gates.

## October 31 continuation — repair project-status heading order

Moved the single top-level heading ahead of the dated status sections. This is a documentation-structure correction; the recorded test, merge and deployment evidence is unchanged.

## October 31 post-merge release state

## October 31 continuation — add the animal-agency research note


The current-main source-ID collision was resolved before publication: local source IDs 535–538 belong to different BeVo/BORIS records on `main`, so the ethics note now references new IDs 548–551. Added `interspecies-communication-ethics-review-2026` and its four source records. The note states the targeted review depth, component rights and limits; it distinguishes PREPARE planning, ARRIVE reporting and the EU directive's defined scope from any Talk2Nature approval. No dataset, code, model, participant observation or recording is included. The dirty divergent checkout was not modified.

**Checks:** Python **239 passed, 1 skipped**; Node **167 passed**. The local noindex build produced **159 pages plus 404**; checker validated **160 HTML / 10,974 links**. The explicit-origin public-mode build produced **159 pages plus 404**; checker validated **160 HTML / 11,135 links / 159 reachable public pages**. `git diff --check` passed. These are generated artifacts and tests; no live deployment or public indexing is claimed.

**Next:** keep the note as context for a future species-specific welfare/methods review; it does not approve a parrot study. Continue the zero-command product track and preserve the real-data admission gate.


PR [#608](https://github.com/Metivity/talk2nature/pull/608) merged as `febd5de157ab7b409a23010e4bf6c270e0e7c094`. Post-merge Public checks run [#41163242087](https://github.com/Metivity/talk2nature/actions/runs/41163242087) passed all jobs. The static GitHub Pages workflow remains manual (`workflow_dispatch`); no deploy run followed the merge.

Fresh live readback of `/app/station/` returns HTTP 200 but still shows the previous `Try without a microphone` action. The source update and tests are merged; the public website has not yet been updated. Next: run the manual Pages workflow, then check live route preservation, Station copy, the four candidate research pages, sitemap and crawl metadata. Do not equate a merged PR with a deployment. Named physical-device and independent novice acceptance remain open.

---

## October 31 — Zero Command and Arbimon governance decision

Reviewed the official RFCx Arbimon privacy policy and terms. The published policy states submitted audio/annotations/metadata may train ML models, future submissions can be opted out but existing model effects cannot be extracted, and annotations/labels may be kept indefinitely. The terms describe a perpetual, irrevocable submitted-content license plus competitor-use and organization-disclosure clauses. Applicability to Talk2Nature/Raviv remains unresolved; this is a policy-text summary, not a legal determination.

**Decision:** Arbimon is prior-art documentation only. No account, competitive benchmark/product-development use, connector or project-data handoff until an authorized review resolves the terms and any written disclosure/permission. Keep Zero Command local-first and portable. Sources 546–547 and the Arbimon note/resource now carry the policy review. No account, upload, recording, analysis, legal review or partner contact occurred.

**Next acceptance gate:** named-device, no-animal rehearsal of the microphone-free example and explicit Start/Stop, interruption, local save/reopen/discard, no silent resume and device/OS cues. Record exact device/OS/revision; do not infer physical-phone or novice acceptance from source or emulator tests. Real-data admission and AutoResearch remain **NOT READY**.

---


## October 31 continuation — check the current public release candidate

Built the local branch for `https://metivity.github.io/talk2nature` and ran the site checker: **158 public pages plus 404**, **159 HTML documents / 11,059 links / 158 reachable public pages**. Compared `dist/sitemap.xml` with a fresh TLS-fetched live sitemap: all **154 current URLs are preserved**, and four candidate note routes are new (Arbimon, BORIS, BeVo and DCASE). Fresh TLS GETs returned **200** for the live home and resource directory, but **404** for all four candidate note routes. The public resource directory's current search result reports 284 records, while the local candidate directory contains 291. The candidate is local-only; no branch push, merge or Pages deployment occurred. Live app readback still shows the control labels from public `main`, matching good-first-use issue #115; GitHub confirms that issue remains open with **zero public comments**. This is not evidence of Google indexing or of the reason no report has arrived. Search Console URL Inspection remains an authenticated follow-up. Keep the walkthrough issue text synchronized only to the version people can currently use. Goal remains **active**.

## October 31 continuation — keep example notes observation-neutral

The shared-animal mobile Station's optional placeholder previously linked movement to a person speaking. Replaced it with “The animal changed position. The reason is unknown.” and updated the scenario regression. On the local rebuilt site, headless Chromium at **390 × 844** showed the Zero Command notice, no horizontal overflow, unchecked recording permission and disabled Start; instrumentation counted **zero microphone calls, zero playback calls and only local-origin requests**. Screenshot reviewed. No capture or playback started; no animal or participant data involved. This is not physical-device or independent-user acceptance. **Checks:** Node **167/167**; Python **239 passed, 1 skipped**; catalog **291 valid**; local noindex build **158 pages plus 404**; site checker **159 HTML / 10,899 links**; `git diff --check` passed. Full Python suite initially exposed an unsupported new research-purpose value; changed it to the established interoperability category and reran successfully. Goal remains **active**; named-device acceptance and external university workflow remain open. No push, merge or deployment.

## October 31 continuation — record Arbimon as an existing research destination

Added official Arbimon source records 542–545, the metadata-only resource `arbimon-hosted-platform-workflow-2026`, a public research note and a researcher-start boundary. The cited documentation covers collaborative project/site organization, passive-audio uploads, analysis, validation, insight publication, one-minute segmentation by the desktop uploader and project backup contents/exclusions. Decision: retain Zero Command as user-started passive, local-first capture; evaluate only an explicit human-controlled researcher handoff if a concrete workflow is supplied. No Arbimon account, application, API, recording, backup or upload was tested; privacy/terms and institutional approval remain unreviewed. **Source-level product check:** the browser capture worklet zeros speaker output; no speech-synthesis/generated-call API was found in the searched web assets; recorded-audio review is explicit, confirmation-gated and warns to use headphones or move away from animals. This is not proof of OS or hardware silence and is not device acceptance. **Checks:** 291 resources validate; local noindex build **158 pages plus 404**; site checker **159 HTML documents / 10,899 links**; new note appears in the generated research index and route; `git diff --check` passed. Unit suites were not run for this documentation/catalog change. No public build, integration, contact or deployment occurred. Five-track goal remains **active**; AutoResearch and real-data server admission remain **NOT READY**. Next: validate one synthetic/rights-cleared university handoff and complete named-device zero-command checks.

## October 31 continuation — map BORIS to the researcher onboarding path

Added source records 538–541, the metadata-only resource `boris-software-v10-0-2`, an indexable research note and a BORIS preflight to `RESEARCHER_START.md`. Official sources document rich subject/ethogram/modifier, point/state and media/frame export fields. Talk2Nature's schema is narrower and its Audacity package is one-way, so no converter is claimed. The current official release/download pages say v10.0.2; the linked user guide still says v9.15.0, leaving v10 export compatibility open. No software, media, project or export was acquired, installed or tested. No partner was contacted. **Checks:** 290 metadata resources validate; Node **167 passed**; Python **239 passed, 1 skipped**; public build **157 pages plus 404**; site verifier **158 HTML pages / 10,988 links / 157 reachable public routes**; generated canonical, source citations and resource card checked; `git diff --check` passed. **Next:** keep the BORIS adapter gated on a researcher-supplied permitted sample, review Arbimon separately, and preserve AutoResearch as **NOT READY**. No deployment occurred.

## October 31 continuation — clarify zero-command control at the microphone gate

Updated the browser Station disclosure beside the recording-permission checkbox: Talk2Nature does not call, imitate or prompt animals; the person chooses when capture starts and can stop at any time; browser capture ends when the page is left. The separate microphone-free invented example remains the easiest first action. Updated regression checks and the zero-command rule to keep this wording at the decision point.

**Verification:** focused zero-command and Station UI tests passed **11/11**; all **167 Node tests passed**; Python reported **239 passed, 1 skipped**. The explicit-origin public build produced **156 pages plus 404**. The site checker validated **157 HTML pages / 10,916 links / 156 reachable public routes**. Chromium emulation at **390 × 844 CSS pixels** confirmed the full setup disclosure, the unchecked permission state and disabled Start action, with no horizontal overflow. This is emulation, not physical-device, screen-reader or newcomer evidence. No microphone was requested; no capture or playback occurred. No push, merge or deployment was made.

## October 31 continuation — add BeVo generation study and data rights

Added BeVo source records, a website research note and separate paper/dataset metadata records after reviewing the arXiv v1 preprint, official project page, Hugging Face dataset card/revision, LICENSE notice and source-license metadata. The review distinguishes anchor-level text-conditioned acoustic generation from event-level behavior labels, comprehension or animal response, and records the dataset's mixed component rights. No audio, code, weights or generated sample was acquired, executed or played. **Checks:** JSON parsed; Python **239 passed, 1 skipped**; Node **167 passed**; public build **156 pages plus 404**; site checker **157 HTML pages / 10,916 links / 156 reachable public routes**; `git diff --check` passed. Model execution and AutoResearch remain **NOT READY**.

## October 31 continuation — verify native Android permission-denial behavior

On public-main source revision `d3d3114`, native core checks passed; focused native/zero-command Node tests passed **19/19**; Gradle `lintDebug`, debug APK and release APK builds succeeded (**88 tasks**); and the release-boundary verifier passed (microphone-only permissions, no network/debug permission or debug receiver, backup disabled). Installed the debug APK on a newly created Pixel 6 API 34 AVD with audio disabled. Start was disabled before consent. After consent and Start, the notification prompt appeared first. Both denial paths were checked: denying notifications returned a recovery dialog and left the station Ready; allowing notifications and then denying microphone access showed “Microphone access is off” and “Nothing started or was saved.” In the latter path, Android reported `RECORD_AUDIO: ignore`, the station returned to “Ready when you are” after “Not now,” and the private app files directory contained no session files. Neither path granted microphone access or created a recording.

This is isolated-emulator evidence, not physical-device validation. We did not grant microphone access or create a recording. Native lifecycle under granted permissions, interruptions, device-specific OS cues, long-duration reliability and real-phone usability remain unverified. The active five-track goal remains open, with zero-command observation and no animal-directed output carried forward as product acceptance rules.

## October 31 continuation — clarify the native Android practice action

Aligned the native welcome button with the browser and contributor language: **Try invented example · no microphone**. Its helper now says it opens an invented browser example, includes no animal audio, needs internet and does not start native capture. Added a regression assertion for the route and no-capture behavior. Focused zero-command Node tests passed **12/12**; Android core checks passed; Gradle `lintDebug` and `assembleDebug` succeeded (**45 tasks**). An isolated Pixel 6 API 34 emulator at 1080 × 2400 showed the complete label/helper with no clipping. Audio was disabled, `RECORD_AUDIO` remained ignored, no `CaptureService` was running and no session files were present. The control was not tapped, so linked-browser behavior was not tested. Physical-device and independent-novice acceptance remain open.

## October 31 continuation — clarify the invented phone-first action

On a clean branch from current public `main` (`d3d3114`), changed the Station's invented-practice button from “Try without a microphone” to **Try invented example · no microphone** and synchronized its helper, generated contribution page and regression check. The README and contributor walkthrough already use the exact label. Linked the existing zero-command rule from the README and specified the invented/no-microphone text as a release acceptance rule.

**Checks:** focused Node tests **17/17**; Python **239 passed, 1 skipped**; noindex build **155 pages plus 404**; site checker **156 HTML documents / 10,691 links**; `git diff --check` passed. Chromium emulation at 390 × 844 CSS px measured 390px viewport/document/body widths and a 296px button, with no horizontal overflow. A pointer-driven invented session reached the recording state with microphone permission unchecked; Stop returned to local review. Instrumentation recorded zero microphone calls, media playback calls and off-origin requests. This does not establish physical-device or independent novice usability. No animal, biological recording, microphone capture or playback was used. This local branch was not pushed, merged or deployed.

## October 31 continuation — document DCASE task candidate and mobile dock fix

Added four primary-source records (531–534), one research note and one metadata-only resource for DCASE 2018 Task 3. Updated the model/data decision to distinguish a narrow binary presence-detection question from a selected dataset or communication claim. The official task page, Stowell et al. (2019), the BirdVox v2 record, the evaluation-data record and baseline README were reviewed. Label provenance is mixed, the evaluation-record license field is blank despite the challenge-level CC BY 4.0 statement, evaluation labels are absent from the reviewed deposit, and baseline code licensing remains unverified. No third-party media/code/weights were acquired or run; AutoResearch and real-data admission stay **NOT READY**.

A rendered 390 × 844 browser check exposed fixed mobile navigation over the research-note introduction. The site now hides the dock when it overlaps visible content and restores it for keyboard focus. Full suites pass: Python **239 passed / 1 skipped**, Node **167 passed**. The local noindex build has **155 pages plus 404**; the site checker validates **156 HTML documents and 10,847 links**; resource validation reports **287 valid**. `git diff --check` passes.

This is unmerged work on `codex/dcase-bird-presence-evidence`, based on public `main` `5e38f0932f0875ff808c4ee93f4d24b7ad216e04`; no push, merge or deployment occurred. Browser emulation is not physical-device acceptance or expert review. Next gate: qualified review before dataset acquisition, with named iPhone/Android checks still open.

> Additional status history is preserved in [STATUS_HISTORY.md](STATUS_HISTORY.md).

## October 30 — keep the active status record manageable

**Question:** can the cumulative status log stay readable and be moved through repository review tools without dropping evidence?

**Change and verification:** split the 1.35 MB log at a dated section boundary. `STATUS.md` is now about 701 KB and `STATUS_HISTORY.md` about 651 KB. All 734 dated section headers and their text remain in order across the two files. The current file links directly to the archive; a regression checks that archive and its reviewer-path evidence remain discoverable.

**Limit:** historical entries retain their original dates and document the state at that time; readers should use the newest entries for current status.

## October 30 — verify live crawl metadata and public discovery

**Question:** do the current live project routes expose the intended crawl metadata, and can a public web search find useful research content?

**Live check:** `scripts/check_live_site.py` passed with certificate validation enabled using the installed `certifi` bundle. It verified the homepage, `/app/` and `/research/resources/`: each has one non-empty title and description, an exact self-canonical URL and `index,follow`; the sitemap contains 154 routes; and `robots.txt` names that sitemap without a global disallow. The default Python trust store initially rejected the certificate; the run succeeded after pointing Python to the local CA bundle, without disabling TLS checks.

**Discovery check and limits:** a web search for Talk2Nature surfaced the [homepage](https://metivity.github.io/talk2nature/), [resource library](https://metivity.github.io/talk2nature/research/resources/), [research frontiers](https://metivity.github.io/talk2nature/research/frontiers/), [starting-points guide](https://metivity.github.io/talk2nature/research/starting-points/) and [research atlas](https://metivity.github.io/talk2nature/research/atlas/); several results carried recent crawl dates. This confirms that those pages are discoverable through the search tool, not that the whole site is indexed or ranked by Google. The available Google Search Console browser tab is signed out, so impressions, submitted sitemap state and URL-level Google indexing remain unverified. Do not treat crawlability or search snippets as adoption evidence.

**Next:** inspect Search Console for the verified property when authenticated access is available; compare sitemap discovery and sampled URL-indexing status, and record the retrieval date and exact scope. The site-wide technical check is a pass; property-level search performance remains open.

## October 30 — rerun zero-command candidate release checks

**Question:** does the local zero-command candidate still pass the repository's complete software and public-site gates, without dropping routes already on the live site?

**Verification:** after refreshing `origin/main` (still `28aba4b`), the candidate remained a direct descendant. All 239 Python tests passed (one intentional skip); all 165 Node tests passed. Regression coverage associates the listen-only explanation with the disabled/permission-gated Start button and confirms every referenced description ID exists in the rendered page. The explicit-origin public build produced 154 pages plus 404; `scripts/check_site.py` validated 155 HTML documents and 10,771 links. A live sitemap comparison preserved all 154 current routes with no unexpected additions or losses. `git diff --check` passed.

**Limits and next:** these are local source/build checks plus a read-only live sitemap fetch. The branch has not been pushed, merged or deployed. The new accessible-description relationship is source-verified, not a screen-reader result. Prior browser-emulation checks do not establish named-phone behavior, operating-system cues or independent comprehension. Continue the named iPhone/Safari and Android/Chrome no-animal walkthroughs and keep the authorized newcomer gate open. The five-track program goal remains active; real-data admission and AutoResearch remain **NOT READY**.

## October 30 — include BirdPark in the benchmark candidate comparison

**Question:** does BirdPark's multimodal zebra-finch system provide a suitable first benchmark task?

**Evidence:** used the current targeted PeerJ methods/data review and exact Zenodo v1/v2 record metadata already cataloged. The paper's evaluated 28 minutes (2,677 vocalizations) are a subset of the 112-minute v2-described deposit, but selected source file IDs/windows are not mapped. Some microphone-only caller labels are guesses based on repertoire/noise; both Zenodo pages display no dataset license. The BirdRadio GPL notice is limited to its reviewed subproject; the full collection and related media terms remain unresolved.

**Change and decision:** added BirdPark as Candidate G in the comparison run card, covering event segmentation/caller attribution only. It remains a metadata-only methods reference, not a behavior/meaning/receiver-response benchmark. Added its specific reviewer requirement and source links. No media, code or model was acquired or run.

**Validation:** checked the candidate-card comparison count and cross-references, reviewed `git diff --check`, and retained the **NOT READY** AutoResearch status. No benchmark is selected or training-ready.

**Next:** resolve rights and exact sample membership, then obtain independent avian annotation and ML/statistical review through an authorized route before any data acquisition or model work.

## October 30 — distinguish call intervals from behavioral replies in a parrot dataset

**Question:** does a dataset field named “Response Time” establish that one bird answered another?

**Evidence:** refreshed the official [Dryad record](https://doi.org/10.5061/dryad.rn8pk0prb), its README description and Dryad’s [reuse guide](https://datadryad.org/help/guides/reuse). The README defines `Response Time(s)` as the interval between consecutive call onsets. The small deposit contains a README and measurement workbook, not the source recordings; workbook rows and pair identifiers were not inspected. Dryad’s repository-wide guide states CC0, but the publisher article and supplementary files have separate terms.

**Change and decision:** updated the source/resource catalog and public evidence note to say the timing field is an acoustic interval, not a verified behavioral response. Keep this paper as a methods reference for sequence structure; it is not a decoded-meaning or first-ML benchmark. The compact workbook remains metadata-only while pair identifiers and sensitive-species context await specialist-led review. No files, media or code were acquired or run.

**Validation:** all 238 Python tests passed (one skipped); the focused zero-command copy tests passed (2/2); the 286-resource catalog validated; the local noindex build produced 154 pages plus 404 and passed 155 HTML documents / 10,616 links. AutoResearch and real-data admission remain **NOT READY**.

**Next:** preserve the existing ArcticBirdSounds reviewer gate and continue zero-command named-phone checks when devices are available. No independent review, workbook inspection or model result is claimed.

## October 30 — reconcile BirdPark dataset versions and benchmark scope

**Question:** are the PeerJ evaluation's 28 minutes and the 112 minutes on Zenodo v2 inconsistent, and what labels does this support?

**Primary sources:** read the peer-reviewed PMC article's relevant full-text sections, exact Zenodo 7105196 v1 and 13144875 v2 records and version link, and the official BirdRadio subproject license page. The article's Data Availability statement cites v1 for raw data/annotations and v2 for MP4/HDF5. Its Methods/Table 2 describe 2 × 7-minute pair files plus fourteen one-minute samples across the four- and eight-bird experiments: 28 minutes total from the four experiment conditions represented by the 112-minute deposit. The aggregate discrepancy is resolved as a subset, but selected file IDs/windows were not mapped. Some caller identities for microphone-only segments are guessed using repertoire and noise, so these labels need an independence review before benchmark use.

Added the Zenodo v1 dataset and BirdRadio code subproject as separate metadata-only resources; the BirdRadio GPL-3.0-or-later notice is scoped only to that subproject and its unpinned `dev` branch. Both Zenodo v1/v2 pages display no dataset license. The separately reviewed annotator pack and ETH dataset remain separate records with prior October 24 review dates; their overlap with the v1/v2 chain remains unverified. No third-party data, media or code was acquired or run. The catalog now contains 286 resources.

**Validation:** all 165 Node tests pass; all 238 Python tests pass (one skipped); the catalog accepts 286 resources; the local noindex build produced 154 pages plus 404 and passed 155 HTML documents / 10,616 links; the explicit-origin public build passed 154 reachable routes, 155 HTML documents / 10,771 links; `git diff --check` passes. AutoResearch and data admission remain **NOT READY**.

**Next:** seek qualified avian-bioacoustics and ML/statistical review, resolve component rights and exact sample-to-file mapping, then determine whether an animal/group-held-out event/source task is defensible. If not, retain BirdPark as methods context only.

## October 30 — make zero-command the active Field Companion product contract

Raviv asked to continue along the zero-command direction and keep the project goal active. Clarified the milestone in `GOAL.md` and added explicit acceptance gates to `ZERO_COMMAND.md`: the invented no-microphone path leads; recording is optional and deliberate; examples, observations and predictions stay distinct; Stop/discard/export behavior is verified with invented material; and named-device and newcomer checks remain open until directly observed. The five-track program goal remains active, with zero-command as the current Field Companion milestone.

**Current evidence and limits:** the existing public source has regression coverage for the microphone-free first action and practice flow. This candidate adds the clearer permission-label/muted-state and example-only placeholder improvements, with regression and browser-emulation checks recorded above. This does not establish physical-device silence, device reliability or newcomer comprehension. No animal or bystander recording was made; no new public deployment occurred.

**Next:** work through the remaining no-animal iPhone/Safari and Android/Chrome save/reopen, Stop and interruption checks when the named devices are available; seek a separately authorized newcomer walkthrough; continue tightening only a specific friction point evidenced by those checks. Keep AutoResearch and real-data admission **NOT READY**.

## October 30 — refresh contributor feedback state

**Question:** has the public beginner task received an independently reported phone walkthrough?

**Read-back:** using the connected Metivity GitHub account, [issue #115](https://github.com/Metivity/talk2nature/issues/115) is still open, labeled `good first issue` and `help wanted`, with zero comments. GitHub reports its last update at `2026-10-30T19:10:40Z`; no walkthrough report is present. The issue asks only for device family/browser, task completion, pause point and one clarity suggestion, and warns not to share recordings or personal details.

**Decision and limits:** public first-use evidence remains unverified. Zero comments do not prove no private or unreported use. No invitation, message, recruitment or analytics was added. Keep the existing task and treat only reviewed outside reports as independent-use evidence.

## October 30 — clarify the disabled microphone action

**Question:** does the phone-sized Station explain why microphone capture is unavailable before the person confirms the permission declaration?

**Change:** from public-source commit `28aba4b`, created local branch `codex/zero-command-permission-20261030`. The disabled action now reads **Permission needed** and has subdued styling. Checking the permission declaration enables it and changes the label to **Start listening**; unchecking locks it again. The checkbox is an observer declaration, not proof of rights. Capture, playback and storage behavior did not change.

**Verification:** all 165 Node tests pass; Python reports 238 tests passed and one skipped. The noindex build produces 154 pages plus 404; the site checker validates 155 HTML documents and 10,588 links. Headless Chromium at 390 × 844 confirmed both permission-label/disabled states. Companion mode rendered at 320, 390 and 1440 pixels with no horizontal overflow. Outdoor, companion, parrot and synthetic-practice modes at 390 pixels all showed **Example only:**, kept the note value empty and made zero microphone calls. Across these checks there were no off-origin requests or page errors. The mobile screenshot was reviewed.

**Limits and next:** this is source, automated and desktop-browser-emulation evidence only; no physical phone, OS permission sheet, screen reader or newcomer was tested. Do not treat the permission declaration as legal or technical verification. Keep named iPhone/Safari and Android/Chrome no-animal walkthroughs open. No push, merge or deployment occurred.

**Mobile screenshot follow-up:** scenario-specific text inside the optional note box looked like a possible saved observation. Marked all four scenario placeholders **Example only:** and added a source regression that examples are placeholders rather than prefilled note values. This is a copy clarity improvement; it adds no observation and changes no capture behavior.

## October 29 — verify the live zero-command workflow at phone width

**Question:** can a visitor complete the published microphone-free Station path on a narrow viewport and reopen the exact export in Compare?

**Revision and setup:** tested the public release deployed from [`d8cfd41`](https://github.com/Metivity/talk2nature/commit/d8cfd41a2bb65874057c432ba1c735f725b1aad3) by [Pages run #40850617982](https://github.com/Metivity/talk2nature/actions/runs/40850617982). Used Python Playwright 1.57.0 with headless Chromium 145.0.7632.6 at a 390×844 CSS-pixel viewport.

**Result:** the full path completed: home → **Try an example · no microphone** → Station synthetic rehearsal → add a note → complete the 30-second window → save the ZIP → acknowledge the save → open Compare → import that same ZIP → expand **Recordings & observations**. The reopened session showed the same invented note. The ZIP metadata declares `talk2nature.observation-window.v1`, `origin=synthetic`, `duration_seconds=30`, `stop_reason=window_complete`, and a complete 1,440,000-sample window at 48 kHz. The exported note is user-entered, not a model label.

**Checks and limits:** browser instrumentation counted zero `getUserMedia` calls; the microphone permission remained `prompt`. The public origin was the only request origin, there were no page errors, and `documentElement.scrollWidth` equaled the 390-pixel viewport. The Station worklet source explicitly zeros its speaker output channels. This is headless desktop-browser emulation of the deployed page, not a physical phone, Safari, screen-reader, native-app, microphone or acoustic-output check. No animal or real recording was involved, and the downloaded synthetic ZIP stayed in temporary local storage.

**Next:** repeat the save/reopen task on named physical iPhone and Android devices. An independent newcomer walkthrough still requires Raviv's authorization before recruitment. No interface change or new deployment was made from this check.

## October 29 — set a public contribution and evaluation baseline

**Question:** does the public repository currently show independent use or contributor feedback that we can cite?

**Read-back:** the GitHub contributors endpoint lists Metivity and Dependabot, with no other account in the response. The full issue list contains only owner-authored [#115, the good-first-issue phone workflow](https://github.com/Metivity/talk2nature/issues/115). There are no submitted public first-use or workflow-reproduction reports. GitHub's [traffic endpoints](https://docs.github.com/en/rest/metrics/traffic) provide rolling aggregate clone/view counts, but those counts do not establish a human evaluator, a completed task or research use; the source and intent of an individual clone are not reported.

**Decision:** treat outside uptake as unverified. The empty report queue is an observable baseline, not proof that nobody has tried the site. Do not market clone totals or repository traffic as adoption, research impact or a successful experiment. No analytics, contact, recruitment or user data collection was added.

**Next:** after Raviv authorizes a specific invitation/recruitment step, use the existing privacy-bounded first-use or workflow-report route and count only reviewed evi…157321 tokens truncated…hysical-phone behavior. Next: obtain a small, consented first-time-user review and actual iOS/Android checks before making field-usability claims.

## October 14 — yellow-naped Amazon cultural-change record

**Question:** does the public dataset and associated code provide a rights-clear, reproducible audio benchmark for parrot communication?

**Evidence reviewed:** Dahlin et al. (2024) abstract and targeted Methods/Results passages surfaced by the PMC index; the full PMC page presented a bot check and direct publisher retrieval returned HTTP 403. Reviewed Dryad v6 landing-page/data-dictionary sections, Dryad's current CC0 policy, and the TLS-verified API record/version/file manifest. Dryad reports seven files totaling 9,970,731 bytes, including 2,461 call-level measurement rows and 56 site-year rows; the README says no restrictions on deposited data, but raw audio and roost counts are not in the archive and exact site coordinates are withheld. The version API provides SHA-256 values. The separate analysis repository is MIT at commit 1399b7a2de6354d27b5227bb75de7e285fe3d636; static review of its four R Markdown analyses found author-specific absolute paths, an unpinned latest warbleR install, archived rgdal/rgeos setup notes and missing inputs. No code was run.

**Decision and change:** added original research note yellow-naped-amazon-vocal-culture-2024, three component-specific resource records (article, Dryad dataset, GitHub code), and separate paper/data/API/policy/code source records. The note distinguishes dialect change from meaning, records within-site-year caller IDs and the group-split risk, and links the observation period to the existing country-scale Costa Rica atlas point. Article text remains all rights reserved; Dryad data are CC0; code is MIT. The paper review is not full text. Dryad API file download returned 401 and its public file-stream endpoint returned 403; no file bytes, exact site names, audio, model or participant information were collected.

**Limit and next decision:** this is a useful historical and schema reference, not a reproducible audio or communication benchmark. Full article/supplement review and independent parrot-bioacoustics/statistical assessment remain necessary before a baseline; any future file review should use the documented Dryad route and retain training_admitted=false.

**Validation:** all 142 repository Python tests pass and the resource catalog validates 144 records. The local noindex build contains 111 pages plus 404; the checker verified 112 HTML documents and 5,494 links. The explicit-origin public candidate passed with 111 reachable public pages; 112 HTML documents and 5,606 links were checked. The new page has a unique 147-character description, self-canonical, index/follow metadata, visible component-specific rights and review limits, and a sitemap entry. These candidate checks validate technical crawl setup, but do not establish Google indexing or rankings.

**Release receipt:** PR [#175](https://github.com/Metivity/talk2nature/pull/175) passed the required repository, browser-tool, native Android and preview-site checks, then merged as [`c5dd9b6`](https://github.com/Metivity/talk2nature/commit/c5dd9b6b0d015891ada1627981609de07a51c812). Manual [Pages run #38548849100](https://github.com/Metivity/talk2nature/actions/runs/38548849100) passed its public build, SEO/publish-boundary checks, deployment and live-site verifier. Separate HTTPS checks returned HTTP 200 for the research page, resource directory, sitemap and robots file; confirmed the page's self-canonical, index/follow directive, visible paper/data/code rights and 401/403 data-access limits, sitemap entry, resource-directory entry and robots sitemap directive. This verifies publication and technical crawl configuration, not Search Console discovery, indexing, ranking or independent scientific review.

## October 14 — resource directory research-use filter

**Question:** can readers narrow the growing library by the catalog's research-use assessment without mistaking a declared license or project decision for permission?

**Evidence and change:** the validated catalog contains 144 component-specific resource records. Its `rights.research_use` field currently labels 97 records conditional and 47 unresolved; it contains no “not admitted” research-use entries. Added a filter for those existing assessments and kept it composable with text search and resource type. Every entry retains its full rights scope and limitations; the filter's visible help says it is a catalog note, not permission. No species labels were inferred because the resource schema has no normalized taxon field. No third-party material or recordings were acquired.

**Validation:** all 142 Python tests and 115 Node tests passed; catalog validation accepted all 144 records. The noindex build produced 111 pages plus 404; the site checker validated 112 HTML documents and 5,494 links. The explicit-origin public candidate also passed, with 111 reachable public pages and 5,607 checked links. Headless Chrome mobile emulation at 320 × 740 and 390 × 844 CSS pixels kept document width equal to the viewport. At 320 px, selecting “Unresolved” showed 47 of 144 records; selecting “Conditional” showed 97 of 144. Desktop rendering was also inspected at 1440 px. These are maintainer-run browser checks, not physical-device, screen-reader or independent researcher testing. The candidate has not been deployed; Search Console discovery and indexing remain unknown.

**Release receipt:** PR [#177](https://github.com/Metivity/talk2nature/pull/177) passed public checks [#38551947734](https://github.com/Metivity/talk2nature/actions/runs/38551947734) and merged to `main` as [`8c3e981`](https://github.com/Metivity/talk2nature/commit/8c3e981148c25b901a162a063b58984079432d84). Manual Pages run [#38552246016](https://github.com/Metivity/talk2nature/actions/runs/38552246016) passed its public build, SEO/publish-boundary checks, deployment and live-route verifier. Separate TLS-verified HTTPS checks returned HTTP 200 for the resource directory, filter script and stylesheet, sitemap and robots file; the deployed page includes the research-use control and status attributes, and the script filters by the matching catalog field. This confirms publication and technical crawl configuration, not Search Console discovery, indexing or ranking.


## October 14 — Field Companion mobile accessibility smoke audit

**Question:** do the core Field Companion routes remain navigable and expose accessible names in a narrow mobile browser, including with keyboard focus and the browser accessibility tree?

**Review:** built the current worktree as a local noindex site and inspected `/app/`, `/app/station/?mode=parrot`, `/app/review/`, `/app/compare/` and `/app/check/` in headless Chrome with mobile viewport emulation. Checked all five routes at 390 × 844 CSS pixels and the four primary workflow routes at 320 × 740. At both widths, the tested pages matched the viewport width with no horizontal overflow. The accessibility tree exposed named interactive controls and the expected banner, main, navigation and footer landmarks; the current app destination was marked with `aria-current="page"`. Keyboard Tab reached the visible “Skip to content” link with a 3 px focus outline; Enter moved focus to `main`.

**Decision:** no reproducible defect in this bounded audit required an app-code change. The main paths remain usable in narrow browser emulation; the next validation should cover physical iOS/Android devices, VoiceOver/TalkBack and first-time user comprehension before making broader accessibility or usability claims.

**Limit:** this is a Chrome DOM/accessibility-tree and keyboard smoke check, not a WCAG conformance audit, physical-device test, screen-reader session or participant study. It used no microphone, animal media, camera, network submission or participant data. No third-party source or dataset was added or inspected.


## October 14 — EmotionalCanines evidence note and narrow-screen correction

**Question:** what does a recent dog-bark classification paper actually validate, and does the new evidence page work on very narrow phones?

**Evidence and change:** reviewed the author-hosted ACM Multimedia paper's dataset, annotation, reliability, dog-separated split, results and limits; pinned the exact Hugging Face card revision and GitHub dataset commit. Added one original research note, three source records and separate paper/dataset resource records. The paper's arousal and valence labels were assigned by people from associated video context; this is not an animal-reported emotion or evidence of call meaning. The reported dog-separated test is distinguished from 10-fold results whose grouping was unclear. Dataset and paper declarations are recorded separately; original internet-video rights, consent and privacy were not traced. No data, labels, code or weights were acquired or run.

The styled 320-pixel browser check exposed horizontal overflow from long pinned hashes in the provenance list, which sits outside the main article container. Added narrow text wrapping to article prose and the source list.

**Validation:** 143 Python tests and 115 Node tests passed; the resource catalog validates 146 records. The local noindex build has 112 pages plus 404; the site checker verified 113 HTML documents and 5,547 links. The explicit-origin public candidate also passed: 112 reachable pages, 113 HTML documents and 5,661 checked links. Headless Chrome checks at 320 × 844 and 390 × 844 CSS pixels measured document width equal to each viewport after the fix; the 320-pixel page screenshot was visually reviewed. No physical-phone, screen-reader or Search Console result is claimed. At the time of these candidate checks, PR merge and deployment were still pending; the release receipt below records the verified publication.

**Release receipt:** PR [#179](https://github.com/Metivity/talk2nature/pull/179) merged on October 14 as [`33a835c`](https://github.com/Metivity/talk2nature/commit/33a835c294fa960a54d448f3c01a28729a893658). The manual [Pages run #95](https://github.com/Metivity/talk2nature/actions/runs/38568614553) passed both build and deployment jobs, including the live-route and crawl-metadata check. A direct HTTPS fetch of the new research route returned HTTP 200 and served its unique title, self-canonical and `index,follow` metadata. This confirms publication and technical crawl setup; Google indexing and ranking remain unverified.


## October 20 — Dependabot alert reconciliation

**Question:** do the two open Requests alerts describe the current private-admin dependency pin, or an out-of-date GitHub dependency graph?

**Evidence:** GitHub's alert API still reports `admin/requirements.txt` as `requests==2.32.3` for both alerts. On `main` at `0dae76e`, `admin/requirements.txt` and `admin/requirements.lock` both pin `requests==2.34.2`. PR [#124](https://github.com/Metivity/talk2nature/pull/124) merged the patch on October 14 and added a lock-parity test. The two advisories list first patched versions 2.32.4 and 2.33.0. GitHub's Dependabot page still showed its dependency-file scan from October 14; on October 20 I requested a refresh and GitHub confirmed it was queued. Several minutes later the API still reported the old 2.32.3 requirement and unchanged alert timestamps. See [GitHub's dependency-graph troubleshooting guide](https://docs.github.com/en/enterprise-cloud@latest/code-security/reference/supply-chain-security/troubleshoot-dependabot/dependency-graph-errors) for its stale-graph refresh guidance.

**Decision and limit:** no package was changed and neither alert was dismissed. The current checked-in manifests are above the advisories' stated fixed versions, but the GitHub alert snapshot has not yet reconciled; the installed hosted runtime was not verified. Recheck after the queued scan completes. If a refreshed scan still reports 2.32.3, investigate the repository dependency graph with GitHub before changing code or closing the alerts.

## October 20 — Search Console sitemap reprocessing

**Question:** does the earlier Search Console sitemap-fetch error describe the current deployed sitemap?

**Live validation:** the verified `https://metivity.github.io/talk2nature/` Search Console property still showed an older sitemap read dated October 12 with a fetch error and zero discovered URLs. On October 20, the sitemap was resubmitted through that same property; Search Console confirmed successful submission and said it would periodically process the sitemap. Independent live checks returned HTTP 200 for `/sitemap.xml`, `/robots.txt` and `/research/resources/`. The sitemap parsed as valid XML with 112 URLs, includes the research-resource route, and matches the sitemap directive in `robots.txt`. The resource page serves its own canonical URL and `index,follow` metadata.

**Decision and limit:** no sitemap or site code change was needed. Search Console has accepted the refresh request, but its earlier fetch/index reports have not yet been shown to update. This confirms a processing request, not a completed crawl, indexing, traffic growth or ranking. Recheck the report after Google processes the submission; do not treat the older report as the current live sitemap state.

## October 20 — sitemap report and live-fetch check

**Question:** is the current Search Console sitemap error caused by Google being unable to fetch the public file?

**Evidence:** after the October 20 resubmission, the sitemap detail report showed a same-day read but still said “Sitemap could not be read,” with zero discovered pages. Google’s URL Inspection live test for the exact sitemap URL, run October 20 at 1:40 PM, reported that the URL was available to Google, crawl was allowed, page fetch succeeded, and indexing was allowed. The live-test discovery section explicitly said it was not checked. Separate HTTPS checks still return 200 for the public file, which parses as valid XML with 112 URLs. Google’s [Search Console sitemap guidance](https://support.google.com/webmasters/answer/7451001) recommends using URL Inspection to diagnose fetch failures and notes that temporary processing errors can be retried.

**Decision and limit:** the sitemap report and one-time live fetch test disagree; neither establishes that Google has processed the 112 listed page URLs. No sitemap or robots change is justified by this evidence, and the sitemap was not resubmitted again. Let Google retry, then recheck the sitemap report. If a later attempt still fails, inspect any specific error details before changing the deployed sitemap.

## October 22 — El Silencio as a cross-taxon detection candidate

**Question:** is there a useful public, multi-species dataset to ground an initial sound-analysis workflow, and what does it actually let us test?

**Evidence and change:** reviewed official Zenodo API metadata for the El Silencio labeled release (record 17064353) and separate unlabeled release (17122738), the dataset repository README and MIT license pinned to commit `5e2f7826c908fec3018740068bbdeda6c6977f35`, and only the citation/indexed excerpt for the 2025 CEUR overview paper. The labeled metadata describes 770 one-minute recordings (12.8 hours), about 15,000 acoustic-event boxes and four broad taxa. The useful initial task is sound-event detection and human-reviewed taxon/sonotype organization across species. These event labels are not behavior labels or receiver-response observations and cannot establish communication meaning. Added one original research note, four source records, three separate paper/data/repository resource entries, a link from the detection learning path, collection/license notes and a focused regression test. All downloaded-resource states remain metadata-only.

**Limits and unresolved source discrepancies:** no recording, annotation, protocol PDF, model weight or code file was downloaded, opened or executed; no checksum or baseline was reproduced. The overview excerpt says 11,340 unlabeled recordings across 63 sites while the pinned README and separate Zenodo deposit say 10,980 across 61; the difference is undocumented. The labeled Zenodo page displays 109.8 GB while its file inventory totals 3,546,609,904 bytes; this is unresolved. Record-level CC BY 4.0 does not independently settle source-recording rights, privacy or sensitive-location conditions. The repository MIT license does not license the separate recordings, and the paper's license was not verified. The full overview was not retrievable and its Spanish annotation protocol has not been reviewed. No independent bioacoustics review, participant-data intake, model run or communication benchmark is claimed.

**Validation:** all 144 Python tests and 115 Node tests passed. Local noindex and explicit public-origin builds passed; the site checker covered 114 HTML documents and 5,610 local links / 5,725 public-build links. The rendered note was inspected at desktop and phone-width viewports. This verifies the candidate page and repository behavior only, not physical-device usability, scientific validity or Search Console indexing. Next: obtain a qualified review of the exact protocol and resolve which release/version is fit for a narrowly scoped detection question before acquiring data or running a model. AutoResearch remains **NOT READY**.

**Release receipt:** PR [#186](https://github.com/Metivity/talk2nature/pull/186) merged to `main` as [`230b911`](https://github.com/Metivity/talk2nature/commit/230b9117e48c71072601d4634e4a0c91c091eae9). Manual Pages run [#39835379683](https://github.com/Metivity/talk2nature/actions/runs/39835379683) completed successfully, including the public build, SEO/publish-boundary checks, deployment and live-route/crawl-metadata verifier. A direct HTTPS request to the new route returned HTTP 200 and the deployed page was inspected in a phone-width browser. This confirms publication and technical crawl setup only; Google discovery, indexing and ranking remain unknown.

## October 22 follow-up — complete El Silencio methods review

**Supersedes the partial-review checkpoint above:** read the full 11-page BirdCLEF+ overview and all extractable Spanish text (pages 2-18) from the annotation protocol pinned to dataset commit `5e2f7826c908fec3018740068bbdeda6c6977f35`. The paper describes 770 labeled one-minute soundscapes and about 15,000 event boxes; the manual protocol records acoustic Group/Label/SongType and groups same-species signals separated by no more than one second. These are detection/taxonomic descriptors, not behavior, receiver response or meaning. The competition's 38,000-plus labeled clips, 705 soundscape tests and classification result belong to a separate BirdCLEF+ dataset/task. The four taxa described by the paper do not map cleanly to the protocol's visible bird/anuran/insect group codes; no inter-annotator reliability measure was reported in the reviewed paper/protocol. Specialist review remains necessary.

Updated the public note, source record 331, added pinned protocol source 332, corrected the paper's CC BY 4.0 declaration, and refreshed three metadata-only resource records. The protocol repository's MIT license applies to repository documentation, not automatically to recordings/labels. The 11,340/63 versus 10,980/61 release count and labeled-record page/API size discrepancy remain unexplained. Source-media rights, consent/privacy, human-audio handling and site grouping are not cleared. Only the paper and protocol review copies are retained locally outside the public site; no dataset audio, annotations, model weights or code were acquired or run.

**Jev decision:** recorded an evidence-bounded architecture note in `docs/MODEL_DATA_DECISION.md`. If a future metadata backlog warrants it, Jev may suggest categories for a human-review queue; it does not crawl sources or supply scientific truth. No API call, model test or product integration was made.

**Validation:** 144 Python tests and 115 Node tests passed; the El Silencio and resource-directory regressions also passed after the final copy edit. The local noindex build passed with 114 HTML documents and 5,614 links; the explicit public-origin candidate passed with 114 HTML documents, 5,729 checked links and all 113 public routes reachable. The page was visually inspected at CSS viewport widths 1440 and 390; the mobile page had no horizontal overflow (390px document width), kept the bottom navigation within the viewport, and displayed all five source links. These are browser-emulated layout checks, not physical-phone or independent scientific validation. At the point this candidate review was recorded, it was not yet deployed; the release receipt below records subsequent publication.

**Release receipt:** PR [#188](https://github.com/Metivity/talk2nature/pull/188) merged to `main` as [`fec96fc`](https://github.com/Metivity/talk2nature/commit/fec96fc6e594ccd654ae1438b8786f61dbfdfe4c). Manual Pages run [#39846851474](https://github.com/Metivity/talk2nature/actions/runs/39846851474) completed successfully, including all repository tests, public build, SEO and publish-boundary checks, deployment and live-route/crawl-metadata verification. The research page returned HTTP 200; its live title, canonical URL, schema metadata and cited protocol link were verified. This confirms technical publication only; search discovery, indexing and ranking remain unknown.

## October 22 — current public-main clean-clone verification

**Question:** do the public README/researcher-kit workflows still reproduce from the latest public source without maintainer-only files?

**Evidence and validation:** cloned public `main` at [`f13335f4a1def93492159c26d4eae61358af7597`](https://github.com/Metivity/talk2nature/commit/f13335f4a1def93492159c26d4eae61358af7597) into a fresh depth-one checkout. Python 3.12.5, Node v22.22.1 and Git 2.53.0; no packages installed. The clone stayed clean after the run. Synthetic annotation and split examples matched the documented shape; the split had 10 groups and 12/4/4 records, both labels in every partition, and the documented output SHA-256 `814ccb3495156ef56ae43ccfe79faa4584843402c90d0d30462df93a52ebb35b`. Catalog validation accepted 149 resources. All 144 Python and 115 Node tests passed. Local noindex build/check: 113 pages plus 404, 114 HTML documents and 5,614 links. Explicit public-origin build/check: 113 pages plus 404, 114 HTML documents, 5,729 links and all 113 public routes reachable. Full details are in `docs/RESEARCHER_START.md`.

**Jev fit:** no Talk2Nature API call or product integration is justified now. A future, bounded metadata-only suggestion queue could be tested against human-reviewed source records if triage volume becomes a real bottleneck; typed outputs do not establish scientific correctness. Source access, rights and expert review remain the current constraints. See `docs/MODEL_DATA_DECISION.md`; no provider call was made.

**Limit:** this is maintainer-run software verification, not an independent reproduction, first-time user test, scientific review or biological result. Fixtures are synthetic. No third-party research media, labels, code or model was acquired or run. The independent reproduction count remains zero. No research benchmark gate changed; AutoResearch remains **NOT READY**.

## October 22 — Search Console discovery and indexing baseline

**Question:** is the newly released research note discoverable in Google, and what does Search Console say about current reach?

**Live website checks:** HTTPS requests to /sitemap.xml and /robots.txt returned HTTP 200. The sitemap parsed as valid XML with 113 URLs, includes the El Silencio research page, and the robots file names that sitemap.

**Search Console evidence:** the verified Talk2Nature property’s Web performance report, last updated about 4.5 hours before inspection, covers Sep 29–Oct 20, 2026: 37 impressions, 0 clicks, 0% CTR and average position 6.7. The top-page table shows 29 impressions for /research/resources/, 7 for /research/ and 1 for the homepage. This is a small current baseline, not proof of broad discovery or growth.

The sitemap report still says /sitemap.xml was last read Oct 20, status “Couldn't fetch,” with zero discovered pages. The separate live sitemap and robots checks above pass. URL Inspection for the El Silencio note reports “URL is not on Google” and “URL is unknown to Google,” with no referring sitemap detected. Its Oct 22 live test says the page is available to Google, crawl allowed, page fetch successful, indexing allowed, and the user-declared canonical matches the public URL. Discovery was explicitly “Not checked in live tests.” The Pages coverage report is stale (last update Oct 16) and internally inconsistent: it shows 5 indexed / 0 not indexed in one summary, while listing a one-page “Crawled - currently not indexed” reason whose drilldown shows 0 affected pages. Do not treat that report as a current page-by-page census.

**Action and limit:** attempted the URL Inspection indexing request for the public El Silencio page after the successful live test. Search Console reported it could not connect to its reCAPTCHA service; no request confirmation appeared, so no indexing request is claimed as submitted. No CAPTCHA was solved or bypassed. The page remains unindexed in the available index report. Retry only when the owner UI can complete its verification, then recheck the sitemap report and URL status; do not infer indexing from a successful live fetch. Search Console reporting and request state are separate from the verified deployment.

## October 22 — Central European Birds v1.1 added as a metadata-only detector candidate

**Question:** is there a substantially larger bird dataset that can help test sound-detection technology, and does it supply communication evidence?

**Evidence reviewed:** the current official Zenodo record 21821133 (v1.1, published 2026-08-06), its v1.1 change notes, published file inventory and official `schema.json` browser preview. The earlier record 20762099 is superseded. No audio, annotation CSV, code or model weights were acquired or run.

**Finding:** CEB v1.1 lists 20,826 recordings, 92,857 event annotations, 256 eBird species codes and 21 vocalization types across a 49.7 GB package. Its soundscape subsets are useful candidates for event detection, species/type classification and localization. They do not include independently observed receiver response or ground truth about meaning. The dataset is bird-focused but not a parrot context corpus; keep it separate from the proposed companion-parrot observation study.

**Rights and quality limits:** the record declares CC BY 4.0 for soundscape audio and dataset metadata/annotations. `train_xenocanto` retains source-record licenses, and the schema says some of those fields are empty. Version 1.1 marks 40 zero-area annotations unsuitable for detection/localization and documents one truncated Xeno-Canto file. Its test labels are public, so if examined for development, reserve a separate untouched evaluation. No per-row license review, group/source-overlap audit or qualified specialist review was performed.

**Change and validation:** added source 333, a source-linked public research note and dataset resource, and a detection-path link. The note records the v1.1 release and remains metadata-only. All 144 Python tests and 115 Node tests passed; the catalog validates 150 resources. The local noindex build checked 115 HTML pages and 5,655 links; the public-origin build checked 115 HTML pages, 5,771 links and 114 reachable public routes. The new page was visually reviewed in a desktop browser. No independent reproduction, data acquisition, model run, publication or deployment is claimed here; AutoResearch remains **NOT READY**.

**Release receipt — October 23:** PR [#192](https://github.com/Metivity/talk2nature/pull/192) merged to `main` as [`6d42e1c`](https://github.com/Metivity/talk2nature/commit/6d42e1cd78ecacb07383b6584fe62a5c46bdf986). Pages run [#39854351064](https://github.com/Metivity/talk2nature/actions/runs/39854351064) completed successfully: repository tests, public build, SEO/publish-boundary checks, deployment and the workflow's live-route/crawl-metadata check all passed. The deployed CEB page loaded in a browser with its expected title, exact canonical, `index,follow` directive and description; the live sitemap includes the new route. A separate local run of the live checker could not verify the site because this machine's Python CA bundle rejected the issuer; no certificate check was bypassed. Google Search Console indexing for the new page has not been checked.

## October 23 — candidate benchmark run card

**Question:** which existing bird/parrot resource can support the first useful, reproducible ML exercise without confusing sound classification with communication?

**Review and change:** wrote [`docs/BENCHMARK_CANDIDATE_RUN_CARD.md`](BENCHMARK_CANDIDATE_RUN_CARD.md), linked it from the researcher starter pack and repository README, and added the next evidence gate to the research backlog. The card compares CEB v1.1 soundscape detection with the monk-parakeet identity/convergence study. It records exact release identifiers, component-specific rights and unresolved file provenance; separates candidate reproduction tasks; proposes group-aware evaluation, baselines, metrics, uncertainty and CPU/resource ceilings; and identifies the independent reviewer roles required. It recommends CEB only as a possible engineering/detection reproduction after group validation. It keeps the actual behavior-context/receiver-response benchmark deferred because neither dataset supplies those targets.

**Limits:** this is a review proposal, not a registered experiment or approval to collect data. No third-party files or model weights were acquired, no test labels were inspected, no code/model was executed, no reviewer was contacted, and no biological claim or reproduction is made. The CEB project-group meaning, full data-to-file provenance, test access custody, and the parrot archive's audio-to-selection mapping remain unresolved. AutoResearch remains **NOT READY**.

**Validation:** all 144 Python tests and 115 Node tests passed; the collection catalog validates 150 resources. The local noindex build generated 114 pages plus 404; the site checker validated 115 HTML pages and 5,655 links. `git diff --check` passed. The changes affect repository documentation only; the live website has not been rebuilt or deployed for this proposal.

## October 23 — prioritize the first communication-adjacent ML candidate

**Question:** which available animal dataset is the strongest first ML candidate for Talk2Nature's behavior/context question, rather than a generic detector?

**Evidence reviewed:** rechecked the five-page EUSIPCO 2024 paper and its 2017 Egyptian-fruit-bat data source alongside the current resource catalog, aggregate annotation report and methods-review packet. The paper describes 35,074 retained vocalizations in 11 video-coded context classes and three subject-independent development/test folds. Its within-development train/validation split is stratified by class but not identity. It reports pooled UAR of 22.4% (SVM), 27.7% (ResNet-50) and 33.3% (EfficientNet-B0); confidence intervals resample individual examples rather than animal/session clusters. The source archive reports 293,238 short 250 kHz WAV files and 91,080 annotations. The complete annotation table is already acquired locally and audited in aggregate; no bat audio, exact paper folds or FileInfo.csv was acquired or inspected.

**Decision and change:** updated `docs/BENCHMARK_CANDIDATE_RUN_CARD.md`, `docs/RESEARCHER_START.md`, `README.md` and the research backlog. Bat interaction-context prediction is now the first communication-adjacent ML candidate for independent review, not a ready-to-run benchmark. CEB remains a separate bird sound-event detection exercise, and monk-parakeet identity/convergence remains a separate task. The phone-first public study is still provisionally parrot-centered if multiple households and an avian researcher are available; the bat data was recorded with specialized ultrasonic equipment. New bat acquisition and model execution remain gated.

**Limits and next gate:** subject-independent folds are reported but not verified; both interaction roles, animal pairs, sessions, channels, dates, treatments and chamber conditions may affect generalization. The model predicts human video-coded context, not receiver comprehension or meaning. The next gate is independent bat-behavior and ML evaluation review of the estimand and minimum grouping/join artifacts. CEB's group audit is now secondary unless pursuing that detector task. No external reviewer was contacted, no model was run, and no deployment occurred. AutoResearch remains **NOT READY**.

## October 23 — bounded search for the bat-context reproduction release

**Question:** did the EUSIPCO 2024 bat-context paper's promised code or split artifacts appear in the most direct public sources checked?

**Evidence:** rechecked the first author's public GitHub owner-repository API inventory (13 repositories, newest update October 20, 2025) and queried GitHub repository search for the exact paper title; no matching public repository appeared in those checks. A Zenodo API search was inaccessible from this environment and is not treated as evidence of absence. Coauthor, lab, archival and unindexed locations were not exhaustively searched.

**Change and limits:** updated the bat-context research record and its GitHub source record, plus `docs/BAT_CONTEXT_REVIEW.md` and the research backlog, with the check date and its bounded scope. This improves provenance and makes the current code status precise; it does not establish that no release exists. No code, folds, audio or model weights were acquired; no reviewer was contacted; no model run or deployment occurred. The next gate remains independent scientific/evaluation review before deciding whether more artifacts are necessary. AutoResearch remains **NOT READY**.

**Validation:** all 144 Python tests and 115 Node tests passed. The local noindex build produced 114 pages plus 404; the site checker passed 115 HTML pages and 5,655 links. The explicit-origin public candidate also built 114 pages plus 404; the checker passed 115 HTML pages, 5,770 links and 114 reachable routes. Direct checks confirmed the bat page's title, canonical, `index,follow` directive, updated review date, bounded-search disclosure and sitemap entry. This is a local publication candidate; live deployment and Search Console indexing were not checked.

## October 23 — Search Console sitemap submission and indexing evidence

**Question:** can Google Search Console currently read the live sitemap and confirm discovery of the new bat-context research page?

**Evidence:** in the owner-authenticated URL-prefix property for `https://metivity.github.io/talk2nature/`, the sitemap report listed `/sitemap.xml` as type “Unknown,” submitted October 20, last read October 20, “Couldn't fetch,” and zero discovered pages. The page-indexing report was last updated October 16; its summary showed 5 indexed and 0 not indexed while its reason table listed one “Crawled - currently not indexed” page. Treat both reports as stale/internally inconsistent, not as a current page census. Independently fetched `sitemap.xml` and `robots.txt` over HTTPS using normal and Googlebot user agents: both returned HTTP 200; the sitemap returned `application/xml`, parsed as a Sitemap Protocol `urlset`, contained 114 URLs and included the deployed bat-context route; `robots.txt` names that sitemap. The live route's canonical, review date and updated content also passed direct checks. [Google Search Central's sitemap guidance](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap) says sitemap submission is a crawl hint, not an indexing guarantee.

**Action and current result:** submitted the existing `/sitemap.xml` once through Search Console after the newer deployment. The UI confirmed “Sitemap submitted successfully” and updated its submission date to October 23. On a fresh report load, the submission date remained October 23, the “Last read” field was blank, status remained “Couldn't fetch,” and discovered pages remained zero. There is no new processing timestamp or result yet. No URL-inspection indexing request was made and no CAPTCHA was solved.

**Next decision and limits:** wait for a new Search Console read before taking another action; do not repeatedly resubmit the unchanged sitemap. If the next report still cannot fetch it, compare Search Console crawl diagnostics with the verified public response and escalate through an authorized support path. This verifies the site's sitemap delivery and one successful submission, not Google's indexing, search ranking or visitor discovery. AutoResearch remains **NOT READY**.

## October 23 follow-up — first animal and dataset choice

**Question:** is there a sufficiently rich existing animal dataset to start applying acoustic ML, and which species best fits the project's first goals?

**Decision:** preserve three distinct tracks already established in the benchmark run card. Egyptian fruit bats are the strongest current communication-adjacent context-prediction candidate because the source study pairs calls with video-coded interaction contexts; this is a lab dataset recorded with specialized ultrasonic equipment, and any model would predict annotated context rather than receiver comprehension or meaning. Central European Birds v1.1 is the large bird sound-event benchmark for detection and vocalization-type classification, not a communication dataset. Parrots remain the provisional human-facing companion-app cohort if multiple households and an avian researcher can be secured; that does not make the bat or wild-bird corpora household-parrot evidence.

**Recheck:** the official EUSIPCO 2024 paper and the 2017 Egyptian-fruit-bat data descriptor support the bat candidate's bounded context task. The official CEB v1.1 record describes 20,826 recordings and 92,857 annotations, with component-specific rights. These records and their unresolved provenance/split questions are already catalogued in `docs/BENCHMARK_CANDIDATE_RUN_CARD.md` and the linked research notes; no duplicate resource was added.

**Next gate and limits:** ask independent bat-behavior and ML-evaluation reviewers to assess the exact estimand, grouping and required file joins; only then decide whether a small local reproduction is appropriate. No audio was newly acquired, no model was trained, no reviewer was contacted, no Kiki files were imported and no participant data were collected. Keep AutoResearch **NOT READY** and do not claim translation.

## October 23 follow-up — simplify the Field Companion home

Moved four optional workflows—phone rehearsal, moment comparison, audio review and synthetic practice—under a closed-by-default “More tools” disclosure. Kept outdoor, familiar-animal and parrot observation paths directly visible. A local noindex build passed 144 Python tests, 115 Node tests and the site checker (115 HTML files, 5,655 links). Browser review confirmed the collapsed/expanded states and all four links at a 480 × 844 CSS-pixel viewport with no horizontal overflow. The browser backend enforced a 480-pixel minimum; this does not establish 320/390-pixel, physical-device, screen-reader or independent-novice behavior. The change was deployed from main as [`0f3efe1`](https://github.com/Metivity/talk2nature/commit/0f3efe126293ebcdb28f608ab69efd0c12ce3d1c) by Pages run [#39863744940](https://github.com/Metivity/talk2nature/actions/runs/39863744940), which passed live-route and crawl-metadata checks. A direct live fetch confirmed the disclosure markup and versioned stylesheet are serving; a browser view with an older service-worker shell showed the expected “Update ready” notice. No reload or cache clearing was forced. Physical-device, screen-reader and independent-novice testing remain open.

## October 23 follow-up — bat FileInfo metadata gate and release

**Question:** can the public per-file metadata help connect the bat paper's video-derived annotation IDs to recording conditions, and is it ready to inspect?

**Evidence and rights:** the direct [Figshare API record](https://api.figshare.com/v2/articles/4555897) was re-read. It declares CC0 at item level and lists one 31,574,701-byte `FileInfo.csv` with no upstream MD5. The [2017 data descriptor](https://www.nature.com/articles/sdata2017143) says the table carries exact recording times, channels and voiced-segment sample positions. This makes a join plausible, but the API reveals neither the file schema nor row coverage. The item exceeds the collector's 5 MiB per-file cap; its contents were not downloaded, and the cap was not changed.

**Change and release:** the reviewer packet, backlog and research-resource record now distinguish the live metadata facts from the unverified join and keep the item metadata-only. PR [#200](https://github.com/Metivity/talk2nature/pull/200) merged as [`1360c2a`](https://github.com/Metivity/talk2nature/commit/1360c2a1096060cc9fb50d2eb9f8f9ad7cd36fcd). Pages workflow [#39865657365](https://github.com/Metivity/talk2nature/actions/runs/39865657365) passed tests, public build, SEO/publish-boundary checks, deployment and live-route verification. A direct HTTPS fetch of the live resource directory confirmed the refreshed catalog date and `FileInfo.csv` record.

**Validation and next gate:** 144 Python tests passed; the 150-record catalog validated; the public build/check passed with 115 HTML pages and 5,770 links. No audio or `FileInfo.csv` rows were acquired, no model was run and no independent reviewer was contacted. Ask bat-behavior and ML-evaluation reviewers whether this join is necessary and what integrity plan would justify a separate acquisition decision. AutoResearch remains **NOT READY**.

## October 23 — put first contribution paths at the top of the README

**Question:** can a new visitor find a safe first action, a researcher walkthrough, and the contribution rules without first scanning the tool inventory?

**Evidence:** the current public main revision at `ff96cb3506b904cbe5b60a1ccdefc54f92647d7a` described detailed tools and formats before its participation guidance. The existing `CONTRIBUTING.md` already has four bounded paths, including the no-microphone phone check. GitHub's issue API confirmed that good-first issue [#115](https://github.com/Metivity/talk2nature/issues/115) is open; its current instructions say that trying the workflow requires no account and that email is available as an alternative to a public reply.

**Change:** reorganized the repository README so a curious visitor, prospective contributor, researcher, scientific reviewer and person needing help can each choose a first route immediately. Kept advanced tool explanations, research limits, local build commands, data safeguards and licensing below those entry paths. Added explicit export-privacy and synthetic-demo boundaries. This changes repository documentation only; it does not change the website.

**Validation:** all 144 Python tests passed. The local noindex site build produced 114 pages plus 404; the site checker passed 115 HTML documents and 5,655 links. A local README-link check found no missing relative file targets. The contribution issue's open state was verified through GitHub's public API. This was a maintainer review, not an independent newcomer walkthrough or screen-reader study. No Node or UI tests were needed because no client code changed.

**Next decision and limits:** obtain a first-time contributor walkthrough of the revised README and record where the person hesitates or abandons the path. No source push, PR, website deployment or outreach occurred in this local candidate. Keep search discovery and independent contribution success unclaimed until measured.

## October 23 — live mobile rehearsal smoke check

**Question:** does the deployed simplified Field Companion preserve its first-use path and microphone-free rehearsal at narrow phone widths?

**Evidence:** on the live Pages app at `/app/`, Chromium viewport emulation measured matching viewport, document and body widths at 320 × 740 and 390 × 844 CSS pixels. The first two actions fit at both widths. At 320 × 740, “Try without a microphone” opened a labeled synthetic session; “End rehearsal” returned a partial-moment recap after 4.5 seconds with zero notes and temporary invented audio. The review screen remained 320 pixels wide, showed export/discard/new-moment controls, and reported that audio was temporary. No microphone permission prompt appeared; no session was saved or exported.

**Unverified and limits:** the browser bridge did not activate the native “More tools” disclosure with click, Enter, Space or its exposed accessibility Expand action. This is inconclusive and not a confirmed product defect; verify it on a supported browser/device. The pass is emulated Chromium only and does not validate a physical phone, screen reader, microphone capture, interruption recovery, export/reopen, or first-time-user comprehension. No code or deployment changed; no animal or participant data was used.

**Next step:** check the disclosure and export/reopen path on a physical iOS or Android device, then obtain a first-time-user walkthrough. Keep those usability gates open until observed. AutoResearch remains **NOT READY**.

## October 23 — live non-bird setup check

At 320 × 740 CSS pixels on the deployed Station page, the observer-declared species-group menu accepted “Other mammal”; the selection appeared in the setup summary and the document stayed 320 pixels wide. The page remained Ready, with no microphone permission, session, recording or saved data. This confirms one non-bird setup path in browser emulation only; it does not test animal identification, screen readers, physical devices or novice comprehension.

## October 23 — add the latest bioacoustic benchmark resource

Added a source-grounded research note and metadata-only resource records for the October 7 BEANS-Next/ROOTS preprint. The note separates the held-out evaluation benchmark (real recordings with existing annotations) from the training resource (curated archives, metadata-derived text, audio-derived information and synthetic scenes), and records the paper's limits, rights uncertainty and no-translation boundary. Updated the model/data decision and collection guide. No audio, code or model was downloaded or run; this is a targeted review, not an independent reproduction. AutoResearch remains **NOT READY**.

**Candidate checks:** 144 Python tests, 115 Node tests and 151-resource catalog validation passed. The explicit-origin public build produced 115 pages plus 404; the site checker passed 116 HTML pages, 5,815 links and 115 reachable public pages. The generated note has its research title/description, self-canonical, `index,follow` and sitemap entry. Browser review showed the page at 2,560-pixel desktop and 480 × 844 CSS-pixel responsive viewports without horizontal overflow. This browser backend enforces a 480-pixel minimum, so narrower, physical-device and assistive-technology behavior remain unverified. This is a local release candidate; live deployment and Search Console processing were not checked in this pass.

**Publication receipt (October 23):** PR [#204](https://github.com/Metivity/talk2nature/pull/204) was squash-merged to `main` as [`7ef6304`](https://github.com/Metivity/talk2nature/commit/7ef6304bf6714110a854234fe5437f4f0d4f9f32). Pages run [#39874587604](https://github.com/Metivity/talk2nature/actions/runs/39874587604) completed successfully: repository and browser checks, Android station checks, explicit-origin build, link/SEO/publish-boundary checks, deployment and live-route/crawl-metadata verification all passed. The deployed [BEANS-Next and ROOTS note](https://metivity.github.io/talk2nature/research/beans-next-roots/) was opened and its title, evidence summary, limitations and citations rendered. This confirms publication and crawl configuration, not Search Console indexing, impressions or ranking. No dataset audio, code or model weights were acquired or executed; no independent reproduction or specialist review is claimed. Reopen the bat specialist/file-join/generic-split gates before choosing a first local baseline; keep AutoResearch **NOT READY** meanwhile.

## October 23 follow-up — Google Search Console live-test and crawl-request result

**Supersedes the earlier “no URL-inspection request” status above:** inspected the deployed BEANS-Next research note in the verified Search Console property. Its indexed-version report said the URL was not on Google and was unknown to Google. The live test reported the URL available to Google and eligible for indexing. After that test, Search Console confirmed the URL was added to its priority crawl queue. This is an accepted crawl request, not proof of crawling, indexing or search visibility. Google's [URL Inspection guidance](https://support.google.com/webmasters/answer/9012289) explains that live-test eligibility does not guarantee inclusion and that processing may take days or longer.

The existing sitemap was resubmitted once and Search Console acknowledged submission, but its sitemap table continued to show “Couldn't fetch” without a fresh successful-read timestamp. Direct HTTPS checks returned HTTP 200 for the XML sitemap and `robots.txt`; the XML parsed, names the deployed BEANS-Next route, and `robots.txt` points to the sitemap. Google's [sitemap report guidance](https://support.google.com/webmasters/answer/7451001) treats submission as a request for processing, not confirmation of indexing. No site change is indicated by these checks. Wait for a new Search Console processing result, then recheck the sitemap and URL; do not repeatedly submit the unchanged file. No CAPTCHA was solved or bypassed, and no indexing result, search impression or ranking is claimed.

## October 23 follow-up — verify the live Field Companion disclosure

**Question:** does the deployed “More tools” disclosure open and expose its optional routes through ordinary pointer and keyboard interaction?

**Check:** inspected the live `/app/` page in a separate browser tab. The native `<details>` began closed. Activating its `<summary>` changed `details.open` to true and exposed all four optional route links in the accessibility tree. Pressing Space closed it; pressing Enter reopened it. No microphone permission, recording session or saved data was used.

**Correction and limits:** the previous browser-bridge attempt was inconclusive because its button-role locator did not match the DOM `<summary>` trigger. The native control works in the checked browser session; no UI code change or deployment is warranted. This does not establish physical-phone behavior, Safari/Android behavior, synthesized screen-reader output, or first-time-user comprehension. The separate physical-device and independent-novice gates remain open.

## October 23 follow-up — Search Console index and discovery check

**Question:** did the new ROOTS research note become indexable, and what discovery evidence is available so far?

**Search Console evidence:** in the verified `https://metivity.github.io/talk2nature/` property, Overview reported 5 indexed pages and 0 not indexed. URL Inspection for `/research/beans-next-roots/` reported “URL is on Google” and “Page is indexed.” This confirms Google-reported index status for that URL; it does not guarantee a result for every query or any traffic.

The Performance report was last updated about four hours before inspection and covered September 29–October 20, 2026. It reported 37 impressions, 0 clicks, 0% CTR and average position 6.7. Its page table showed 29 impressions for `/research/resources/`, 7 for `/research/`, and 1 for the homepage; no query rows were available. The ROOTS note was published October 23, after the report window, so this report cannot measure its search performance.

**Sitemap status:** Search Console still listed `/sitemap.xml` as “Couldn't fetch,” with no last-read timestamp and 0 discovered pages. A same-day direct HTTPS check returned HTTP 200 with `application/xml`; XML parsing confirmed the ROOTS and bat-context routes are present. `robots.txt` returned HTTP 200, allows crawling, and names the sitemap. This establishes public reachability, not why Google's report has not processed it.

**Decision and limits:** no site change or repeat submission was made. Do not resubmit the unchanged sitemap while the previous request is pending. Recheck Search Console after processing; if “Couldn't fetch” persists, inspect its detailed failure state before changing the sitemap or server. Recheck page impressions only after a report window includes October 23 onward. Search Console reports impressions, not visits, human understanding, research adoption or project success.

## October 23 — align first-animal guidance with the current research choices

**Question:** does the public explanation distinguish the first ML question from a possible phone-based participant cohort?

**Evidence and decision:** the current benchmark candidate card and bat-context review rank Egyptian fruit-bat interaction-context prediction as the leading data-led, communication-adjacent ML candidate, conditional on independent review and unresolved join/split checks. This uses specialist laboratory recordings and does not test receiver comprehension. The budgerigar option remains a provisional household-app cohort only if access, avian review and participant/data safeguards are established. Broad bird soundscape datasets are an engineering path for detection, not a substitute for behavior or receiver-response evidence.

**Change:** revised the public first-animal page, its title/description and the homepage step to explain the two different choices. Preserved the existing parrot, dog, cat, pig, frog, bat and bird research paths. Updated the active goal and October 3 first-animal decision record so they do not imply that the phone cohort also determines the first ML benchmark.

**Acceptance checks:** 144 Python tests and 115 Node tests passed. The local noindex build produced 115 pages plus 404; the site checker passed 116 HTML pages and 5,704 links. An explicit-origin public build produced 115 pages plus 404; its publish-boundary/link check passed 116 HTML pages, 5,820 links and 115 reachable pages. The route's revised title, description, `index,follow`, canonical and sitemap entry were verified in generated output. Browser inspection at the backend's 480-CSS-pixel minimum showed the candidate cards stacking and document width matching the viewport. It could not test 320/390 CSS pixels; physical phones, screen-reader output and independent novice comprehension remain unverified.

**Limits and next decision:** this is a local release candidate, not a deployment or external review. No new data, model run, recruitment or animal playback occurred. Keep AutoResearch **NOT READY**; the independent bat/ML review and source-join gates remain open.
## October 31 — clarify zero-command language at the start point

**Change:** revised the Field Companion's visible safety note to say **Observe without prompting** in plain language. It explains that the user need not call or imitate an animal, Talk2Nature sends no animal-directed sounds or prompts, the user chooses when capture starts, and browser capture stops when the page is left. Updated the regression check for this copy. Capture and playback behavior are unchanged.

**Checks:** all 167 Node tests passed; all 239 Python tests passed with one intentional skip. The local noindex build produced 155 pages plus 404; the site checker validated 156 HTML files and 10,847 links. Generated Station HTML contains the revised wording. `git diff --check` passed.

**Limit and next step:** the copy describes the app's intended output, not whole-device silence. Zero-command does not mean hands-free, unattended or background recording. Continue the open named-device synthetic rehearsal and authorized newcomer-comprehension gates. No animal or participant recording was made.

## October 31 — align the contributor quick-start with the synthetic rehearsal

**Finding:** a no-microphone browser rehearsal displayed **Finish and review** as the direct path to review; its stop control was **End rehearsal**. The contributor guide instead called the action **Stop recording**. The same current screen showed the documented **Save this moment** action and the explicit **I saved the file** acknowledgement, followed by the Compare route; Compare exposes **Choose saved moment**.

**Change:** corrected the README and contributor quick-start to name the controls a newcomer sees and added a regression assertion to keep both public paths aligned with the app template. This was a microphone-free invented rehearsal. No WAV or ZIP was downloaded, no microphone was requested, and the saved-session flow was not counted as complete.

**Next:** run the repository/site checks and keep actual device and independent newcomer acceptance open.

## October 31 continuation — refresh near-term funding without conflating voucher applicants

Freshly reviewed the official Israel Innovation Authority [open-applications list](https://innovationisrael.org.il/%D7%A4%D7%AA%D7%95%D7%97%D7%99%D7%9D-%D7%9C%D7%94%D7%92%D7%A9%D7%94/), [Tnufa](https://innovationisrael.org.il/programs/%D7%9E%D7%A1%D7%9C%D7%95%D7%9C-%D7%AA%D7%A0%D7%95%D7%A4%D7%94-%D7%A7%D7%A8%D7%9F-%D7%94%D7%94%D7%96%D7%A0%D7%A7/), [Pre-Seed](https://innovationisrael.org.il/programs/preseed/), [academic compute call](https://innovationisrael.org.il/kol_kore/usage-vouchers-rnd-research/) and [industrial Nebius call](https://innovationisrael.org.il/kol_kore/vouchers-nebius-rd-labs/). Source records 26, 27, 121 and new records **557–558** now reflect checks dated October 31. Tnufa and Pre-Seed list a November 9 noon Israel-time cutoff. The academic voucher closes November 4 and is restricted to budgeted academic research; the industrial product-development voucher has rounds on November 5, December 10 and January 7. The calls have different applicant types, discounts and minimum allocations, so the catalog keeps them separate.

**Readiness decision:** no academic host or eligible industrial company is documented; neither an admitted benchmark nor a large-model compute need is established. Both vouchers are conditional/not ready and are not cash. Pre-Seed remains no-go at documented readiness, with company, investor and open-source-policy gates unresolved. No applicant eligibility is asserted; no application, contact or compute purchase occurred.

**Candidate validation:** full Python suite **243 passed, 1 skipped**; Node suite **170/170**; resource validator **310 valid**; local noindex build **162 pages plus 404**; site checker **163 HTML documents / 11,474 links**; candidate sitemap preserves all **154/154** live routes with eight additional research routes; rendered funding page contains the revised deadlines and distinct voucher terms; `git diff --check` passed. The candidate is on `codex/funding-voucher-readiness-2026-10-31`, based on public `main` `f44e38ff0b970cd164798ecffb6c0f600d4f5264`. No merge or Pages deployment has occurred. The original local worktree remains untouched and divergent. This does not establish applicant eligibility or funding readiness; AutoResearch and real-data admission remain **NOT READY**.
