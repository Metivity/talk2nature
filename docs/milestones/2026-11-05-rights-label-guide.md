# Explain catalog rights statuses in the evidence map

**Date:** November 5, 2026  
**Question:** can a researcher tell from the public evidence map what catalog rights statuses mean and whether a listed resource is ready to use?

## Evidence and decision

Audited all 378 resource records in [`research/resources.json`](../../research/resources.json), against the field requirements in [`talk2nature/collection.py`](../../talk2nature/collection.py) and the current evidence-map rendering in [`web/knowledge_build.py`](../../web/knowledge_build.py). Every resource had component-specific license, scope, conditions, source evidence, and separate research, commercial, and redistribution statuses. In 193 records, at least one of those three uses is marked `unresolved` or `not_admitted`. This count does not establish that the other records are legally cleared; `conditional` still depends on each record's conditions and project gates.

No article, data, code, model, recording or weight was newly downloaded or reviewed. The existing per-resource source URLs and review-depth records remain the evidence; this milestone audits how the catalog explains its own metadata.

## Change and acceptance

Added a compact rights guide to the public evidence map. It explains `conditional`, `unresolved` and `not admitted` in plain language; names each record's component, source evidence and conditions as the things to inspect; and distinguishes paper citation from data/code/media/model reuse. A generated count reports how many resources have at least one unresolved or not-admitted use status. A regression test recomputes that number from the catalog and checks the explanations and separate acquisition/analysis gates.

The guide is collapsed by default to keep the dense catalog scannable, but its summary has a 48-pixel target. On narrow screens, each definition becomes a single column. Acceptance checks: Python **302 passed, 1 skipped**; Node **188 passed**; public build **197 pages plus 404**; `scripts/check_site.py` **198 HTML documents and 13,835 links checked, with all 197 public routes reachable**; 320px and 390px Chromium review of the evidence map and expanded guide, with no horizontal overflow, failed requests or page errors.

## Limits and next decision

The statuses are project screening metadata, not legal advice or blanket permissions. The count is not a dataset-readiness score. This change does not alter rights decisions, admit resources, authorize acquisition, training or redistribution, or establish independent research review. Next, use the map's per-record evidence links to prioritize rights clarification only for resources tied to a named, independently reviewed research question; otherwise keep the research catalog metadata-only.
