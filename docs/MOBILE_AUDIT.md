# Mobile product audit and release decisions

October 1, 2026. Internal engineering/product review of Talk2Nature, not independent scientific or security certification. Scope: public mobile entry, existing Station/Listen tools, installation, offline behavior, exports, design and discovery. Private hosting and real research admission remain separate.

## Decision: one installable web app first

The Field Companion at `/app/` has three workflows: Outdoor voices, Shared moments and Sound desk. The first two provide different observation prompts around the same bounded Station engine; they are not different trained models. Sound desk reuses Listen's WAV review workflow. Sharing the engine avoids inconsistent consent, timing and export behavior across separate apps.

A standalone manifest, home-screen icons and installation instructions connect this to the website. It can be used immediately in a browser. Physical Android/iPhone installation and microphone behavior remain unverified; no App Store/Google Play listing or native binary is claimed. Platform documentation supports browser installation, with different browser/OS entry points. [Browser installation](https://web.dev/learn/pwa/installation), [Apple home-screen web apps](https://support.apple.com/guide/iphone/open-as-web-app-iphea86e5236/ios), [WebKit's current web-app behavior](https://webkit.org/blog/17333/webkit-features-in-safari-26-0/).

An experimental, source-only Android Station preview now exists for an owner-operated device evaluation. It implements a user-started foreground audio service, persistent Stop control, bounded encrypted local storage, interruption recovery, and manual review/export. It is not a signed APK, store release or validated field recorder; physical-device behavior and endurance remain unverified. See the [Android build and safety limits](../native-android/README.md) and the device-test gates in [NATURE_STATION.md](NATURE_STATION.md). Wrapping the current web page in a native container would not establish reliable capture behavior, and the prototype does not justify inviting field use.

## Findings and treatment

| Finding | Impact | Treatment |
| --- | --- | --- |
| Separate tools lacked a clear mobile entry/install path | Visitors had to infer the product | New app home, three workflows, installation manifest/icons, public `/mobile/` landing page and website navigation |
| Desktop-first editorial layout was cumbersome on a phone | Recording controls and scenarios were hard to discover | Dedicated app shell, safe-area spacing, phone navigation and scenario-specific guidance |
| Glass effects can reduce readability or be unsupported | An attractive screen could be hard to use | Controlled dark surfaces, visible focus, 44+ pixel primary controls, opaque fallback and reduced-transparency/motion styles; no full accessibility certification |
| Repeated export filenames lacked session identity | Different sessions could be confused | UUID filenames, session ID, declared device UTC start and WAV SHA-256 in browser JSON exports |
| A storage-limited event could disappear from marker outcomes | A detected event might be mistaken for a quiet window | Preserve only event ID/onset and storage-limit reason; regression test; audio is not retained |
| Installing a web app could imply continuous recording | Users could expect all-day capture | Explicit five-minute foreground limit throughout; native milestone remains distinct |
| Offline caching could cross the private-data boundary | Private pages or media could accidentally persist | App-scoped service worker, exact public-shell allowlist, no runtime-response caching, authorization/mutation/unknown-query bypass |
| Cached code can update during a session | Work could be lost or mixed across versions | Content-derived cache revision; new worker waits for old app windows to close; no forced reload or skipWaiting |
| “Offline ready” can be false after storage eviction | Users could leave connectivity without tools | Worker checks every cached file before reporting readiness; setup failure and repair messaging |
| Product availability could be mistaken for audience traction | Publicity could overstate progress | Public demo/share link and feedback path; no invented users, partners or results |

Station 0.2 exports remain preliminary. Hashes establish byte correspondence, not permission, animal identity or meaning. The device wall clock is unverified and not synchronized across phones. Compare can reopen the original Station ZIP without unzipping; Review can now verify the ZIP and pass one retained clip with its full session journal into a local annotation notebook. The direct path reduces extraction steps while preserving the distinction between original session notes and new annotation labels.

## Offline boundary

Offline setup is optional and user-triggered on the app home. Only the six public companion-app routes, their required code/styles/illustration, manifest and icons are cached. The service worker lives under `/app/` and cannot control the private admin origin or unrelated site routes. Its fetch handler additionally restricts exact public URLs, request method and accepted scenario queries. It never stores microphone audio, notes, exports, runtime responses, authentication tokens or private data. [Service-worker lifecycle and caching reference](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API/Using_Service_Workers).

Exports are still essential: offline availability does not make a journal persistent. Browser storage can be evicted. Public research pages linked outside the app's cached routes require connectivity. Clear the site's browser storage to remove the optional public cache; removing a home-screen icon may leave it. Cached app updates wait for existing app windows to close. A failed cache installation removes the incomplete new cache, preserving the previous version and unrelated caches.

### October 13 follow-up: update notice on every app screen

The original update-ready message appeared only on the app home page. An opted-in offline user already on Station, Review or Compare could keep using an older cached shell without seeing that notice. All Field Companion routes now include one polite status region. On opening an app route, the app checks the existing app-scoped registration; if an update is waiting or finishes installing, it explains that the current session will not reload, asks the user to export anything they want to keep, and explains that closing all Talk2Nature windows and reopening applies the update. The app does not register a worker unless the user previously enabled offline tools, call `skipWaiting`, reload, or cache audio and notes.

The new watcher is part of the exact offline asset allowlist. Unit tests cover an already-waiting worker and a newly installed waiting worker; build tests check the notice on all six app routes. A 390 × 844 CSS-pixel preview reviewed the notice's fit on the synthetic Station screen. Existing-client update propagation and installed-device behavior remain unverified; no physical device or real capture was used.

## Release checks and unresolved gates

Run all Python repository tests, `node --test tests/*.test.mjs`, public/local build checks, and a real browser walkthrough. Meaningful checks include offline navigation after network disconnection, a synthetic audio session offline, source review, UUID/checksum export, a WAV opened in Sound desk, phone/desktop layout, installation manifest diagnostics and public deployment equality. Record actual outcomes in STATUS.md rather than interpreting this checklist as completed.

Still required: actual home-screen installation and recording on Android/iPhone; phone lock/background, call interruption and thermal tests; independent accessibility/security review; an approved scientific protocol and collaborator; real hosted persistence/recovery. An in-app desktop browser does not establish physical-phone compatibility. No new service budget, partner contact or scientific claim is authorized by this release.

## Discovery: the next two weeks

The concrete distribution surface is `/mobile/`: an indexable introduction, useful install guide, one-minute synthetic exercise, explicit limits, share/copy controls and focused feedback. The website home and navigation point to it. A GitHub mobile-check form asks for reproducible technical feedback without recordings or sensitive details.

| Step | Audience and deliverable | Measurement | State |
| --- | --- | --- | --- |
| Founder demonstration | 45–60 second screen recording: choose rehearsal, add marker, stop, inspect, export | Viewers who can repeat the workflow and report a useful next task | Script below; video not recorded |
| Device circle | Five consenting testers across at least two Android/iPhone combinations | Installation, first completed synthetic session, export success, specific failures | Target only; no testers recruited |
| Scientific review | One qualified animal-communication researcher and one existing observation team | Written workflow critique and one bounded question | No new outreach sent |
| Developer release | README, public app, audit, reproducible tests and one small issue to contribute | Independent reproduction or substantive contribution | Artifacts prepared; no external reuse claimed |
| Broader announcement | Founder-owned professional/social channels and relevant community channels after checking their current posting rules | Repeat use and actionable feedback; manually recorded with permission | Copy below; not posted |
| Follow-up | Publish what failed and what improved; add a reviewed Hebrew introduction if useful | Returning testers, corrected defects, confirmed workflow value | Backlog |

Do not buy reach before the first five testers can complete the exercise. No analytics SDK, referral identifiers, newsletter signup or automatic enrollment was added. We cannot infer active users from requests or installation metadata. Record volunteered results in the private execution register; preserve email/contact privacy. Recheck community submission rules when an actual posting destination is selected.

### Founder demo script

“Can an everyday phone help us understand the living world more carefully? This is Talk2Nature's first field companion. I'll use invented sounds, so no microphone or animal is involved. I add an observation marker, stop the session and inspect the next sound. The timing is visible; the meaning is still a question. You can export your clips and notes, or inspect a WAV more closely. Try it on your phone and tell us where the workflow helps or fails. We're building the tools in the open.”

### Suggested launch copy — not posted

“We've released the first Talk2Nature field companion: a free, open-source web app for short listening sessions, observed context and local audio review. Try the synthetic rehearsal without a microphone, then add the app to your home screen if it is useful. This is early research tooling; it does not translate animals. We're looking for device testers and people who already study or document animal behavior. Start here: https://metivity.github.io/talk2nature/mobile/”

The larger objective remains a credible observation and learning network. Distribution should invite useful participation while accurately showing today's capabilities.

## October 7: parrot field visit

Added a fourth home-card workflow and matching install shortcut. `mode=parrot` opens the existing Station with a 30-second whole-moment window and an observer-declared Parrot group. Species remains optional and editable; no acoustic caller/meaning classifier or automatic reply is added. Calls, mimicry, nearby human speech and visible context are explicitly kept as separate observations. The one new preset module is included in the exact offline shell, and only the allowlisted `mode=parrot` query can reuse the cached Station page.

Validation: 79 Node tests and 50 Python tests passed; the local build/check produced 70 content pages plus 404 and 2,886 valid local links. Browser review verified the parrot selection and whole-window default at a 390 CSS-pixel viewport, with document width matching the viewport. No microphone permission was opened. This is a local preview; it is not deployed and has not been tested on a physical phone.

## October 2: mobile style and finite motion

Added a shared mobile navigation dock with four 54-pixel-high destinations, section selection, safe-area spacing and bottom focus clearance. Research notes now use a compact field-guide header, readable phone typography and a clearer study summary. The app retains its own navigation, now with 48-pixel targets; the public dock is not duplicated inside it.

The listening app has a shorter phone introduction, compact monitor and a direct Open listening controls link. At a verified 390 × 844 CSS-pixel viewport, activating it placed Start listening at y573 with permission, status and the synthetic option visible. The earlier entry layout placed Start at y1235. Recording permissions, baseline, limits, manual playback and local-only behavior remain intact.

The homepage has three original inline illustrations and keyboard-operable Birds / Plants / Fungi choices, with selected state and a polite announcement. Light humor surrounds the research; scientific findings and limits are unchanged. Motion is finite (at most four seconds per effect), restricted to decorative/editorial elements, and respects OS reduced motion plus a per-page motion switch. No animation loop, new dependency, remote asset, audio or storage was added. Content remains visible if animation support is unavailable.

Browser acceptance: 320-pixel research reading and Menu/Escape; 390-pixel card selection, 54-pixel dock targets, app navigation without duplicate docks, controls jump and offline review/example with no autoplay; 1440-pixel desktop composition. No horizontal overflow on the inspected layouts. OS reduced motion disabled animation and disabled the switch with an explanatory label; manually disabling motion also removed animation. The offline shell includes the exact revision of the two new public assets. These are browser viewport tests, not physical iPhone/Android, screen-reader or native-install validation.


## October 3: whole-moment continuation

Companion mode now defaults to a visible 30-second whole-window choice; highlights remain available. Synthetic Chrome capture reached exactly 30 seconds, stopped automatically and showed one complete window. Offline shell setup and navigation to companion mode succeeded with network emulation offline. A second synthetic observation preserved a context marker and was stopped at seven seconds, visibly labeled Partial observation window. Save session reached the download-requested state; a corresponding disk file was not found in the checked Downloads location, so browser download completion/reimport is not newly verified. ZIP/WAV/checksum interoperability is verified by executable tests, distinct from this browser limitation.

Measured widths 320 and 1440 CSS pixels matched document widths, and the new selector retained a 48-pixel control height at 320. The 390 × 844 composition was visually inspected. These are emulated desktop-browser checks, not physical iPhone/Android microphone or installation tests. Temporary network/viewport overrides are removed after release verification. The offline shell still stores only public assets; audio and notes remain temporary.


## October 3: field-guide design and simpler observation flow

A bounded design/product continuation introduces Set up → Observe → Keep, a shorter first control view, mobile Stop fixed above the safe area during capture, four explicit observer-note shortcuts, a readable session recap, and export feedback next to Save. The home screen uses original SVG parrot artwork, blue-green glass, warm pale actions and a compact first-observation invitation. `docs/APP_NEXT_IDEAS.md` records the design rationale and prioritized future work.

Measured desktop/mobile widths 1440, 390 and 320 matched document widths. At 390, the home action began at y370 and the Station Start button fit within the control view (y633 in the tested anchored layout). At 320 during capture, Stop occupied y704–758 within a 780-pixel viewport; app navigation was hidden until stopping. These measurements describe browser emulation, not physical phones. A synthetic partial window retained quick notes; an offline 30-second rehearsal completed with two notes. Highlights capture produced four clips. Unadded typed notes stayed readable with an explicit exclusion warning, and a confirmed New moment cleared the draft and returned to setup. Permission gating, mode locking and manual-only playback were preserved.

The actual highlights ZIP download was completed through Chrome’s native Save panel, then checked from disk: four synthetic WAVs, matching journal checksums/sample counts and valid ZIP CRCs. The unadded draft was absent from the journal. This resolves download completion for this run, not browser reimport or physical-device saving. Native Save and script-confirm dialogs blocked the browser automation helper until handled through their visible UI; no application permission or browser security protection was weakened. Receipt: ignored `tmp/design-next/export-proof.json`.

Keyboard Tab reached the next action with a visible outline; Enter navigated into Station. Reduced-motion emulation disabled both new illustration animations, and reduced transparency gave the console a solid background with no blur. Countdown text is no longer a per-frame live announcement; state and note feedback remain available. This is a focused check, not a full screen-reader/accessibility audit. All 39 Python and 57 Node tests passed, including observer provenance in exports, bounds, uncertainty and recap distinctions. Local/public builds checked 57 HTML pages and 2,236 links. No new backend, dataset, biological result or real-data admission was added.

## October 3: reopen and compare saved moments

Added `/app/compare/`, a new home invitation and a Compare navigation item (installation remains on Home). The two-slot layout stacks on phones; the main comparison uses readable observations while clock, sample rate, processing and detector fields remain in optional details. Original session ZIPs reopen without manual JSON handling. Invented examples illustrate complete versus interrupted windows. See `SESSION_COMPARE.md` for import and interpretation boundaries.

Acceptance: 39 Python + 68 Node tests passed. The new tests include bounded archive corruption/layout checks, WAV/hash/sample verification, completeness/discard preservation, old context-free highlights, session replacement races and the actual file-change handler in a DOM harness. That handler verifies untrusted notes remain literal text and failed replacement leaves the old session intact. Local/public builds check 58 HTML pages with 2,207/2,266 link references.

Browser checks: 1440px desktop and 390/320px responsive layouts; no horizontal overflow; example pair, expanded notes, optional settings, keyboard Enter, manual player preparation with paused=true/autoplay=false, clearing the selected session and revoked player source. Reduced motion removed animation; reduced transparency removed blur. After explicit offline setup, comparison navigation and example review worked with network emulation offline. Reload showed no open sessions or audio source. Temporary emulation overrides were restored.

The original four-clip synthetic ZIP actually downloaded in the previous release was reopened through Chrome’s native file picker and displayed its declared synthetic origin, 23.7-second duration and four retained recordings. The extension’s direct file-selection helper was blocked by its existing file-URL permission; no extension/browser permission was changed. A separate damaged-file native picker attempt could not resolve the test path and was cancelled; damaged replacement is therefore verified by executable importer/real-handler tests, not claimed as a native-picker browser result. No real microphone, physical-phone file selection or biological experiment was tested. Live publication receipt follows in `STATUS.md`.

## October 11: live phone workflow recheck

Rechecked the published `/app/` in Chrome at 390 × 844 CSS pixels. The document width matched the viewport (390px); “Record a moment” and “Try without a microphone” were visible at y370 and y432. The shared-moment route opened with the 30-second whole-moment option selected, animal identity left as “Not sure yet,” and an explicit recording-permission checkbox. Start and synthetic rehearsal controls were visible together.

The microphone-free rehearsal entered its synthetic state, kept Stop visible at the bottom of the screen, and stopped into a clear partial-session recap: 8.3 seconds, zero notes, temporary audio and a reminder to save before leaving. No microphone permission or real recording was used. In the captured review frame the fixed app dock covered the lower edge of the next clip card; at that time, controls had not been tested at the bottom of the card, leaving focus/scroll access as a follow-up check.

### October 11 follow-up: review-card access beneath the dock

Repeated the live rehearsal at 390 × 844 CSS pixels using `/app/station/?mode=demo`. The synthetic whole-moment flow produced one 11.9-second partial clip. At the recap's initial scroll position, the fixed app dock visually covered the card's lower portion. Scrolling to the bottom of the page moved the full card and its review controls above the dock: the card occupied y136–511, its controls y386–488 and the dock y770–832. The controls were visible and reachable; no code change is indicated by this check.

This closes the documented scroll-access question for one synthetic partial clip. It does not test a multi-clip highlights session, keyboard focus through every control, a physical phone or assistive technology. No microphone permission, real recording, playback or upload occurred.

### October 11 follow-up: multi-clip review and keyboard focus in the local build

Audited the current local public build in headless desktop Chrome with mobile viewports. A microphone-free synthetic highlights session produced two invented sound events. At 390 × 844 CSS pixels, the document matched the viewport and the keyboard could reach each event's source selector, notes and review/save/discard actions. Before the fix, discarding a clip sent focus to the document body. Discard now moves focus to the next remaining event; after the final discard it moves to the visible save-status message, while the journal retains the discarded event IDs and timing. After smooth scrolling settled, the next-event heading and final status message were both in view. At 320 CSS pixels, the responsive document width also matched the viewport.

The empty review message now distinguishes a session with no detected clips from one whose clips were manually discarded, omitted by storage limits, or represented by an incomplete/discarded whole-moment window. This prevents a deletion from being presented as “no sound.” Automated checks cover those states and focus selection; the offline app shell includes the new review helper. Local verification passed 82 Node tests, 56 Python tests and the site checker (77 HTML pages, 3,333 links). The browser rehearsal made zero microphone calls and no non-local requests. It is desktop Chrome emulation only: physical phones, assistive technology and a live deployment remain unverified.

## October 12: phone rehearsal before field use

Added `/app/check/` as a distinct eight-second, user-started microphone check. It asks permission before microphone access, processes frames into aggregate duration/level/near-full-scale readings, retains no frames, and provides visible Stop/cancel controls. It terminates on page hiding, page exit, an ended microphone, audio interruption or a no-frame watchdog. It has no session, journal, export, playback, storage or upload path. The app home and listening setup link to it; the exact public offline shell includes the page and modules.

The result distinguishes browser audio receipt from device quality. Processing rate and dBFS readings do not establish sensitivity, frequency response, calibrated sound pressure or wildlife suitability. Automated checks verify the meter's eight-second sample bound and aggregate-only output, app-route discovery, search metadata and offline allowlisting. Rendered inspection was initially unavailable; the October 12 follow-up below closes the local browser-layout check, but does not validate physical phone behavior. No microphone was opened. Physical iPhone/Android behavior, actual microphone access, repeatability against a reference recorder, screen-reader use and first-time user comprehension remain unverified. This local implementation is not a field-readiness certification.

### October 12 follow-up: responsive browser check

Served the local noindex build over a temporary loopback-only static server and inspected it in Chrome. The phone rehearsal was visually checked at 390 CSS pixels and the phone rehearsal, resource directory, conure evidence page and world atlas at 320 CSS pixels. In each measured view, document width matched the viewport. The resource search returned the single conure playback record from 34 resources; its expanded disclosure showed separate review depth, rights scope and the unstated license version. Atlas filters placed the conure under birds, Egyptian fruit bat under mammals, and *Fusarium* under plants & fungi. The check's permission declaration remained unchecked; pressing Start produced the permission reminder and focused the checkbox without opening a browser microphone prompt. No browser console errors appeared during these checks.

This is responsive desktop-Chrome evidence, not physical-phone, microphone, screen-reader or user-comprehension validation. At the time of this pre-release check, the live resource-directory URL returned the project's not-found page. A later October 12 release check superseded that observation: the live route now returns the indexable resource directory, while the current local candidate contains one additional unpublished resource. See `docs/STATUS.md` for the exact live response and sitemap checks. Search Console indexing remains unverified.

### October 12 follow-up: Station controls with the fixed Stop bar

Built the current public candidate for its GitHub Pages subpath and exercised the synthetic rehearsal in mobile-emulated Chromium at 320 × 740 and 390 × 844 CSS pixels. At both widths, the fixed Stop control remained visible; after scrolling the quick observations and marker guidance into view, the controls and welfare guidance sat fully above Stop. At 390 pixels, all four quick-observation buttons occupied two visible rows and the “Observe naturally” guidance remained readable. At 320 pixels, the “Do not provoke calls” guidance was fully visible above Stop. An uncertain marker was added successfully to the synthetic timeline. No microphone was requested or used, and no browser page errors occurred during the 320-pixel check.

This closes the local rendered-layout check for the fixed Stop bar. It is desktop Chromium with emulated phone dimensions, not physical iPhone/Android, Safari, assistive-technology or first-time-user validation. The candidate remains local and undeployed.


### October 12 candidate: Listen ZIP path and opportunity-page rendering

Built a local release preview for the exact GitHub Pages subpath. At 320 and 390 CSS pixels, the Listen guide's expanded file instructions showed the new “open the original ZIP in Compare” route; its `/talk2nature/app/compare/` target returned HTTP 200. The note still distinguishes whole-session ZIP review from opening one WAV for annotation and reminds visitors to use recordings they have permission to inspect. The funding page rendered at 320, 390 and 1440 CSS pixels without horizontal overflow. Its upcoming Horizon call card exposed direct official topic and applicant-eligibility links. All five page loads returned HTTP 200 with matching canonical URLs and no browser page errors. No recording or microphone access occurred. This is local browser-emulation evidence, not a deployed-site or physical-device test.


### October 12 live-release verification

After PR #23 merged and the manual Pages deployment succeeded, the production Station was exercised at 320 × 740 CSS pixels in synthetic mode. The Stop control stayed fixed and visible; the quick-note rows scrolled above it; an uncertain marker was added to the timeline. The live Listen page's ZIP instructions opened Compare at the project-prefixed route, which returned HTTP 200. The public resource directory and opportunity page loaded at their canonical project URLs, with no horizontal overflow at the tested widths. No microphone was accessed.

These are live website and desktop-Chromium emulation checks, not physical-phone, Safari, Android, screen-reader or first-time-user studies. Search Console processing remains unverified.

### October 12 follow-up: current-main companion path at phone widths

Built the current repository snapshot (`5fb188d`) as a public-origin local preview and checked the Field Companion in mobile Chromium at 320 × 740 and 390 × 844 CSS pixels. The home page had no horizontal overflow; both first actions fit at 320 pixels (276 × 54 and 276 × 47 CSS pixels). On the companion setup route, “Who was there?” opened at both widths and exposed all 12 observer-declared groups, including other birds, mammals, amphibians, reptiles, fish, invertebrates, mixed scenes and “Not sure yet.” Selecting “Other mammal” and entering the temporary example “bat” displayed the relevant ultrasonic/underwater limitation. The picker remained explicitly observer-declared, not automatic identification.

In the microphone-free rehearsal at 320 × 740, tapping “Try without a microphone” entered the synthetic recording state; tapping Stop returned to local review. A guarded `getUserMedia` stub recorded zero microphone calls, the viewport remained 320 pixels wide, and Chromium reported no page errors. No audio was recorded, saved or exported. The temporary species example was only a browser interaction and was discarded when the page closed.

This is maintainer-run responsive and interaction QA of the current source, not a physical-phone, screen-reader, Safari, first-time-participant or independent usability test. It found no concrete layout or control defect to change. Next: collect a small amount of consented first-time-user feedback and test on actual iOS/Android devices before claiming field usability; participant recording intake remains closed.

### October 13 follow-up: session retention explained before recording

The novice path previously showed “On your device” but did not explain that an unexported session disappears when the page closes; the export reminder appeared only in the later review screen. Added a short warning on the companion home page and directly above Station's recording controls. The Start button's accessible description points to the warning. It says that nothing uploads or auto-saves and that users must export to keep audio and notes. No storage, upload, identity, or backend behavior changed.

In local Chromium at 320 × 740 and 390 × 844 CSS pixels, the home action and Station setup remained within the viewport, with no horizontal overflow. Clicking the microphone-free demo called `getUserMedia` zero times; no page errors occurred. This is maintainer browser emulation, not a physical phone, screen-reader run or first-time-user comprehension study. See `docs/STATUS.md` for automated checks and counts.

### October 12 follow-up: public-site dock while reading

The fixed bottom dock previously occupied the last 68 CSS pixels of the viewport at 320 × 740 and intersected the below-fold research summary. It now moves out of view after deliberate downward scrolling, returns on upward scrolling or near the top, and is revealed when keyboard focus enters the navigation. In local public-build Chromium checks at 320 × 740, the dock moved fully below the viewport while the summary scrolled above it; upward scrolling and keyboard focus restored it. At 390 × 844 the page width remained within the viewport; at 900 × 900 the site dock remained hidden. Reduced-motion emulation reported a zero-second transition. No page errors occurred.

This is desktop Chromium with emulated viewport sizes, not a physical-phone, Safari, screen-reader or first-time-user check. The footer navigation remains usable without JavaScript, though it will not auto-hide. No audio, microphone, participant data or browser storage was used.

## October 13: narrow research provenance after deployment

The cross-taxon dataset-discovery note exposed a horizontal overflow at 320 CSS pixels: its full pinned commit identifier widened the article to 348 pixels. The same note fit at 390 pixels. PR [#80](https://github.com/Metivity/talk2nature/pull/80) added `overflow-wrap: anywhere` to article review paragraphs, retaining the full identifier. After the merge and successful Pages deployment, a fresh browser-emulated check measured the live page at 320 × 740 and 390 × 844 CSS pixels. At both sizes, the document and body widths matched the viewport; the 320-pixel review paragraph reports `overflow-wrap: anywhere`.

This closes the post-deployment layout check for that article. It is browser viewport emulation, not physical iPhone/Android, Safari, screen-reader or first-time-user validation. It establishes a responsive rendering result, not search-engine indexing or scientific review.

## October 13: Station setting-note touch interaction

Loaded the deployed Field Companion Station in desktop Chrome through Playwright's mobile emulation with touch enabled at 320 × 740 and 390 × 844 CSS pixels. In each viewport, started only the "Try without a microphone" synthetic rehearsal, waited for its explicit synthetic state, stopped it, then tapped the 48-pixel "Other animals" setting-note label using `page.touchscreen.tap`. Captured `pointerdown` and `touchstart` to confirm a touch event; the first tap selected the option and showed the whole-session observer-note feedback, and the second tap cleared it.

At both sizes, document and body widths matched the viewport, with no horizontal overflow or page errors. A guarded `getUserMedia` stub recorded zero microphone calls, and the browser made zero non-read network requests. The session existed only in memory and was neither exported nor uploaded. This is real touch-event delivery in desktop-Chrome mobile emulation, not physical-device use, iOS Safari, screen-reader, or first-time-user comprehension testing; those remain open.

## October 13 follow-up: verify browser download and reopening in Compare

**Question:** does the novice save path generate a real browser download that the next app step can reopen, while preserving observer context without turning an empty session into “silence”? **Procedure:** built the current local noindex site and opened `/app/station/` in desktop Chromium with a 390 × 844 CSS-pixel mobile viewport and downloads enabled. Stubbed `getUserMedia` to fail and count any call. Started only the invented synthetic rehearsal, stopped it, selected the optional “Other animals” whole-session setting note, and saved the session. Captured the browser's download event into a temporary directory, opened the ZIP, acknowledged the saved copy, followed the in-app Compare link and loaded that same ZIP into its first-session slot.

**Result:** the browser returned HTTP 200, generated a nonempty ZIP containing the session journal and `READ-ME.txt` (no WAV, as expected for zero retained clips), and Compare reopened it. The imported recap showed `Other animals · observer-entered`, zero retained recordings and zero observations; its detail text said “No audio was retained. That does not establish silence.” The document and body both measured 390 pixels wide; `getUserMedia` was called zero times, and no JavaScript page errors occurred. The temporary ZIP was removed automatically at the end of the check. No real recording, participant data, external sample or research admission was involved.

This is desktop Chromium with mobile viewport emulation and programmatic file selection. It verifies browser download generation and app import, but not the default Downloads location, a physical phone, iOS Safari, native file-picker behavior, assistive technology or first-time-user comprehension. No code change was needed. Keep the app's broader field-usability claim open until physical-device and independent novice checks are available.

## October 13 follow-up: keyboard path and Chromium accessibility tree

**Question:** does a keyboard-only visitor have a reachable microphone-free Station path, named controls and understandable state transitions? **Procedure:** served the local public build and confirmed the Station response at the test route was byte-identical to `dist/app/station/index.html`. In desktop Chrome at a 390 × 844 CSS-pixel viewport, advanced with Tab from the page start to “Try without a microphone,” then activated it with Enter. The test blocked and counted any `getUserMedia` call, inspected Chrome's accessibility tree, and pressed Enter on the focused Stop control.

**Result:** the tab sequence reached the synthetic control in order. Starting changed the state to “Synthetic session,” exposed the microphone-free explanation in the polite status region, and moved focus to “Stop recording.” Stopping changed the state to “Stopped · local only,” updated the polite status text to “Stopped by you,” and moved focus to the visible review area. Chrome's accessibility tree exposed a name for every button, textbox, combobox, checkbox and link in the checked view; document and body widths both measured 390 pixels. The microphone-call count was zero. No app code change was needed.

This is a maintainer-run Chromium accessibility-tree and keyboard check, not synthesized screen-reader output, a VoiceOver/NVDA test, physical-phone use, or independent first-use evaluation. Those remain open; the app's wider field-usability claim is not yet established.

## October 13: simplify the home entry on narrow phones

Removed a second 30-second “Begin” card that repeated the hero's two actual choices. The hero now explains the first observation in one short, lightly playful paragraph. A 320 × 740 Chromium mobile-emulation check then exposed the fixed Home/Listen/Review/Compare dock covering the second hero action. A narrow-width CSS rule reduces only the headline below 361 CSS pixels; at 320 × 740 the headline fits in two lines, both “Record a moment” and “Try without a microphone” finish above the dock, and the page has no horizontal overflow. At 390 × 844 both actions also remain clear. On the actual GitHub Pages `/talk2nature/` path, the home page and both CTA destinations returned HTTP 200; required assets loaded without failures, there were no page errors, and the duplicate card is absent.

Temporary local screenshots were visually inspected but are not project assets. This is maintainer-run desktop Chromium viewport emulation, not physical-device, iOS Safari, screen-reader or independent novice testing. No microphone, audio, participant data or real animal observation was used.

## October 14: Android Station build and package boundary check

The current source builds both debug and release APK variants with Android lint passing. The pure-Java capture-core checks, browser import/eight-hour-limit tests, and release-package boundary script all pass. The release APK contains the required recording permissions and intended notification/foreground-service declarations; the boundary check confirms no `INTERNET`/`DUMP` permission or debug receiver, with backup disabled. See `docs/STATUS.md` for the exact commands and results.

No device was connected for this run. Build success does not verify microphone behavior, screen lock, calls, permission revocation, notification controls, one- or eight-hour endurance, battery/thermal behavior, accessibility or first-time-user comprehension. The local release APK is unsigned and was not distributed. Physical-device review and release signing/store requirements remain open; this prototype is not ready for field-study recruitment. Gradle emitted deprecation warnings that should be reviewed before a Gradle 9 upgrade.

## October 14 follow-up: explain Android permissions before the first prompt

**Question:** does a first-time Station user learn why Android asks for microphone and notification permissions before the system prompt appears?

**Change:** the setup card now says that Android asks for microphone access, may ask to show notifications, keeps a Stop action in the listening notification, and does not start a session until the user taps Start and grants access. This places the permission purpose alongside the recording limits and wildlife-care consent.

**Check:** built debug and release APKs with Android lint passing; `testDebugUnitTest` is configured but has no test sources. The Android core checks and release-package boundary check passed. Installed the debug build in a temporary Android 14 emulator configured to 320 dp width. Visual inspection showed the disclosure, consent checkbox and Start button readable and reachable by scrolling, without horizontal overflow. The emulator displayed Android's notification permission prompt; after denying it, Station reported that nothing started or was saved. Microphone permission was not granted, and no recording was made. The temporary AVDs and emulator were removed afterward.

This is an emulator UI and permission-flow check, not physical-phone, microphone, screen-lock, battery, vendor-specific or first-time-user validation. Real-device readiness remains open.

## October 14 follow-up: simplify Android microphone limits

**Question:** can a first-time observer see the practical limits quickly, with specialist calibration detail available when wanted?

**Change:** shortened the always-visible limit to the 24-clip/24 MB cap, unsaved quiet moments, and the fact that the station is not continuous or unbiased monitoring. Kept the warning that an ordinary phone may miss bat ultrasound, underwater sounds or vibrations. Moved microphone/device-processing calibration and sensitivity caveats into a collapsed “Phone microphone details” control; its label changes between show and hide.

**Check:** Android lint plus debug and release APK assembly passed. The capture-core checks, native-session import/schedule tests, and release-boundary check passed. Installed the debug APK in a fresh Android 14 emulator at 320 dp width. The initial screen showed the practical caveats with the detail text hidden; tapping Show exposed the calibration caveat and changed the control to Hide; tapping Hide removed it again. The visible text fit the narrow layout without horizontal overflow. No microphone permission was granted, no audio was accessed and no session was started. The temporary Talk2Nature AVD and emulator were removed after the check.

This verifies a maintainer-run emulator interaction only. It is not a physical-phone, TalkBack, screen-lock, battery, vendor-specific or first-time-user comprehension test. Those remain open, as do release signing and field-readiness gates.

## October 14 follow-up: make the first-use invitation fit every animal

**Finding:** the mobile app's main first-use invitation joked specifically about a parrot, even though the same companion offers observer-declared groups for dogs, cats, many other animal groups, mixed scenes and unknown sources. On the narrow phone layout, this is the first explanatory copy beside the two main actions, so the parrot reference could make a cross-species tool feel parrot-only.

**Change:** replaced the species-specific joke with a short, playful line about quiet moments counting and no big show being needed. The 30-second whole-moment path and the explicit microphone-free demo are unchanged; the app still leaves species identity to the observer.

**Check:** rendered the local noindex build in desktop Chrome with CDP mobile metrics at 320 × 740 and 390 × 844 CSS pixels. The headline and both first-use actions fit above the fixed dock; document and body widths equal the viewport, and both routes remain present. The repository suite, local and explicit-origin public builds, and site checker passed. No microphone, animal audio, camera or participant data was used. This is browser emulation only; physical phones, screen readers and first-time-user comprehension remain unverified.

**Release:** PR [#163](https://github.com/Metivity/talk2nature/pull/163) passed public checks [#38514844447](https://github.com/Metivity/talk2nature/actions/runs/38514844447), merged as [`203164f`](https://github.com/Metivity/talk2nature/commit/203164ffb5d5b93ca0b147a2a626170b8eea03ad), and deployed by Pages run [#38514992709](https://github.com/Metivity/talk2nature/actions/runs/38514992709). Live HTTPS checks verified the app, both first-use routes, sitemap and robots file return HTTP 200, with the new copy, canonical, `index,follow` and sitemap entry present. Search Console indexing, physical-device behavior and novice comprehension remain unverified.

## October 14: keep parrot-operated interfaces separate from the Field Companion

The full text of the CHI 2024 tablet ergonomics study was reviewed for this distinction. Its 17 trained parrot completers used a 10.1-inch tablet in a caregiver-supported enrichment task; larger targets increased hit rate in that setup, but touch-point precision did not significantly differ by target width. The result is not a phone-layout specification, a communication test or evidence for adding sound playback. The Field Companion remains a human-operated passive-observation tool. A future animal-operated enrichment interface would need its own qualified avian/animal-computer-interaction review, hardware-specific study and welfare protocol with a voluntary exit. Full source and limits are recorded in the [research note](../content/research.json).

## October 14 follow-up: validate the published first-use feedback path

**Question:** can a visitor try the microphone-free rehearsal and prepare concise usability feedback without an account, upload or automatic submission?

**Check:** opened the live `/mobile/` page in desktop Chrome mobile emulation at 320 × 740 and 390 × 844 CSS pixels. At both widths, the feedback helper produced a visible, reviewable report from invented QA entries; document width matched the viewport; and the email action remained a `mailto:` draft. The browser reported no page errors or non-GET requests. At 320 × 740, followed the practice link into Station, started the synthetic rehearsal, and confirmed the microphone-call stub stayed at zero. The page identified the session as synthetic; no recording, email, issue or upload was created.

**Limit:** this verifies the published software path with maintainer-entered test text, not a first-time-user outcome, actual email-client behavior, screen-reader use or physical iPhone/Android behavior. No participant feedback was collected. Independent novice and physical-device review remain the next usability gates.

## October 23 follow-up: progressive disclosure on the Field Companion home

**Question:** can a first-time visitor choose a simple observation path before encountering researcher-oriented utilities?

**Change:** kept the two hero actions and three direct observation paths together—outdoor, familiar animal and companion parrot. Moved the phone rehearsal, saved-moment comparison, audio review and invented-scene practice into a native, closed-by-default “More tools” disclosure. All four remain reachable; this changes their order and visibility, not their underlying behavior.

**Check:** all 144 Python tests and 115 Node tests passed. The local noindex build produced 114 pages plus 404; the site checker passed 115 HTML pages and 5,655 links. In the local browser preview, the 480 × 844 CSS-pixel viewport had no horizontal overflow, displayed three core paths before the collapsed disclosure, and exposed all four optional routes when expanded. The disclosure was keyboard-accessible through native `<details>/<summary>` semantics. No microphone was opened and no animal or participant data was used.

**Limit:** this browser backend enforced a 480-pixel minimum for the measured preview, so this pass does not establish 320- or 390-pixel behavior, physical-device usability, screen-reader output or independent novice comprehension. Those remain open. This is a local candidate; it has not been deployed.

**Release receipt — October 23:** PR [#198](https://github.com/Metivity/talk2nature/pull/198) merged as [`0f3efe1`](https://github.com/Metivity/talk2nature/commit/0f3efe126293ebcdb28f608ab69efd0c12ce3d1c). Pages run [#39863744940](https://github.com/Metivity/talk2nature/actions/runs/39863744940) passed tests, public build, link/SEO/publish-boundary checks, deployment and live-route/crawl-metadata verification. A direct live fetch confirmed the new closed-by-default disclosure markup and the versioned app stylesheet returned HTTP 200. An already-open browser view showed the service worker's “Update ready” notice with older cached markup; no reload or cache clearing was forced. Existing app windows should follow the visible save/export and close/reopen guidance before receiving the update. Physical-device and independent-novice testing remain open.

## October 23 live multi-species setup check

**Question:** can an observer choose a non-bird animal group before a session starts on a narrow phone layout?

**Check:** on the deployed Station route in Chromium emulation at 320 × 740 CSS pixels, selected “Other mammal” in the observer-declared “Who was there?” menu. The choice appeared in the setup summary, document width remained 320 pixels, and the page stayed Ready. No microphone permission was requested and no session, recording, export or saved data was created.

**Limit:** this checks the setup control only. The app does not identify the animal; the selection is the observer’s note. Emulation does not establish physical-device, screen-reader or independent-novice usability, nor any biological result.

## October 23 live phone-width rehearsal

**Question:** does the deployed simplified home and microphone-free rehearsal remain usable at narrow phone widths?

**Check:** on the live Pages app at `/app/`, Chromium viewport emulation at 320 × 740 and 390 × 844 CSS pixels reported matching viewport, document and body widths. At 320 pixels, the two first-use actions measured 276 × 54 and 276 × 47 CSS pixels; at 390 pixels, both measured 346 pixels wide. At 320 pixels, “Try without a microphone” opened the clearly labeled synthetic session; “End rehearsal” produced a partial-moment recap after 4.5 seconds with zero notes and temporary invented audio. The review controls were visible and the document remained 320 pixels wide. No microphone permission prompt appeared; the session was not saved or exported.

**Earlier automation result (superseded):** the initial browser bridge showed the native `<details>/<summary>` disclosure as a collapsed button, but its button-role locator did not match the DOM trigger. That no-op was a selector mismatch, not evidence of a broken disclosure.

**Follow-up live-browser check:** in a separate tab on the deployed `/app/` page, activating the native `<summary>` opened the disclosure; the DOM's `details.open` state changed from false to true and all four optional routes appeared in the accessibility tree. Space closed it and Enter reopened it. The control is now verified with pointer and keyboard input in this browser session.

**Limits:** this check does not establish physical-phone behavior, Safari/Android home-screen behavior, screen-reader output, microphone capture quality, interrupted-session recovery, export/reopen success or first-time-user understanding. No microphone was opened, no animal or participant data was used, and no code or deployment changed.

## October 23 follow-up: observer note through narrow-phone review

**Question:** does a manually entered observation survive the synthetic Stop-to-review path at a narrow phone width, and can the user reach Save afterward?

**Check:** on the deployed Field Companion at 320 × 740 CSS pixels, opened the microphone-free synthetic rehearsal, added the “Movement” observation at 00:03 and ended the rehearsal. The app reported “Stopped · local only” and “Stopped by you”; the timeline and partial recap retained one note. Scrolling to the lower review area exposed the “Save session” control. The page heading still says “A rehearsal in listening” after stopping, but the state label and recap clearly report the stopped state.

**Decision and limits:** no code change was indicated. This was desktop-Chromium viewport emulation with invented audio, not physical-phone, Safari, screen-reader or first-time-user testing. No microphone permission was requested, and no download, upload or real recording was made.

## October 23 live Station setup review at narrow phone widths

**Question:** can a visitor reach the Station's listening controls on a narrow phone layout, and does the fixed navigation obscure the primary action?

**Check:** inspected the deployed `/app/station/?mode=companion#station-console` in Chromium viewport emulation at 320 × 740 and 390 × 844 CSS pixels. At both widths, the document and body matched the viewport with no horizontal overflow. At 320 pixels, the setup card needed a short scroll before “Start listening” and “Try without a microphone” were visible. At 390 pixels, “Start listening” was visible at the top; the fixed bottom navigation sat over the lower edge of the setup card while the page was at its initial scroll position. Scrolling the card/page brought the consent and listening actions into view and moved the fixed navigation out of the way. The silent synthetic route and advanced settings remained reachable.

**Decision and limits:** the main action is reachable, but the fixed navigation makes the initial card feel crowded at the smaller width; consider a focused UI adjustment only if a physical-device or novice check confirms that friction. This was browser viewport emulation, not a physical phone, Safari/Android home-screen, screen-reader or first-time-user test. No microphone, playback, export or save action was used, and no recording was created.

## October 23 live deployed synthetic-rehearsal walkthrough

**Question:** does the deployed home page distinguish recording from no-microphone practice, and does the live rehearsal route end in a review state that identifies synthetic content as temporary?

**Check:** inspected the live `/app/` and `/app/station/?mode=demo#station-console` in the in-app browser at its 1280 × 720 desktop viewport. The home page exposes separate “Record a moment” and “Try without a microphone” actions and explains the local/no-account/no-automatic-playback boundary. Opened the rehearsal route directly; this was not a home-to-Station clickthrough. Its setup shows the 30-second whole-moment default, the no-upload/no-auto-save/export reminder, and the phone-microphone/identification limitation. Pressing “Try without a microphone” entered a state labeled “Synthetic session”; the page said it used invented tones in the audio engine with no microphone access or audible playback. Selecting “I’m not sure” added one timeline note at 00:09. “End rehearsal” opened a local-only review of an 18.8-second partial moment, labeled invented practice audio, with one note and an explicit reminder to save before leaving. No session was saved or exported.

**Decision and limits:** the observed live path is coherent and its synthetic, uncertain and temporary boundaries remain visible through review; no change was indicated by this check. This is a desktop accessibility-tree and screenshot walkthrough, not a phone-width recheck, physical-device, Safari, screen-reader, microphone-permission instrumentation or first-time-user study. No real recording, animal or participant data was used; no microphone prompt appeared.

## October 24 local Stop-bar reachability recheck

**Question:** does the always-visible mobile Stop control make the quick observation notes unreachable or unusable during a recording?

**Check:** tested the local noindex build of `/app/station/?mode=parrot` in Chromium emulation at 390 × 844 CSS pixels. The document and body were both 390 pixels wide, with no horizontal overflow. During a microphone-free synthetic whole-moment rehearsal, the fixed Stop strip occupied y=758–832. At scroll position 766.5, all four quick-note buttons were visible at y=349–477, well above the strip. Keyboard activation of “Movement” added “I noticed movement” to the local timeline; stopping opened a local review showing one note and 14.5 seconds observed. A separate intermediate scroll frame showed the expected transient overlap while content passed beneath the fixed strip; continued scrolling brought the controls fully clear. The page reserves 112 CSS pixels below the fixed strip while recording.

**Decision and limits:** no CSS change is justified by this check: the Stop action remains fixed and the note controls have a reachable, unobstructed scroll position. Keep first-time-user, pointer, screen-reader and physical-device checks open; this was keyboard-assisted desktop Chromium emulation, not a real phone or a usability study. No microphone permission, upload, save, download or real animal/participant data was involved. The synthetic session remained temporary and was discarded when the test tab closed.

## October 24 Compare action clearance at narrow phone width

**Question:** does the fixed app navigation cover the Compare page's first-use “Try an example pair” action on a 320-pixel phone viewport?

**Evidence and change:** before the edit, Chromium emulation measured the button bottom at about y=696 and the dock top at y=666 at 320 × 740, covering the lower 30 pixels of the action. At 390 × 844 there was no overlap. Reduced only the Compare heading to 2.1rem inside its existing `max-width:360px` rule; wording and the wider-phone style remain unchanged.

**Verification:** rebuilt the local noindex site and checked `/app/compare/` in headless Chrome at 320 × 740 and 390 × 844. The 320-pixel button now ends at y=643.2 with the dock starting at y=666 (22.8-pixel clearance); at 390 pixels the button ends at y=664.5 and the dock starts at y=770. At both sizes, document/body widths equal the viewport, the example pair opens with both sessions labeled “INVENTED EXAMPLE,” and no page errors occur.

**Limits:** this is a local Chromium viewport-emulation check, not a physical-phone, Safari/Android, screen-reader or first-time-user study. It uses invented sessions only; no microphone, recording, upload, save or research admission occurred. The screenshot is a temporary local QA artifact and is not part of the site.

**Release receipt:** PR [#328](https://github.com/Metivity/talk2nature/pull/328) merged as [`b05bc55`](https://github.com/Metivity/talk2nature/commit/b05bc551ae36f4867722a388d1655dc621e7c5b8). Pages run [#40081911116](https://github.com/Metivity/talk2nature/actions/runs/40081911116) passed its public build, tests, publish-boundary checks, deployment and live-route verifier. A separate live Chromium check returned HTTP 200 and confirmed the same 22.8-pixel / 105.5-pixel clearances at 320 × 740 and 390 × 844, with working invented examples and no page errors. Physical devices and assistive technologies remain untested.

## October 24 — keep the pending-update alert in one status region

**Question and evidence:** does a waiting service-worker update create one clear, accessible notice? The live Field Companion's accessibility tree showed the identical “Update ready” message in both the global update banner and the offline-tools status after a new worker was waiting.

**Change:** send the update message to the global banner when it exists, leaving the offline status focused on whether the public shell is ready; use the offline status only as a fallback on a page without the banner. Added checks for both cases.

**Limits:** this removes duplicate status text by construction and tests the state helper; the live observation was a browser accessibility-tree check, not a phone-width, physical-device or screen-reader test. No microphone, recording, upload or animal/participant data was used. The change needs CI, a release and post-release browser verification before it is considered live.

## October 24 post-release check — single-region update notice

**Question:** is the update-notice correction served by the live Field Companion, and does its normal home screen keep offline readiness distinct from update status?

**Release:** PR [#335](https://github.com/Metivity/talk2nature/pull/335) merged as [`ac9f6fd`](https://github.com/Metivity/talk2nature/commit/ac9f6fdb58f36d213c755c674c7e90a16840da91). Pages run [#40087965008](https://github.com/Metivity/talk2nature/actions/runs/40087965008) completed successfully on that commit.

**Live check:** a TLS-verified fetch of `/app/` served `app.js?v=d1e6972ad9bec584`; that bundle imports the matching versioned [`app-update.mjs`](../web/assets/app-update.mjs). The deployed helper sends “Update ready” to the global notice when one exists and uses the offline-status region only as a fallback. A fresh live `/app/` accessibility-tree view showed the offline-ready message and update-check control, with no duplicate update-ready text. This checks the default page state and served code; I did not trigger a waiting-worker update cycle in this browser.

**Test:** `node --test tests/app-update.test.mjs` passed all four cases, covering a global notice, offline-status fallback, an already-waiting worker and a newly installed worker. The update remains user-controlled: it does not force a reload or activate a waiting worker mid-session.

**Limits and next decision:** the release and helper behavior are verified, but a full update cycle from an older installed shell remains unverified on a physical phone and with a screen reader. Preserve the waiting-worker behavior while making its save/reopen guidance clear to nontechnical users; the October 25 wording change is recorded below. No microphone, recording, upload or animal/participant data was used.

## October 25 — simplify the waiting-update notice

**Question and evidence:** does the update notice tell an everyday app user what to do without internal browser language? The live Station accessibility tree showed “Nothing will reload now” and “Export work you want to keep,” followed by an instruction to close all Talk2Nature windows. Those phrases describe implementation details rather than the user's next action.

**Change:** the notice now reads: “A new version is ready. Save any moment you want to keep, close all Talk2Nature tabs or windows, then reopen the app.” The worker still waits for the existing windows to close; no forced reload or mid-session activation was introduced. The focused unit test pins the exact text in both global-notice and fallback cases.

**Verification:** PR [#381](https://github.com/Metivity/talk2nature/pull/381) merged as [`f1be81c`](https://github.com/Metivity/talk2nature/commit/f1be81cd62e40ba02ac4e9ab17ab86858ffdaa03). Pages run [#40134112457](https://github.com/Metivity/talk2nature/actions/runs/40134112457) passed Python and Node suites, public build, publish-boundary checks, deployment and live-route verification. A cache-bypassing live browser view at 390 × 844 CSS pixels displayed the new message in two lines; document and body widths were both 390 pixels, no page errors were reported, and the Station remained ready for its synthetic rehearsal. Starting then stopping a 4.7-second invented rehearsal left the page and waiting notice in place; the recap marked the audio synthetic and partial. No microphone was opened, and no save or upload action was initiated.

**Limits:** this is in-app-browser emulation, not physical-phone or screen-reader evidence. It verifies message rendering and no interruption in the synthetic path; it does not verify installing an update on iOS or Android.

## October 25 comparison: expose practice without adding another app mode

**Question:** does the evidence support a separate curated Learn experience in the Field Companion?

**Review:** MooLogue's 2026 paper describes learning from a curated cattle-call library, with a restricted dataset and unresolved discrepancy between the paper's offline-first app description and an older repository's cloud-upload README. BirdNET Live's v1.2.1 docs describe on-device bird-species ID, automatic local session review, and explicit export/deletion; its privacy policy says raw audio stays on-device and optional external location/weather requests are off by default. The app requests microphone permission before readiness and does not assess call meaning. We reviewed the docs and release files, not an installed app or runtime network traffic.

**Decision:** Talk2Nature already has a short invented-scene exercise that teaches observation versus inference without animal audio or microphone access. A second product mode and an audio library would be premature without rights-cleared educational examples or user evidence. The home page now offers “Practice careful noticing” as a small optional link before the collapsed utility panel, leaving “Record a moment” and “Try without a microphone” as the main actions. No recording, playback or upload behavior changed.

**Check:** local browser rendering was reviewed at the available 480 × 844 CSS-pixel viewport. The document width stayed at 480 pixels; the practice action sits after the three observation scenarios, and its destination opens the invented-scene lesson without a microphone prompt. The browser clamps this environment to 480 CSS pixels, so this is not a 390-pixel viewport, physical-phone, screen-reader or independent-user test. All 117 Node tests and 170 Python tests passed (one intentional external-sample skip); the noindex build produced 138 pages plus 404 and the checker validated 139 HTML documents and 7,090 links.

**Next check:** after the separate recruitment authorization, use the [first-use walkthrough protocol](FIRST_USE_WALKTHROUGH.md) with five consenting first-time testers across at least two Android/iPhone combinations. Begin at `/app/`; read the task prompt once, then do not coach. Test microphone-free synthetic practice, note entry, stop, save and reopen in Compare with the normal file picker. Do not ask for animal data or grant microphone permission. Record only anonymous task outcomes, assistance, approximate time and confusion. Separately, run a controlled physical-device capture check with no animals or people being recorded before making hardware/field-readiness claims. Preserve user control and the passive-observation default; recruit nobody or send invitations until separately authorized.

## October 25 — clean-session zero-command Station walkthrough

**Question:** does a clean browser session let someone enter and review a no-microphone practice moment without setup?

**Check:** a separate Chrome task session opened the deployed Station without the pending-update notice seen in the older in-app-browser session. The first screen offered a no-microphone rehearsal; selecting it displayed that invented tones were not played aloud and no microphone was accessed. Tapping “Movement” added one timestamped note. Ending the session opened a partial review labeled synthetic, showing 4.4 seconds observed and one note. No export or upload occurred.

**Decision and limits:** the basic clean-session browser flow works. The update notice appeared in the older in-app-browser session but not the separate clean Chrome session, consistent with an update waiting on an already-open client. Selecting “Discard session” opened an explicit confirmation; browser control timed out, and I did not confirm deletion. This is a maintainer walkthrough, not one of the five independent testers, a screen-reader pass or a physical-phone test. No code change is supported by this single check. Keep the planned five-person/two-platform study and phone save/reopen/export checks open; no participant recruitment or invitations occurred.

## October 25 — complete a zero-command save-and-reopen rehearsal

**Question:** can a visitor preserve a moment with ordinary buttons and reopen it without handling a JSON file or extracting an archive?

**Check:** built the current local noindex site and opened `/app/` in a mobile-width browser preview. The effective viewport was 480 × 844 CSS pixels; the document remained 480 pixels wide and the observation cards collapsed to one column. From the home screen, “Try without a microphone” opened the rehearsal setup; the in-console button began it. The default was a 30-second whole moment with animal identity left unknown. A synthetic session started without a microphone prompt, accepted one “Movement” note, and stopped at 4.8 seconds. The recap labeled the clip invented and partial. “Save session” generated a ZIP; reopening it through Compare → “Choose first session” displayed “Invented example,” partial whole moment, 4.8 seconds, one retained recording, one observation, unknown animal and soundscape context “Not recorded.” Compare reported “Opened locally”; no upload or playback action was taken, and the page stated that playback is user-started.

**Limits and next gate:** this verifies the maintainer's synthetic browser path and local export parser, not a first-time user's comprehension, microphone capture, keyboard/screen-reader use, physical-phone storage, or iOS/Android behavior. It does not satisfy the five-person/two-platform target. A follow-up click on “Discard session” timed out in browser control before a confirmation state could be read; no deletion was verified or claimed. A real field recording remains outside this check; keep consent, protocol and hosted-storage gates closed until separately reviewed.

## October 28 — make one saved moment the beginner path

The mobile guide previously said to unzip a saved session to review its WAV, although the app's Compare tool accepts the original ZIP directly. The homepage also described Compare as reopening two moments, which obscured its single-session review capability. Updated the guide to say that one download can be opened directly; made the second Compare slot explicitly optional; and changed the homepage shortcut and page metadata to lead with reviewing one saved moment. No data retention, download, playback or audio-capture behavior changed.

The local noindex build passed all 193 Python tests (one intentional skip), all 139 Node tests and the site checker (144 HTML documents, 7,629 links). Installed Chrome previews at 320×568 and 390×844 CSS pixels showed matching document and viewport widths on both Compare and the mobile guide; screenshots were visually reviewed. This is maintainer emulation only. Physical iPhone/Android behavior and uncoached newcomer comprehension remain unverified; preserve the existing device and recruitment gates.
