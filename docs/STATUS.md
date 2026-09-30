# Project status

Updated September 30, 2026. Public launch and the first bounded data/code/research collection are complete. Private-product work remains unfinished; live Google identity, hosting, funding and scientific-pilot dependencies remain.

## Implemented

- Working brand: Talk2Nature / Listen closely. Understand carefully. Name clearance remains open.
- Scope, open-source/business approach, contribution rules and company boundaries documented.
- Apache-2.0 original software and CC BY 4.0 original public-summary policy; no third-party audio or model weights included.
- Responsive static website: 23 content pages plus 404, original SVG identity, 15 evidence notes, 54-source inventory, ten dated opportunity records, roadmap, methods, contribution and privacy guidance.
- Technical SEO preparation: unique titles/descriptions, structured page metadata, canonical/base-path support, sitemap, robots and social metadata. Local builds default to noindex. The public build allows indexing; Search Console ownership is verified. Search-engine indexing is not yet verified.
- Research utility: metadata validation and deterministic connected-group splits across individuals, sessions and source hashes. Synthetic fixtures only; no trained model or empirical result.
- Local Tnufa preparation brief and application register in ignored `funding/`. No submitted application or confirmed eligibility.

## Validation

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
