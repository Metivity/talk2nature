# Project status

Updated September 30, 2026. Public launch is complete; funding and scientific-pilot dependencies remain.

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
