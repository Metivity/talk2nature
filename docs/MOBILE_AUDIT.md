# Mobile product audit and release decisions

October 1, 2026. Internal engineering/product review of Talk2Nature, not independent scientific or security certification. Scope: public mobile entry, existing Station/Listen tools, installation, offline behavior, exports, design and discovery. Private hosting and real research admission remain separate.

## Decision: one installable web app first

The Field Companion at `/app/` has three workflows: Outdoor voices, Shared moments and Sound desk. The first two provide different observation prompts around the same bounded Station engine; they are not different trained models. Sound desk reuses Listen's WAV review workflow. Sharing the engine avoids inconsistent consent, timing and export behavior across separate apps.

A standalone manifest, home-screen icons and installation instructions connect this to the website. It can be used immediately in a browser. Physical Android/iPhone installation and microphone behavior remain unverified; no App Store/Google Play listing or native binary is claimed. Platform documentation supports browser installation, with different browser/OS entry points. [Browser installation](https://web.dev/learn/pwa/installation), [Apple home-screen web apps](https://support.apple.com/guide/iphone/open-as-web-app-iphea86e5236/ios), [WebKit's current web-app behavior](https://webkit.org/blog/17333/webkit-features-in-safari-26-0/).

Native Android is still the next candidate for unattended recording. Wrapping the current page in a native container would not establish reliable background capture. That milestone needs a foreground audio service, persistent controls, bounded encrypted local storage, interruption recovery and physical-device endurance tests described in [NATURE_STATION.md](NATURE_STATION.md). Native SDKs are available locally; the reason for sequencing is a useful, verified cross-platform release and an identified test device, not an assumed inability to build native code.

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

Station 0.2 exports remain preliminary. Hashes establish byte correspondence, not permission, animal identity or meaning. The device wall clock is unverified and not synchronized across phones. Listen can inspect a Station WAV but does not import its entire journal; a later export bundle/import workflow remains a usability improvement.

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
