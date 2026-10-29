# Public deployment

Raviv approved publication and deployment on September 30, 2026 using the account associated with raviv@metivity.com. GitHub associates that email with the Metivity user. Use this account for Talk2Nature; the funding applicant/legal entity remains a separate unresolved decision.

- Repository: https://github.com/Metivity/talk2nature (public; default branch main).
- GitHub Pages returned origin: https://metivity.github.io/talk2nature/ (HTTPS enforced).
- Workflow: `.github/workflows/pages.yml`, manually dispatched. Source pushes alone do not deploy.
- Build uses the origin supplied by `actions/configure-pages`, runs tests and the generated-site checker, then uploads only `dist/`. After deployment, the workflow retries a live HTTPS check of the homepage, Field Companion and resource directory, their index/canonical metadata, the sitemap entries and the robots sitemap line. It does not verify Google indexing or ranking.
- Current release outcome is recorded in `docs/STATUS.md`.

For an authorized future release, push reviewed changes and dispatch `pages.yml` on main. The workflow verifies core live routes and crawl metadata after deployment; then inspect a representative evidence note, mobile navigation and 404 as appropriate. Keep funding drafts, audit, recordings, screenshots and credentials outside the published artifact.

Before dispatching, save the current live sitemap and compare it with the public candidate. A clean internal-link check does not detect dropped public routes. Do not release while previously published URLs disappear unless each removal has an intentional, reviewed fallback.

Local public-build check:

```sh
python3 web/build.py --public --base-url https://metivity.github.io/talk2nature --repo-url https://github.com/Metivity/talk2nature
python3 scripts/check_site.py
mkdir -p tmp
curl -fsS https://metivity.github.io/talk2nature/sitemap.xml -o tmp/live-sitemap.xml
python3 scripts/compare_sitemap_routes.py --reference tmp/live-sitemap.xml --candidate dist/sitemap.xml --base-url https://metivity.github.io/talk2nature
```

The route comparison exits nonzero if any deployed sitemap URL is missing from the candidate; new candidate URLs are listed for review. Save the live sitemap only in ignored `tmp/`. The final command is an additional release gate, not permission to publish.

Search Console uses the raviv@metivity.com owner session and the exact URL-prefix property https://metivity.github.io/talk2nature/. Its public ownership tag is stored in `content/publication.json` and emitted only on that origin’s public home page; retain it after verification. Verification/submission outcomes are recorded in `docs/STATUS.md`. A custom domain needs confirmed ownership and DNS access; none has been purchased. For project Pages sites, robots.txt under the project path is not the origin-level robots file; do not claim it controls the whole host. Google requires robots.txt in a site's top-level directory and limits its rules to that host/protocol/port ([robots.txt scope](https://developers.google.com/crawling/docs/robots-txt/robots-txt-spec)). The project sitemap is instead submitted through the verified URL-prefix property when available. Sitemap submission is a hint, not a guarantee of crawling or indexing ([sitemap guidance](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)); use the Search Console Sitemaps report and live URL Inspection to diagnose fetch errors ([troubleshooting](https://support.google.com/webmasters/answer/7451001?hl=en)).

The website links GitHub's privacy statement and has no analytics, signup or upload service. Local previews remain noindex by default; keep previews on loopback or authenticated hosting because noindex is not access control.
