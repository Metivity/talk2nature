# Project status

Updated September 30, 2026. Public launch is authorized and in progress; funding and scientific-pilot dependencies remain.

## Completed locally

- Working brand: Talk2Nature / Listen closely. Understand carefully. Name clearance remains open.
- Scope, open-source/business approach, contribution rules and company boundaries documented.
- Apache-2.0 original software and CC BY 4.0 original public-summary policy; no third-party audio or model weights included.
- Responsive static website: 23 content pages plus 404, original SVG identity, 15 evidence notes, 54-source inventory, ten dated opportunity records, roadmap, methods, contribution and privacy guidance.
- Technical SEO preparation: unique titles/descriptions, structured page metadata, canonical/base-path support, sitemap, robots and social metadata. Local builds default to noindex. The public build allows indexing; search-engine indexing is not yet verified.
- Research utility: metadata validation and deterministic connected-group splits across individuals, sessions and source hashes. Synthetic fixtures only; no trained model or empirical result.
- Local Tnufa preparation brief and application register in ignored `funding/`. No submitted application or confirmed eligibility.

## Validation

- Twelve unit/integration tests pass, including leakage chains, mixed synthetic/real rejection, input ordering, missing origin and public project-subpath links.
- Generated-site checker passes: 24 HTML pages and 516 link references checked locally. External URLs are drawn from the audit; not all external pages were re-fetched during this build.
- Browser: desktop visual inspection; live search, taxon filter, combined filter, zero results and reset verified; evidence page reached with keyboard navigation.
- Responsive rendering checked down to a 390 CSS-pixel layout; measured document width equals viewport width. Mobile menu opens and Escape closes it. Corrected a heading whitespace issue found during responsive review.
- In-app browser pointer navigation did not reliably activate links during automation; keyboard navigation worked. Recheck pointer navigation in the eventual public browser. Do not call this a full accessibility audit.

## Preview

- Loopback server: `http://127.0.0.1:4173/`, serving only `dist/`.
- Start again with `python3 -m http.server 4173 --bind 127.0.0.1 --directory dist` if necessary.
- Saved desktop image: `tmp/site-preview/home.png` (local only).
- Preview has no signup, analytics, uploads, API keys, live model or database.

## Public launch — September 30, 2026

Raviv approved deployment under raviv@metivity.com. The authenticated GitHub user Metivity is linked to this email through GitHub's commit-author association. Created public repository https://github.com/Metivity/talk2nature and configured GitHub Pages; the service returned https://metivity.github.io/talk2nature/ with HTTPS enforced. Release verification is in progress; repository/site creation alone does not confirm a successful deployment.

The initial public snapshot uses the confirmed repository-local Git identity. Earlier unpublished draft history remains on the local codex/foundation branch. Private funding drafts, the audit and raw/source papers remain excluded.

## Next actions

1. Finish and verify the public deployment; record workflow URL and live checks here.
2. Verify Search Console ownership and submit the sitemap if the authorized owner session is available. Indexing/ranking is not guaranteed.
3. Funding still needs an applicant's legal name, country, individual/company status, eligibility facts, defensible R&D contribution and budget. No application has been submitted. Current Tnufa forms were not retrieved: attachment access failed and direct page retrieval returned HTTP 403. Do not use the old form surfaced by search. Previously verified deadline: October 8, 2026.
4. Scientific pilot needs Kiki ownership/access if relevant, one species/question, usable independently labeled observations and an appropriate collaborator. No Kiki assets imported, animals recruited, weights installed or model accuracy claimed.

## Research checkpoint

The library has 15 notes and 54 source records, including three source-based method reviews. Exact candidate model references, licensing distinctions and data limitations are in `docs/MODEL_DATA_DECISION.md`. These are not expert endorsements or replications. The tested metadata/split utility uses synthetic fixtures only. Further model integration depends on a concrete dataset and question.

Keep work bounded to these milestones; broader reading and optional styling remain backlog.
