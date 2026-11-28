# Google discovery follow-up — November 28, 2026

This is a Search Console readback, not an indexing or ranking guarantee. The existing Talk2Nature URL-prefix property was inspected through the authorized Metivity Google account. No property, verification, permission or host configuration changed.

## New evidence

- The sitemap submission still showed **Couldn't fetch**, type **Unknown**, zero discovered pages and a last read of **November 25**. Its detail view said **Sitemap could not be read**. The sitemap was not resubmitted.
- URL Inspection for `https://metivity.github.io/talk2nature/contribute/` succeeded. The indexed-data view said **URL is unknown to Google**, with no referring sitemap, no referring page and no recorded crawl. This is a discovery/coverage observation, not a finding that the live page is inaccessible.
- A live test of that exact URL succeeded using **Google Inspection Tool smartphone**. It reported **URL is available to Google**, **Page can be indexed**, **Crawl allowed: Yes**, **Page fetch: Successful** and **Indexing allowed: Yes**. The declared canonical was the exact contribution-page URL. Google-selected canonical is determined only after indexing.
- One indexing request was made for the contribution page after that successful live test. Google confirmed **Indexing requested** and stated that the URL was added to a priority crawl queue. No visible CAPTCHA challenge was solved and the request was not repeated. Queue acceptance is not proof of indexing.
- The Page indexing report was last updated **November 23** and showed **13 indexed pages**. Its headline said zero not-indexed pages, while the reason table contained one **Crawled – currently not indexed** entry. No total excluded-page count is inferred from that inconsistent display.

## What this changes

Google's live inspection can fetch and index the contribution page in principle. This narrows the earlier uncertainty about that URL's accessibility. It does **not** diagnose the sitemap-fetch failure, prove the entire site is accessible to every Google crawler, or show that the page has entered the search index.

The live public software remains the November 25 deployment at `12ac68383a82d0c04cdcd625bf5fca0ed1276bf1`; public `main` at this check was `8bcaf84c5f4227774e5b90cb38ef8aa6f04ce930`, which adds documentation only. The earlier [197-route release check](LIVE_RELEASE_2026_11_25.md) is separate from this Google inspection.

## Next check

Revisit the contribution page's indexed-data view and the existing sitemap report after Google processes a new crawl or report update. Do not repeatedly request indexing or resubmit the sitemap while the request is queued. If a new reproducible fetch error is reported, diagnose that exact response before changing working site files.

Google's [URL Inspection guidance](https://support.google.com/webmasters/answer/9012289) distinguishes indexed information from live testing. Its [recrawl guidance](https://developers.google.com/search/docs/crawling-indexing/ask-google-to-recrawl) explains the limits of an indexing request. No new traffic/performance comparison was made in this check.
