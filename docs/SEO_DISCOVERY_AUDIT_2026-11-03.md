# Search discovery snapshot — 2026-11-03

## Question

Can a public search surface Talk2Nature's research work, and what can this check establish before the newest research page is published?

## Observed evidence

- A connected web-search query for `site:metivity.github.io/talk2nature/ Talk2Nature animal audio` returned the homepage, the live resource directory, research frontiers, research atlas, evidence map, MammAlps review, speech-pretraining review, shared dataset-loader review, reading paths, ice-crystal evidence review and V33DA review. The tool labeled these results as crawled between four days and two weeks before this check.
- Opening the public [resource directory](https://metivity.github.io/talk2nature/research/resources/) today showed its live heading at **284 records**. The current local `research/resources.json` contains **354 records**. This is a measured 70-record publication gap, not a discovery or ranking metric.
- A site-restricted query for the new `animal-audio-model-landscape-2026` route did not return that route. The page is in an open draft PR and is not yet part of the deployed site, so this is expected and does not demonstrate a crawl failure.
- The connected tools in this check do not expose Google Search Console. No impressions, clicks, indexed-URL count, position or sitemap-processing status was available.

## Interpretation

The search tool can find several established research pages, which is evidence of search discovery for those URLs only. Its crawl labels and result selection do not establish Google indexing, audience reach, ranking quality or search traffic. Do not call the new page indexed until its route is published and a search-engine-specific inspection is available.

## Next verification

After the PR is accepted and the authorized Pages deployment completes, fetch the exact route and confirm its HTTP status, canonical URL, robots directive and presence in the live sitemap. Then use Search Console URL Inspection and sitemap reporting if the owner account is connected. Recheck the live catalog count against the source only after deployment; keep crawl evidence separate from traffic or ranking claims.

## Limits

This is a one-time, tool-mediated search snapshot, not a repeatable rank-tracking study. No analytics account was accessed and no tracking code was added. The observed resource-directory count comes from the live page; the 354 count comes from current local source and has not been published.
