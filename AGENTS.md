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
- Owner Google identity must be checked server-side and pinned by stable subject. Do not authorize the entire Metivity domain. Google Cloud account verification is complete. Dedicated project `talk2nature` was created under raviv@metivity.com in the metivity.com organization; no billing was attached. OAuth configuration is still being completed; a live client/login is not yet verified.
- No paid cloud budget has been approved for this phase. No private database on GitHub Pages or ephemeral serverless storage; private origin/region and backup/withdrawal requirements must be resolved before hosted use.
- Field Notes study/session/evidence tables and the catalog import are documented in `docs/FIELD_NOTES.md`. `python3 -m admin.catalog` imports public metadata only. Preserve frozen study/evidence versions and the distinction between participant observations and external source samples. Study/session records have no deletion UI yet and must remain synthetic.
