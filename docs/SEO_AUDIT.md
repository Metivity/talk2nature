# Search discovery and indexing audit

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
