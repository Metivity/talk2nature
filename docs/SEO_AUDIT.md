# Search discovery and indexing audit

## November 25 follow-up — check the host crawl policy

The earlier `robots.txt` result below describes `/talk2nature/robots.txt`. Google applies crawl rules from the host-root `/robots.txt`; a file in a project subdirectory does not establish crawler policy. The revised live verifier now fetches `https://metivity.github.io/robots.txt` and checks its web Googlebot rules against the sitemap and all listed pages. It covers specific and wildcard agent groups, merged groups, longest matching paths, allow ties, UTF-8/escaped paths, wildcards and end anchors. Server failures and rate limiting leave the policy unresolved and fail the check.

The current host-root response is **404**. Google's [robots specification](https://developers.google.com/crawling/docs/robots-txt/robots-txt-spec) treats client errors other than 429 as an absent robots file with no crawl restrictions. Thus this response does not explain the Search Console sitemap-fetch error. The project artifact still names the sitemap, but it does not provide automatic discovery through root robots. Search Console accepted the November 25 resubmission; processing remains unresolved as recorded in the [live-release receipt](LIVE_RELEASE_2026_11_25.md).

The Search Console settings page confirms the project owner can access the URL-prefix property. Root robots and Crawl Stats reports are disabled there because they require a root-level property. No root property, domain setting or other repository was changed. A fresh run of the revised verifier passed all **197** live sitemap pages. This records the responses received by the checker and their applicable rules; Google's fetch result remains a separate observation.

## November 2 historical snapshot

**Checked:** November 2, 2026. This is a technical/discovery snapshot, not a ranking forecast. Owner-only query and page-level Search Console details are kept outside the public repository.

## Verified public signals

- The live `robots.txt` returns HTTP 200, allows crawling, and names `https://metivity.github.io/talk2nature/sitemap.xml`.
- The sitemap returns HTTP 200 as `application/xml`. The live XML parses as a sitemap `urlset` with 154 URLs.
- Search Console's submitted-sitemap detail still says **“Sitemap could not be read”** and shows zero discovered pages. The report's last read is November 2. No specific XML, 404, robots or server error is displayed.
- The Search Console manual-actions and security-issues reports show **no issues detected**. Its Core Web Vitals panel has no field data, which is not a passing field-performance result.
- Search Console page-indexing data is older than the latest source changes. Page-level examples and index counts remain in the owner-only snapshot.
- Direct requests to two research routes present in the local candidate still return HTTP 404 on live Pages. Candidate publication and Google indexing are separate gates.

Google's [Sitemaps report guidance](https://support.google.com/webmasters/answer/7451001) lists robots restrictions, unresolved manual actions, a wrong URL and general access errors among fetch-error causes. The checks above rule out some of these locally, but a successful direct request does not prove Google's crawler received the same response.

## Decision and next checks

No `robots.txt` or sitemap code change is justified by this snapshot: the live file is valid and reachable, while the Search Console state is generic and has no actionable sub-error. Do not mark the sitemap issue fixed, resubmit it repeatedly, or request validation until a specific cause appears. Recheck after Google processes the current submission.

First bring the reviewed source candidate through the repository's authenticated pull-request and Pages release path. After deployment, verify the newly added routes return HTTP 200, compare the live sitemap against the generated route set, then use URL Inspection on a representative new research page. Keep traffic/query details private; interpret the small Search Console sample cautiously. The owner-only snapshot is ignored at `data/private/seo-search-console-2026-11-02.json`.
