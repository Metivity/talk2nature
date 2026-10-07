# Talk2Nature project audit

**Audit date:** October 7, 2026
**Scope:** current local repository and noindex site build, selected live Pages routes, public research/tool boundaries, private workbench status, governance and dated opportunities. This is an implementation and consistency audit, not a scientific peer review, legal opinion, security penetration test or participant study.

## Overall assessment

Talk2Nature makes sense as an early open research library and a set of local, reproducible observation tools. It is not yet an animal-communication product, shared recording platform, hosted research database or validated machine-learning system. The public materials generally say this clearly, and the repository has careful rights, provenance, uncertainty and animal-welfare boundaries.

At the time of this October 7 audit, the main source of confusion was **release drift**: the local branch contained complete pages and workflows that were absent from the live Pages site. Direct visits to the live `/community/university/` and `/tools/interop/` routes showed the project's 404 page. They were local-only additions, not broken links from the live navigation. The October 8 release addendum below records the authorized publication work and its outcome.

## What is in place

- The static public site has a clear top-level path through research, tools, videos, project approach, the app and participation. Its local build is deliberately `noindex`; the public builder requires the confirmed Pages origin.
- The research catalog distinguishes summaries from original work, records review depth and limitations, and links the atlas to cited study locations. A location pin is not an observation from Talk2Nature.
- The browser Field Companion, Listen, session comparison and Audacity handoff keep recording work local and user-controlled. They do not upload recordings or infer animal meaning. The PWA shell caches public files only; capture is foreground-only.
- The private FastAPI workbench is owner-restricted and rejects real research data. Local owner sign-in and access checks have been exercised. Hosted deployment, durable private storage and real-data intake remain unverified and closed.
- Code and original summaries have distinct licenses. Third-party recordings, articles, datasets and model weights retain separate rights. No formal university, UN or conservation partnership is claimed.
- KeeKee, the likely parrot prototype from Downloads, has only been reviewed statically. Its provenance and component licenses are unresolved; its code, sound files and user data were not imported.

## Issues found and addressed in the local tree

1. **Funding dates needed a fresh check.** The Tnufa and Pre-Seed records were still marked as checked September 30. The Israel Innovation Authority now lists both deadlines as October 8, 2026, at 12:00. The records and source dates now show the October 7 check, and the page links the cutoff to the official open-applications listing. Tnufa applicant route and project facts remain unconfirmed. Pre-Seed requires an Israeli startup company and signed investor documentation covering at least 15% of the proposed round. Neither application is marked submitted. See the [Tnufa rules](https://innovationisrael.org.il/programs/%D7%9E%D7%A1%D7%9C%D7%95%D7%9C-%D7%AA%D7%A0%D7%95%D7%A4%D7%94-%D7%A7%D7%A8%D7%9F-%D7%94%D7%94%D7%96%D7%A0%D7%A7/), [Pre-Seed rules](https://innovationisrael.org.il/programs/preseed/) and [official open-applications list](https://innovationisrael.org.il/%D7%A4%D7%AA%D7%95%D7%97%D7%99%D7%9D-%D7%9C%D7%94%D7%92%D7%A9%D7%94/).
2. **A home-page count label was too vague.** “Starting notes” and “sources in the research inventory” are now “research notes” and “source records.” The source count includes different kinds of public references, not only papers.
3. **Local and deployed site must not be confused.** The current working tree generates the university evaluation and Sound Handoff Lab pages and tests their links. The live site has not received these changes. The public build and deployment were not run as a release action in this audit.

## Important project gaps

- **No shared observation database:** public tools export to the participant's device; there is no public upload or contribution endpoint. The local private workbench is synthetic-only. The website must not imply that a field recording will appear in a shared database.
- **No demonstrated biological result:** there is no Talk2Nature animal-communication model, translation, species recognizer, validated behavior classifier or controlled animal exchange. The Station's simple level detector is a capture aid, not a biological finding.
- **No approved field study:** an independent scientific lead, protocol, ethics/welfare decisions, participant and recording consent, retention/withdrawal plan, rights review and sensitivity controls must precede any real-data intake or playback experiment.
- **No independent evaluation yet:** the university page is a synthetic workflow invitation only. An independent researcher has not been shown completing the exact workflow in this audit.
- **Governance capacity is small:** Raviv is the sole maintainer. Succession, an appeal route for conduct decisions, an archival DOI/release practice and a shared research-data governance model remain open.
- **Legal and public identity decisions remain open:** the project name has not been cleared as a trademark, and the funding applicant/legal entity and country/residency facts are not established in project records.
- **Global awareness is a plan, not an outcome:** the site has technical SEO elements and useful public pages, but this audit does not establish search indexing, site traffic, adoption, university interest, funding or partnership.

## Next sequence

1. Keep the October 8 funding records accurate; do not submit an application until the applicant, eligibility, project plan, budget, IP position and required declarations are confirmed.
2. Review the local-only page set as one release. Run a public build with the exact Pages origin, inspect the generated `dist/` for private files, then verify every newly linked live route and asset after an explicitly authorized deployment.
3. Ask one independent researcher to try the synthetic workflow and report a failure or information-loss case. Treat this as software evaluation, not research recruitment or endorsement.
4. Find a qualified scientific lead and settle one passive, species-specific question, annotation protocol, welfare limits and data-governance review before opening any real-data path.
5. Only then decide whether hosted storage, a native dedicated-phone app, camera/video, or model training addresses a demonstrated need.

## Verification and limits

- JavaScript tests: **79 passed**.
- Repository Python tests: **51 passed**.
- Owner-workbench suite: **104 passed, 49 PostgreSQL integration tests skipped** in the default run because no disposable PostgreSQL test URL was configured. The documented disposable-cluster harness was attempted, but local PostgreSQL initialization was blocked by the environment's denied shared-memory (`shmget`) call; this is an environment limitation, not a successful PostgreSQL integration result.
- Local build: **70 pages plus 404**; site checker: **71 HTML pages and 2,889 local links**.
- A separate static pass found no missing page title, description, English language declaration, single-H1 structure, duplicate IDs, missing image `alt` attributes or unsafe blank-target links across the 71 HTML files.
- Browser review checked the local home, app, university page, Sound Handoff Lab and funding page. At a 390 CSS-pixel viewport, the homepage and university page had no horizontal overflow. The live Pages funding page was inspected; the two unpublished routes returned the designed 404. No microphone, camera, animal playback, deployment or external message was used.

## October 8 release and open-source review

Raviv authorized deployment. The release preparation adds `docs/OPEN_SOURCE_PRACTICE.md`, a PR checklist and GitHub issue-creation contact links. The project already had distinct licenses, maintainer governance, conduct/security routes, citation metadata, issue forms and least-permission public CI. Remaining gaps are a sole maintainer, no independent science/reproducibility review, no verified branch-protection configuration, and no archival DOI or research-data governance service. The new plan prioritizes useful reproductions and response capacity rather than popularity metrics.

The IIA pages and open-applications list were checked again on October 8; they show the Tnufa and Pre-Seed cutoff at 12:00 Israel time that day. No funding submission was made: eligibility facts and required declarations are not confirmed. See the [official open-applications list](https://innovationisrael.org.il/%D7%A4%D7%AA%D7%95%D7%97%D7%99%D7%9D-%D7%9C%D7%94%D7%92%D7%A9%D7%94/) and the [open-source practice plan](OPEN_SOURCE_PRACTICE.md).
