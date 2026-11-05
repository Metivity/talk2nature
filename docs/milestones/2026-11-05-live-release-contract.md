# Live release contract: contributor paths and mobile file selection

**Date:** November 5, 2026  
**Question:** did the merged mobile file and contribution improvements reach the live Pages site, and does the release check cover the requested contributor shortcuts?

## Evidence reviewed

- PR [#735](https://github.com/Metivity/talk2nature/pull/735) merged to `main` as `937eb2a85186e969b25a58938d2dfeee0b056f25` after the repository's required Public Checks passed.
- The merged source includes clearer file-selection feedback and direct links to researcher, developer and naturalist paths.
- A read-only inspection of the public [contribution page](https://metivity.github.io/talk2nature/contribute/) still returned the older copy and did not show the three direct role links. It also showed internal feedback copy that the source page and source tests exclude.
- A general search result for the [research directory](https://metivity.github.io/talk2nature/research/resources/) still described 284 records and was marked crawled six days before this check. This is an old search-result snapshot, not a current live catalog count or Search Console report.

## Change and verification

Extended `scripts/check_live_site.py` so the post-deployment contract requires these fragment links and labels on `/contribute/`:

- `#contribute-researchers` — “I’m a researcher”
- `#contribute-developers` — “I’m a developer”
- `#contribute-naturalists` — “I’m a naturalist or supporter”

Added a regression test that removes one shortcut and confirms the contract rejects the page. Verification on this candidate: Python **301 passed, 1 skipped**; Node **188 passed**; explicit-origin public build **197 pages plus 404**; `scripts/check_site.py` **198 HTML documents, 13,834 links checked, 197 public routes reachable**; `git diff --check` passed.

## Limits and next decision

This update improves the release gate; it does not publish the merged UX or establish search indexing, ranking, traffic, physical-phone behavior or assistive-technology acceptance. Search Console was not authenticated. The manual Pages workflow remains pending. After publication, run `scripts/check_live_site.py` against the deployment URL and inspect the live contribution and file-opening flows. Then capture Search Console coverage separately from public search-result sampling. No animal or participant data were used.
