# Live release check: first-use UX

## November 25 — host-level crawl verification

The current release and native file-picker walkthrough are recorded in [the release receipt](LIVE_RELEASE_2026_11_25.md). The verifier now also checks the host-root robots policy against all sitemap pages and the sitemap itself. `robots_names_sitemap` retains its existing meaning for the generated project artifact. `project_robots_is_crawler_policy` makes its scope explicit, and `host_robots` reports the effective URL, HTTP status, web Googlebot permission and sitemap hint separately.

A 404 at the host root is accepted under Google's documented no-restriction behavior. A 429, server error or network failure fails verification rather than claiming crawl access. Matching host rules that block any listed page or the sitemap also fail. This does not verify Google indexing or that Google's network receives the same response. See [the SEO audit](SEO_AUDIT.md) for sources and the current Search Console limitation.

## November 5 historical snapshot

**Reviewed:** November 5, 2026  
**Source revision:** `a55ff385db8809617ba92e1cb2d4ea28171f02e9` (main after PR #730)  
**Purpose:** ensure the post-deployment check tests the user-facing changes instead of only page reachability and SEO metadata.

## Change

`scripts/check_live_site.py` now includes the homepage, contribution page, Listen, saved-session Compare, annotation Compare, and the existing app/research routes in its release check. It verifies that the internal feedback phrase is absent, the homepage links to the invitation, researcher/developer/source-suggestion paths are visible, and file pickers explain phone Files access, desktop browse/drop behavior, supported limits, and accepted file types. The existing sitemap-wide canonical, indexability, reachability, and robots checks still run.

Tests cover both the updated pages and regressions for internal feedback copy and old file-picker instructions.

## Live read-back

A TLS-verified read using the installed `certifi` CA bundle checked the current Pages release. It has 154 sitemap routes. The expanded verifier found seven problems:

- The internal feedback phrase is still visible on the homepage.
- The live contribution page lacks the new direct role paths.
- The live Listen page lacks the phone file-picker guidance.
- The live Compare page lacks the current ZIP-opening instructions.
- The live Station page lacks its current disclosure.
- `/tools/annotation-compare/` is missing from the sitemap.
- `/tools/annotation-compare/` returns 404.

The merged main source contains the corrected UX, so these failures show a stale publication. They do not indicate that the updated source failed its local checks. The live request read page text, headers, sitemap and robots only; it did not access recordings, private data or Search Console.

## Verification

- `python3 -m unittest tests.test_live_site -v` — 17 passed.
- `python3 -m unittest discover -s tests -v` — 300 passed, 1 skipped.
- Public build — 197 pages plus 404.
- `python3 scripts/check_site.py` — 198 HTML documents, 13,829 links, 197 public routes reachable.
- All eight live UX contracts pass against their generated candidate pages.
- `git diff --check` — passed.

This checker validates page copy and file-input declarations; it does not emulate a native phone file chooser or assistive technology. Search Console indexing remains unverified.

## Next release action

Run the manual GitHub Pages workflow for the approved main revision under the Metivity GitHub account. After deployment, require this live check to pass and separately inspect Search Console for indexing status. Workflow dispatch is manual and was not performed during this audit.
