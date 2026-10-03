# Talk2Nature project instructions

## Ownership and boundaries
- Active project: Talk2Nature, Raviv's independent initiative. On September 30, 2026, Raviv explicitly approved publishing and deployment using his raviv@metivity.com account. GitHub associates that email with the authenticated Metivity user; the confirmed repository is Metivity/talk2nature and host is GitHub Pages. The funding applicant/legal entity is still unconfirmed.
- Keep other companies' code, data, credentials and strategy out of this repository. Kiki is a potential starting point, not an authorized import; confirm its location and ownership first.
- The September 30, 2026 request authorizes creating the repository, building and publicly launching this project's website, researching funding, and preparing/applying for suitable opportunities. Use the confirmed Metivity account for this repository and its Pages deployment; do not use another authenticated account. Do not invent applicant facts, sign declarations, accept funding obligations, purchase services or message prospective partners without the necessary explicit authorization.
- No sub-agents unless Raviv or applicable instructions explicitly request them.
- Follow Raviv's CX rules for supported read-only commands. Do not use CX for edits or credentials.

## Current goal and continuity
- Read `docs/GOAL.md` and `docs/STATUS.md` for the current scope and next actions.
- Existing evidence baseline: `research/build_audit.py` and `output/pdf/talk2nature-audit-and-plan.pdf` (September 30, 2026).
- Public source records live in `content/`; private application preparation belongs in `funding/`, which is excluded from public builds and Git by default.
- No QMD collection is configured. Do not index unrelated folders.
- The current collection goal uses `research/resources.json`, `talk2nature/collection.py` and `docs/COLLECTION.md`. Downloaded third-party samples and receipts belong in ignored `data/external/`, never in the website or `examples/`. Acquisition is separate from scientific admission and the private server's synthetic-only gate.

## Scientific and editorial standards
- Distinguish detection, identification, association, experimentally supported meaning, bounded exchange and general translation.
- Cite original sources, state exactly what was reviewed, and separate findings, limitations and proposed experiments. Never imply all literature has been read.
- Do not reproduce publisher articles, figures, third-party audio or model weights without explicit redistribution rights. Publish original short summaries and links.
- No fabricated partnerships, team members, awards, results, application submissions or testimonials.
- Initial animal work is passive observation. No automated playback or treatment advice.
- Code, model weights, datasets and article content have separate licenses. Do not assume public availability permits commercial use or redistribution.

## Implementation and verification
- Website: dependency-free Python static builder in `web/build.py`; HTML/CSS/JS output in ignored `dist/`.
- Research tooling: standard-library Python in `talk2nature/`; synthetic examples only in `examples/`.
- Run `python3 -m unittest discover -s tests -v`, `python3 web/build.py`, and `python3 scripts/check_site.py` after relevant changes. Inspect meaningful desktop/mobile UI behavior before a public release.
- The public Field Notes demo is a browser-only simulation with invented scenes and no private API or persistent storage. Run `node --test tests/demo.test.mjs` for demo changes; the Pages workflow also runs these checks. Keep demonstration role switching separate from actual server authorization.
- A public build requires an explicit `--base-url` and `--public`; local previews are noindex. Never invent a production origin.
- Deploy only public build output. The audit, funding drafts, local screenshots and raw recordings are not website assets.
- Use a `codex/` prefix for new branches. Do not commit secrets, raw recordings, personal applicant data or rendered temporary files.

## Repository publishing identity
- Use repository-local Git author Raviv Yatom <raviv@metivity.com>. GitHub CLI authentication must select Metivity per command without changing the global active account. Never print or save tokens in project files.
- Public default branch: main. Local task branches use codex/. The earlier codex/foundation history remains local; publish only the clean public-launch history.
- Deployment workflow is manual (workflow_dispatch) and publishes only checked dist/ output. Future deployment requires task authorization; pushing source alone does not deploy.

## Phase two private workbench
- The current task branch is `codex/private-research-foundation`. The public website remains on the deployed Pages revision recorded in `docs/STATUS.md`.
- Read `docs/PHASE_TWO_PLAN.md`, `docs/PRIVATE_ARCHITECTURE.md` and `admin/README.md` for private-product work.
- `admin/` is a separate Python/FastAPI owner-only metadata rehearsal. Run `.venv/bin/python -m unittest discover -s admin/tests -v` after backend changes; keep the original dependency-free website checks as well.
- Real data is rejected by the server. Do not remove this gate without an approved protocol, consent and hosted-storage review. No demo-auth environment switch in production code.
- Owner Google identity must be checked server-side and pinned by stable subject. Do not authorize the entire Metivity domain. Google Cloud account verification is complete. Dedicated project `talk2nature` was created under raviv@metivity.com in the metivity.com organization; no billing was attached. On October 1, Raviv confirmed Google policy acceptance. OAuth branding and the identity-only local web client were created, the exact owner test user was saved, and one real owner sign-in succeeded. The stable subject is pinned in ignored owner-only `admin/.env`; do not print or commit it. A different Google account was also rejected after signature verification. Repeat owner login after restart with the explicit pin also succeeded. Hosted sign-in remains unverified.
- On October 1, 2026, Raviv approved the proposed Cloud Run plus dedicated Supabase Pro hosting in Frankfurt with a total budget of up to US$50/month. Provider agreements and credential handoffs remain subject to the applicable action-time rules; do not buy add-ons or exceed that budget. No private database on GitHub Pages or ephemeral serverless storage; private origin/region and backup/withdrawal requirements must be resolved before hosted use.
- Field Notes study/session/evidence tables and the catalog import are documented in `docs/FIELD_NOTES.md`. `python3 -m admin.catalog` imports public metadata only. Preserve frozen study/evidence versions and the distinction between participant observations and external source samples. Study/session records have no deletion UI yet and must remain synthetic.
- `python3 -m admin.recovery --name <new-name>` rehearses restoration in ignored `data/private/recovery/`, scrubbing live auth state from the copy and never activating it. Preserve pinned owner identity. Copies are unencrypted and may predate withdrawals; never treat this rehearsal as a hosted backup service or reactivate an older snapshot without deletion/revocation reconciliation.

- Hosting preparation is in `docs/HOSTING.md`. PostgreSQL runtime uses a private schema and a restricted role; initialize schema explicitly, never at startup. Hosted mode requires HTTPS, Google client, pinned owner subject and verified-TLS PostgreSQL, with no SQLite fallback. `.venv/bin/python scripts/test_postgres.py` tests both adapters in a disposable loopback cluster; never point these destructive fixture resets at an existing or remote database. The manual private-checks workflow verifies the container build and locked local-mode behavior. Actual cloud deployment and hosted recovery remain unverified. Provider billing completion and Supabase agreement acceptance are separately pending; private setup details are in ignored `data/private/setup-status.json`. Do not recreate the existing pending Talk2Nature billing account.

## Public Listen workbench
- `tools/listen/` processes short user-selected WAV files locally; it is separate from synthetic Field Notes and the private database. Preserve no-upload/no-browser-storage behavior and explicit manual playback.
- `talk2nature.annotation.v1` is preliminary annotation metadata, not an admitted research manifest. A matching checksum does not prove rights, consent, identity or biological meaning. Do not automatically admit it to training/private storage.
- Run `node --test tests/demo.test.mjs tests/listen.test.mjs` plus repository/site checks after relevant changes. Reproduce browser JSON export/reimport and the Python `talk2nature.annotations` report for release checks.

## Public Nature Station
- `tools/station/` implements user-started, foreground-only local microphone capture and a silent synthetic pipeline. Read `docs/NATURE_STATION.md` for current bounds and the future device/AI architecture. This is separate from the private synthetic-only database.
- Preserve bounded event storage, visible permission/start/stop, hidden-page/interruption cleanup, pending-permission cancellation, zero worklet speaker output and manual post-session playback. No automatic animal playback, background browser promise, upload, browser persistence or research admission.
- `talk2nature.station.v1` is preliminary relative-time metadata. A following sound is not a reply; undetected sound is not silence. Preserve discarded-event tombstones until whole-session discard and exclude calibration from complete quiet-window claims.
- Run `node --test tests/demo.test.mjs tests/listen.test.mjs tests/station.test.mjs` plus repository/site checks for public audio changes. Verify synthetic browser capture, review/export and responsive layout; distinguish this from actual microphone and physical-phone testing.

## Installable public Field Companion
- `web/app_build.py`, `web/templates/app*` and `web/assets/app*` generate `/app/` (home, Station and Sound desk) and `/mobile/` (install/share page). Read `docs/MOBILE_AUDIT.md` for the current product audit and distribution plan.
- Offline setup is user-triggered and saves an exact public-shell allowlist only. Preserve `/app/` service-worker scope, no runtime-response caching, no private/admin routes, no audio/notes, credential-free precaching, bounded revision cleanup and no forced mid-session updates. Do not turn offline availability into a persistent-recording or background-capture claim.
- Preserve Station session UUID filenames, declared unverified device clock, WAV checksums and storage-limit event tombstones. These do not establish rights, meaning or research admission.
- Use `node --test tests/*.test.mjs`, Python repository tests, public/local build checks and browser offline workflow checks after relevant mobile changes. No native binary, physical-phone installation or App Store/Google Play release is claimed until separately verified.

## Evidence graph and sound notebooks
- October 2: `docs/DISCOVERY_PLAN.md` records the multimodal/plant/fungal research direction and hosting gates. Do not claim its future media/model schema is deployed.
- `talk2nature/knowledge.py` and `admin/knowledge.py` project versioned citations and owner-only research lineage from authoritative records. Preserve frozen references, public/private separation and withdrawal behavior. Citations are not corroboration; graph exports are not training admission.
- Listen `.t2n` notebooks bundle a bounded WAV and annotation metadata locally; validate audio/checksum/labels before replacing work. Preserve optional technical formats, no upload/persistence and dirty-draft protection. Run notebook tests and browser save/reopen checks after changes.

## Synthetic media/model lineage
- Schema v2 adds research_media, media_sync, model_runs, model_inputs and model_results. Read docs/MEDIA_LINEAGE.md before changing these records. Existing databases require explicit migration; runtime must not silently migrate PostgreSQL or a legacy SQLite store.
- Descriptors and outputs are invented metadata only. Preserve no-object/no-upload/no-model-execution boundaries, pre-review media/alignment freezing, exact release/input/split membership, and transactional withdrawal invalidation across dependent runs. Preserve observation labels separately from predictions.
- Run both adapter suites with scripts/test_postgres.py, migration/recovery tests and existing publication checks after lineage changes. Never run disposable test resets against an existing database.


## Whole-moment observation mode
- `web/assets/window-model.mjs` adds a separate user-started 30-second continuous mode with `talk2nature.observation-window.v1` journals. Preserve quiet samples, exact sample bounds, incomplete/interruption/discard status and bounded memory. Window entries are not detected vocalizations; omit detector/response-window inference.
- Companion mode defaults to Whole moment; public exports remain local and research admission remains closed. Include `tests/window.test.mjs` through the existing `node --test tests/*.test.mjs` command and keep the module in the exact offline allowlist.
- `research/budgerigar_sample_report.json` is an aggregate structural inspection, not an admitted dataset. Its optional SciPy inspection script parses only the checksum-pinned MAT sample in ignored external storage; no MATLAB code or workspace is executed.


## Guided observation UI
- `web/assets/observation-ui.mjs` supplies human-entered quick notes and complete/partial/discard-aware recaps. Preserve `user-entered` provenance, unknown sound sources, the marker limit, truthful synthetic labels and unadded-draft disclosure. No quick note is an inferred behavior or training label.
- Preserve phase-aware mobile Stop access, live-region restraint, reduced-motion/transparency support, confirmed reset and export feedback. Keep this UI module in the public offline allowlist. Test via `node --test tests/*.test.mjs` and meaningful browser workflows.

## Public research atlas and next goals
- Read `docs/RESEARCH_ATLAS.md` and `docs/ATLAS_NEXT_GOALS.md` for geography coverage, location-review scope and future milestones.
- `content/atlas-places.json` and note-level `atlas` metadata describe coarse public literature locations. Preserve cited passages, animal-origin versus study-region roles, explicit unknowns and separate observation/publication dates. Never substitute author affiliations for study sites or expose participant/sensitive wildlife coordinates.
- `content/atlas-goals.json` defines measurable coverage targets and future review/hosting gates. Compute coverage from validated records; a multi-site note counts once. Do not turn planned approvals, recruitment or participant releases into completed progress.
- Atlas location citations may use an explicit public full-text review URL. Publish short original summaries and links, not downloaded PDFs or review screenshots. The atlas is outside the app's offline scope and never reads private observations.
- Run repository Python/Node suites, both site-build checks and focused desktop/mobile atlas/goals checks after relevant changes; synchronize public metadata without changing frozen study evidence or the synthetic-only admission gate.
