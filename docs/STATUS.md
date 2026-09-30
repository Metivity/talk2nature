# Project status

Updated September 30, 2026. The expanded website and Field Notes product page are live. The database-backed study/session rehearsal is implemented locally. Live Google identity, private hosting, funding and scientific-pilot dependencies remain.

## Implemented

- Working brand: Talk2Nature / Listen closely. Understand carefully. Name clearance remains open.
- Scope, open-source/business approach, contribution rules and company boundaries documented.
- Apache-2.0 original software and CC BY 4.0 original public-summary policy; no third-party audio or model weights included.
- Responsive static website: 25 content pages plus 404, original SVG identity, 16 evidence notes, 58-source inventory, ten dated opportunity records, Field Notes product page, roadmap, methods, contribution and privacy guidance.
- Technical SEO preparation: unique titles/descriptions, structured page metadata, canonical/base-path support, sitemap, robots and social metadata. Local builds default to noindex. The public build allows indexing; Search Console ownership is verified. Search-engine indexing is not yet verified.
- Research utility: metadata validation and deterministic connected-group splits across individuals, sessions and source hashes. Synthetic fixtures only; no trained model or empirical result.
- Local Tnufa preparation brief and application register in ignored `funding/`. No submitted application or confirmed eligibility.

## Initial launch validation

- Twelve unit/integration tests pass, including leakage chains, mixed synthetic/real rejection, input ordering, missing origin and public project-subpath links.
- Generated-site checker passes: 24 HTML pages and 543 link references checked locally. External URLs are drawn from the audit; not all external pages were re-fetched during this build.
- Browser: desktop visual inspection; live search, taxon filter, combined filter, zero results and reset verified; evidence page reached with keyboard navigation.
- Responsive rendering checked down to a 390 CSS-pixel layout; measured document width equals viewport width. Mobile menu opens and Escape closes it. Corrected a heading whitespace issue found during responsive review.
- Live pointer navigation passed after using the browser viewport control instead of a mismatched emulated display. Keyboard navigation, search and filters passed. Responsive checks at 390 and 1280 CSS pixels showed no horizontal overflow; menu Enter/Escape and an evidence-page link passed. This is not a full accessibility audit.

## Preview

- Loopback server: `http://127.0.0.1:4173/`, serving only `dist/`.
- Start again with `python3 -m http.server 4173 --bind 127.0.0.1 --directory dist` if necessary.
- Saved desktop image: `tmp/site-preview/home.png` (local only).
- Preview has no signup, analytics, uploads, API keys, live model or database.

## Public launch — September 30, 2026

Raviv approved deployment under raviv@metivity.com. The authenticated GitHub user Metivity is linked to this email through GitHub's commit-author association. Created public repository https://github.com/Metivity/talk2nature and configured GitHub Pages; the service returned https://metivity.github.io/talk2nature/ with HTTPS enforced. The deployed release is commit `2cb6089ab979af5005567144dc4d7eb258ef4fad`; workflow https://github.com/Metivity/talk2nature/actions/runs/36738153662 completed successfully. All 32 public content/asset files, including 24 HTML pages, returned HTTP 200 and matched the local checked build byte-for-byte. The `.nojekyll` build marker is not publicly served. A nonexistent route returned the custom 404 with HTTP 404. The origin-level robots.txt returned 404, so the project-level file is not described as controlling the host.

The initial public snapshot uses the confirmed repository-local Git identity. Earlier unpublished draft history remains on the local codex/foundation branch. Private funding drafts, the audit and raw/source papers remain excluded.

## Next actions

1. Public deployment is verified. Saved proof: `tmp/site-preview/public-home.png`; detailed HTTP comparison: `tmp/live-launch-check.json`.
2. Search Console ownership was verified through the HTML tag under raviv@metivity.com, and the exact project sitemap was submitted. The UI acknowledged successful submission, then initially reported "Couldn’t fetch" / "Sitemap could not be read". The same URL returns HTTP 200, application/xml and valid generated XML locally. Google’s live test at 18:42 Asia/Jerusalem confirmed Crawl allowed = Yes, Page fetch = Successful, Indexing allowed = Yes for the exact sitemap URL. One resubmission was accepted; the sitemap report still says "Couldn’t fetch" with zero discovered pages. Cause remains unresolved; no site-side fetch/XML defect was identified. Retain the tag and recheck the report in a later authorized session; do not claim indexing or successful sitemap processing. Diagnostic screenshots: `tmp/site-preview/google-live-sitemap.png` and `tmp/site-preview/search-console-sitemap.png`.
3. Funding still needs an applicant's legal name, country, individual/company status, eligibility facts, defensible R&D contribution and budget. No application has been submitted. Current Tnufa forms were not retrieved: attachment access failed and direct page retrieval returned HTTP 403. Do not use the old form surfaced by search. Previously verified deadline: October 8, 2026.
4. Scientific pilot needs Kiki ownership/access if relevant, one species/question, usable independently labeled observations and an appropriate collaborator. No Kiki assets imported, animals recruited, weights installed or model accuracy claimed.

## Research checkpoint

The library has 15 notes and 54 source records, including three source-based method reviews. Exact candidate model references, licensing distinctions and data limitations are in `docs/MODEL_DATA_DECISION.md`. These are not expert endorsements or replications. The tested metadata/split utility uses synthetic fixtures only. Further model integration depends on a concrete dataset and question.

Keep work bounded to these milestones; broader reading and optional styling remain backlog.

## Phase two checkpoint — September 30, 2026

Raviv requested a new goal for useful mobile apps, controlled contributions, a private owner admin with Google Sign-In, hosting and an AI architecture. Created the active goal and local branch `codex/private-research-foundation` from the public launch history. No new push or deployment has been performed in this phase.

Implemented locally in `admin/`:
- FastAPI owner workspace and responsive observation form. Only synthetic metadata is admitted; no recording, audio uploads, contributor accounts or model training.
- Google Identity Services client integration and official server token verification; exact raviv@metivity.com authorization, one-time browser nonce, persistent subject binding, opaque expiring/revocable sessions, CSRF/Origin checks, private-response headers and input limits. Without provider configuration, Sign-In is visibly unavailable and private routes remain locked.
- Quarantine, four-check review, training-permission gate, fingerprinted private synthetic releases, optimistic version checks, withdrawal payload removal and dependent release revocation. Public sharing is a separate permission and has no publishing endpoint.
- Separate environment and dependency lock; SQLite runtime under ignored `data/private/`. Hosted Postgres, private objects, workers, backups and contributor roles remain proposed work.

Validation:
- 21 admin security/workflow tests passed, including actual RSA verification with a generated test key and mocked Google certificate retrieval. These are not live Google login tests.
- The original 12 repository tests passed. Dependency consistency and JavaScript syntax checks passed. Local noindex site build/check passed: 24 HTML pages / 518 local link references. The public website was not redeployed.
- Browser: submitted a synthetic observation, verified incomplete review rejection, accepted after four checks, created a private release, withdrew the record, verified release revocation and signed out. Tests used an isolated synthetic SQLite database and an injected test session; production code has no demo login. The test session was revoked and its browser cookie removed.
- Desktop and narrow-layout checks passed without horizontal overflow at measured widths 1280 and 480 CSS pixels. This browser's viewport tool clamped the narrow layout; no 390-pixel or physical-phone claim is made. Two malformed select options and hidden-button styling found during browser testing were fixed. No native recording/background behavior has been tested.
- Proof: `tmp/admin-preview/desktop.png` is a crop of the native browser capture showing the synthetic workbench before the withdrawal test. Rendered screenshot files are local only.

Decisions and next actions:
1. Read `PHASE_TWO_PLAN.md`: start with mobile Field Notes and review; then evaluate a dedicated Android listening station, with iOS and TV capabilities treated separately. First AI work uses licensed acoustic representations, independent behavior labels and held-out baselines. Plants/fungi require separate sensing protocols.
2. Read `PRIVATE_ARCHITECTURE.md`: modular Python API, private data boundary, explicit release gates and capacity/cost model. Current implementation is a local adapter; do not deploy its SQLite database onto ephemeral serverless storage.
3. Google Cloud account verification is required. The browser reached Google's “Verify it's you” screen for raviv@metivity.com. Raviv was asked to complete it; no password was requested in chat, no cloud project/client created and no billing linked. Resume in the handed-off Google Cloud tab after his response, configure a dedicated Talk2Nature web client, then verify live owner login and wrong-account denial.
4. Monthly cloud budget and first device choice were asked asynchronously and remain unanswered. No paid provisioning is authorized. Continue with local/free preparation until the budget and exact project/region are resolved.
5. Gate B still requires real identity, hosted persistence, backup/restore and deletion checks. Gate C requires a scientist, protocol, consent, contributor authorization and real-device tests before any real data intake.

The active goal is not complete. Funding applicant facts, Kiki ownership/access and scientific collaboration remain unresolved; no outreach or application was submitted in this phase.

## Continuation: cloud identity and provenance

Previous turn classification: progress (implemented and tested the local vertical slice). This continuation also made progress: the actual browser session showed account verification had completed, and the dedicated Google Cloud project `talk2nature` was created under raviv@metivity.com in the metivity.com organization. No billing was attached. The standalone “No organization” path failed validation and resource loading; the separate project uses the authorized account's organization and does not reuse either of its earlier projects.

Google Auth Platform branding is prepared with name Talk2Nature, support/contact raviv@metivity.com, and External/testing audience. Setup is at the final, unchecked “I agree to the Google API Services: User Data Policy” step. Requested Raviv's confirmation at this agreement step as required by the browser-control confirmation rules. Do not accept or click through until that response arrives. No OAuth client exists yet, no test user has been saved yet and live Google Sign-In remains unverified. The cloud tab is preserved for handoff; proof is `tmp/admin-preview/google-policy-approval.png`.

Additional implemented controls: review decisions now retain owner role, source version, timestamp and individual attestations in the private record. New releases reject missing review provenance, and exports recompute their stored content fingerprint before returning data. Withdrawal removes the stored review with the active payload. Added an unauthenticated `/privacy` disclosure linked from Sign-In and the workspace, explaining actual Google data use, session retention, unencrypted local storage and withdrawal limits without claiming hosted controls exist.

Validation: 24 backend tests pass, adding retained-review, missing-review rejection, changed-release rejection and pre-login privacy coverage to the earlier suite. The original 12 tests were unaffected and previously passed. JavaScript syntax and diff checks pass. The local server was restarted with the new code. The new cloud project and code are progress; the goal is still not complete.

Next dependency: obtain the pending policy acceptance decision, finish OAuth branding, create a web client for the exact local origin, add the owner test user and test a real owner login before making a live-auth claim. Hosted deployment still needs the unanswered spending limit, exact hosted origin/region, durable storage and operational checks. No external partner outreach, model training or real-data intake has begun.

## Data, code and research collection — September 30, 2026

Raviv explicitly requested this new goal. It proceeds independently of the pending Google policy agreement. Goal scope and acceptance are recorded in `docs/GOAL.md`; collection findings and the next acquisition order are in `docs/COLLECTION.md`.

Created `research/resources.json` with eight reviewed/prioritized paper, code, dataset and model records. Extended the public-content source inventory from 54 to 58 and evidence notes from 15 to 16 with an original parrot-data feasibility note. Source review depth, separate component rights and unresolved artifact checks are explicit. These changes are local; the public site still serves its previously recorded release.

Implemented a standard-library collection CLI with offline planning, explicit IDs, reviewed-license admission, immutable source versions, upstream Git blob checks, SHA-256 receipts, TLS verification, byte limits, staging and no code execution. Downloaded nine files totaling 92,952 bytes into ignored `data/external/`: a parrot annotation table, selected R analysis scripts, Perch configuration, documentation and license notices. No audio, full archives, model weights or publisher articles downloaded. The API for Edmond reports MIT on the dataset and approximately 100.5 GB in full archives; those remain outside the bounded sample plan.

The inspected parrot table contains 808 annotation rows and 176 distinct nonempty behavior strings. `research/parrot_sample_report.json` records aggregate diagnostics and exact source provenance without raw locations or notes. Labels mix observable actions with vocal descriptions, bird entries are incomplete/un-normalized, and audio/selection-table linkage is not yet checked. This is a candidate dataset, not an admitted training corpus. The private admin still rejects real data.

Next scientific milestone: audit full methods, selection-table joins, missing/uncertain identities and behavior-label independence; then decide whether a small matched audio subset can support a held-out baseline. Keep plant/fungal sensing separate. Google Sign-In, cloud budget, Kiki ownership and collaborator access remain pending and do not block this collection workflow.

Validation: 23 repository tests passed (11 collection/report checks plus the original 12), including checksum/size failures, blocked rights, interrupted fetch cleanup, destination safety and aggregate-report provenance. Catalog validation passed. Local noindex build/check passed: 25 HTML pages and 544 link references. Diff checks passed; raw samples/receipts are Git-ignored. The admin was untouched, so its earlier 24-test result was not rerun or represented as a new live-auth check. This completes the bounded collection goal; no trained model or deployed update is claimed.

## Field Notes deployment and database milestone — September 30, 2026

Raviv explicitly approved deployment and requested the next app/database goal. Deployed commit `387031367eb3caed67c142d4f4cf1cc8f9419b65` through successful Pages run https://github.com/Metivity/talk2nature/actions/runs/36761796253 under the verified Metivity account. Live https://metivity.github.io/talk2nature/field-notes/ explains the app and states that it is a private local prototype. The public site has 26 HTML pages including 404, 16 notes and 58 sources. All 34 public content/asset files returned HTTP 200 and matched the checked build; an unknown path returned 404. Public build/check passed with 614 link references and retained canonical/sitemap/Search Console metadata. No claim of search-engine indexing is made.

Browser verification: Field Notes navigation, new parrot note and live search passed. The release page's narrow layout and keyboard mobile menu were checked at a measured 480 CSS pixels with no horizontal overflow; the browser's sizing differed from the requested viewport. Live proof: `tmp/site-preview/field-notes-live.png`; HTTP proof: `tmp/field-notes-live-check.json`.

Private implementation now stores public research catalog snapshots, immutable study protocols/codebooks, exact cited evidence versions, study sessions and observation/session links in SQLite with foreign-key checks. A session must belong to an active synthetic study; linked observations must match its species/animal/session and codebook and not precede its start. Closing a session stops new observations. Existing review/release/withdrawal controls remain, and releases include protocol/evidence references. Legacy standalone synthetic records remain compatible and visibly distinct.

`python3 -m admin.catalog` imported 82 records into the actual local private database: 58 sources, 16 notes and 8 resource records. The second import created/changed/retired zero records. Catalog updates preserve earlier cited versions. External annotation rows, audio and model weights were not imported. Source JSON remains the public editorial source; private study/session/observation records are database-owned. See `docs/FIELD_NOTES.md` for the current schema, media-storage boundary and next gates.

Browser rehearsal in an isolated synthetic database completed study creation, activation, session start, linked observation submission, review, release creation, reload persistence and session closure. The app showed no horizontal overflow at measured 1280 and 390 CSS pixels; the phone layout was visually checked. Screenshot: `tmp/admin-preview/field-notes-desktop.png`. Testing used an injected synthetic session, which was revoked; its cookie and local token file were removed and the isolated server stopped. This is not live Google authentication. The normal locked local server remains on port 4180 with the catalog populated.

Required checks: 31 backend tests passed, including new persistence, frozen-evidence, admission, linkage, access and session-transition coverage; 23 website/research tests passed. JavaScript syntax and diff checks passed. The public website is deployed; the private app is local only. The Google agreement/client, cloud budget/origin/region, durable hosted storage, participant permissions and actual capture tests remain separate gates. No paid services or real-data intake were enabled.

## Public Field Notes demo and local recovery rehearsal — September 30, 2026

Raviv asked to proceed and “build the dome”; interpreted in commentary as “demo.” Deployed public commit `71f1656ae128600646751eac75f295cfe7b7cd19` via successful Pages run https://github.com/Metivity/talk2nature/actions/runs/36771689362 under Metivity. Live demo: https://metivity.github.io/talk2nature/field-notes/demo/, linked from the Field Notes product page. This is the current public release; later recovery/docs source commits do not change Pages.

The demo uses invented clear/obstructed scene descriptions, behavior labels including unknown, separate review/training permissions, a practice reviewer role, four review checks, acceptance/rejection, simulated release and withdrawal. Unsupported or unknown labels cannot pass acceptance; review-only examples cannot enter a training release; withdrawal clears the demo observation and revokes a dependent release. Choices exist only in tab memory and reset on reload. No private API calls, public accounts, uploads, microphone access, persistent storage or model inference were added. Role switching is instructional, not production authorization.

Validation: 23 repository tests, four new Node demo tests and 35 backend tests passed (62 total). The Node checks now run in the Pages workflow. Public build/check passed with 27 HTML pages including 404 and 638 link references. All 38 published files matched the checked build, including the browser module served as JavaScript; a missing route returned 404. Proof: ignored `tmp/field-notes-demo-live-check.json`. One transient GitHub error page cleared on reload; the actual published demo subsequently loaded and completed the flow.

Browser checks covered desktop at 1280 CSS pixels and mobile at 390, with no horizontal overflow. Verified required review permission, required review checks, training opt-out, unknown-label rejection, accepted release, withdrawal/revocation and reset/reload. The deployed entry link and complete live release/withdrawal flow passed, including keyboard focus after release. Live proof: `tmp/site-preview/field-notes-demo-live.png`. Temporary local demo tab/server were cleaned up; the live demo tab remains the deliverable.

Added `admin.recovery`: a local SQLite backup/restore rehearsal that preserves pinned owner identity and research records but removes live auth sessions and login challenges from the copied snapshot. It checks database integrity, foreign keys, schema and record fingerprints, refuses existing destinations, writes owner-only files and never activates or overwrites the running database. The actual 82-entry catalog was restored and verified in ignored `data/private/recovery/demo-readiness-20260930/`; no real observations or owner identity existed in that source database. Isolated tests additionally preserved withdrawal/revocation state, tested session scrubbing and refused broken references. These are unencrypted local copies; hosted/off-device backup, retention and post-snapshot withdrawal reconciliation remain unfinished.

Next useful milestone: resolve pending Google policy/client setup and verify real owner sign-in; choose durable private hosting, origin/region and budget; implement operational deletion/recovery before invited collection. No Google agreement was accepted, billing attached, real recordings admitted, partner message sent or translation result claimed in this continuation.


## PostgreSQL and private hosting preparation — October 1, 2026

Raviv asked to proceed with Google Sign-In and private hosting. The dedicated Google project/account was verified in the existing console tab. Branding remains at the unchecked Google API Services User Data Policy agreement. Requested specific acceptance at that step under the browser-control agreement rule; no answer has arrived. Proof: `tmp/admin-preview/google-policy-approval-current.png`. Separately requested a budget decision for the concrete Cloud Run/Supabase proposal in `docs/HOSTING.md`: up to US$50/month, proposed Frankfurt region. No paid provisioning, account agreement acceptance or billing attachment occurred.

Implemented PostgreSQL as an alternative private store with a private schema, explicit versioned initialization, separate runtime-role grants, transaction-scoped serialization, parameter binding, verified remote TLS and redacted storage errors. Hosted configuration requires HTTPS, a real Google client configuration, pinned owner subject and remote PostgreSQL. Cloud Run cannot silently fall back to SQLite. Added a bounded server launcher, database readiness endpoint and storage-specific privacy disclosure. SQLite remains the actual local database; its existing 82 catalog records were not migrated to a cloud provider.

Local tests: 74 backend cases passed, including 35 PostgreSQL integration cases with a restricted runtime role, atomic replay consumption, rollback, permissions, studies/evidence/session persistence and withdrawal. The runner created its own password-protected loopback-only PostgreSQL 14.18 cluster, then stopped it and removed generated files. No existing database was used. All 23 repository tests and local noindex site checks passed; pip dependency consistency and diff checks passed. The owner server was restarted on port 4180; `/ready` returns 200, private observations return 401, and Google config remains `ready: false`. Browser inspection confirmed the current local-storage privacy disclosure.

Added a pinned-base non-root Docker recipe and manual GitHub verification workflow using only a standard public-repository runner. The first CI run built the image but caught excess admin-directory files in the packaging assertion. Fixed recursive ignore rules and explicit COPY patterns; the rerun additionally seeds harmless excluded-file sentinels and checks the actual build context. This source preparation does not deploy the private service or modify the live Pages release `71f1656`.

Next required work remains the pending agreement and budget decisions, actual Google owner login and wrong-account denial, provider-specific configuration and origin, container/security review, managed PostgreSQL backup/restore and post-snapshot withdrawal reconciliation. Real contributor accounts and recording intake remain disabled. The SQLite recovery tool is not a PostgreSQL backup tool.


Container verification completed on source `6777955` in successful manual run https://github.com/Metivity/talk2nature/actions/runs/36786952737. Both database suites (74 tests), repository checks (23 tests), the pinned-base image build, actual context/image exclusions, non-root execution, missing-hosted-settings rejection and locked local-mode HTTP smoke checks passed. The CI context included harmless `.env`/private-directory markers to prove exclusion; no real private files or cloud credentials were sent. Proof: ignored `tmp/private-hosting-ci.json`. No image was published to a registry and no private service was deployed. Managed PostgreSQL recovery, provider configuration and a dependency/image security review remain before rollout.
