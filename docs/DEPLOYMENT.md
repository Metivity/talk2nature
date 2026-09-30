# Public deployment

Raviv approved publication and deployment on September 30, 2026 using the account associated with raviv@metivity.com. GitHub associates that email with the Metivity user. Use this account for Talk2Nature; the funding applicant/legal entity remains a separate unresolved decision.

- Repository: https://github.com/Metivity/talk2nature (public; default branch main).
- GitHub Pages returned origin: https://metivity.github.io/talk2nature/ (HTTPS enforced).
- Workflow: `.github/workflows/pages.yml`, manually dispatched. Source pushes alone do not deploy.
- Build uses the origin supplied by `actions/configure-pages`, runs tests and the generated-site checker, then uploads only `dist/`.
- Current release outcome is recorded in `docs/STATUS.md`.

For an authorized future release, push reviewed changes, dispatch `pages.yml` on main, and inspect the completed deployment. Check home, an evidence note, live search, mobile navigation, 404, canonical URLs and sitemap. Keep funding drafts, audit, recordings, screenshots and credentials outside the published artifact.

Local public-build check:

```sh
python3 web/build.py --public --base-url https://metivity.github.io/talk2nature --repo-url https://github.com/Metivity/talk2nature
python3 scripts/check_site.py
```

Search Console uses the raviv@metivity.com owner session and the exact URL-prefix property https://metivity.github.io/talk2nature/. Its public ownership tag is stored in `content/publication.json` and emitted only on that origin’s public home page; retain it after verification. Verification/submission outcomes are recorded in `docs/STATUS.md`. A custom domain needs confirmed ownership and DNS access; none has been purchased. For project Pages sites, robots.txt under the project path is not the origin-level robots file; do not claim it controls the whole host. Use page metadata and submit the project sitemap through the owner property when available.

The website links GitHub's privacy statement and has no analytics, signup or upload service. Local previews remain noindex by default; keep previews on loopback or authenticated hosting because noindex is not access control.
