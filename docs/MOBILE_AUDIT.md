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

Offline setup is optional and user-triggered on the app home. Only the three public app pages, their code/styles/illustration, manifest and icons are cached. The service worker lives under `/app/` and cannot control the private admin origin or unrelated site routes. Its fetch handler additionally restricts exact public URLs, request method and accepted scenario queries. It never stores microphone audio, notes, exports, runtime responses, authentication tokens or private data. [Service-worker lifecycle and caching reference](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API/Using_Service_Workers).

Exports are still essential: offline availability does not make a journal persistent. Browser storage can be evicted. Public research pages linked outside the app's cached routes require connectivity. Clear the site's browser storage to remove the optional public cache; removing a home-screen icon may leave it. Cached app updates wait for existing app windows to close. A failed cache installation removes the incomplete new cache, preserving the previous version and unrelated caches.

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
