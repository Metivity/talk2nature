# Open-source health and adoption plan

**Reviewed:** October 8, 2026; funding-readiness note updated October 25, 2026. This is a working project plan, not a claim of adoption or an external certification.

## What success means here

Success is a useful, trustworthy research tool that another person can understand, reproduce, correct and maintain. Stars, downloads and page views can describe reach, but they do not show that the tool solves a real workflow or supports sound science.

The plan follows GitHub's repository and community-health guidance, the Open Source Definition, CHAOSS project-health metrics and OpenSSF's security-practice guidance. These sources emphasize clear project purpose, recognized licenses, contribution and conduct paths, safe reporting, maintainable collaboration and contextual measures of responsiveness and sustainability. See [GitHub repository best practices](https://docs.github.com/en/repositories/creating-and-managing-repositories/best-practices-for-repositories), [GitHub community-health files](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file), the [Open Source Definition](https://opensource.org/osd), the [CHAOSS starter project-health model](https://www.chaoss.community/kb/metrics-model-starter-project-health/) and [OpenSSF Scorecard beginner checks](https://github.com/ossf/scorecard/blob/main/docs/beginner-checks.md).

## Current foundation

- **Purpose and boundaries:** the project describes a cited research library and local observation tools. It does not claim animal translation, a trained Talk2Nature model, public recording intake or a hosted research service.
- **Reuse:** original software is Apache-2.0 and original public summaries are CC BY 4.0. Third-party code, papers, recordings, datasets, weights and marks keep their separate rights. Contributions do not require copyright assignment.
- **Participation:** `CONTRIBUTING.md`, `SUPPORT.md`, `GOVERNANCE.md`, `CODE_OF_CONDUCT.md` and `SECURITY.md` route contributors and sensitive reports. Issue forms cover source corrections, research questions, software bugs, reproduction, mobile checks and audio-tool compatibility.
- **Quality and release:** public pull requests run Python and JavaScript suites plus the site checker with read-only workflow permissions. Actions are pinned to immutable commit references. The `main` branch now requires a pull request, the passing `checks` workflow and an up-to-date base; force-pushes and deletion are blocked, and the rule applies to administrators. Required approvals remain at zero until a second reviewer is available. Pages deployment is separate and manual; only the generated public `dist/` is uploaded. The first tagged source release, `v0.1.0`, has version/date metadata in `CITATION.cff` and a public changelog; it remains pre-1.0 and makes no scientific-validation claim. A bounded post-release check found no configured repository webhooks or exact-title Zenodo record, so no archival DOI is claimed.
- **Research integrity:** examples are synthetic, scientific summaries state their review depth and limits, citation metadata is present, and data admission remains closed until protocol, consent, rights and hosting gates are satisfied.

This release adds a pull-request checklist and issue-form contact links so a newcomer can find contribution, support, security and conduct guidance at the point they need it.

## October 11 follow-up: make the first contribution concrete

The repository now has three explicit entry tasks in `CONTRIBUTING.md`: try the microphone-free phone rehearsal, reproduce the synthetic researcher kit from a clean checkout, or check one claim against its primary source. Each task states what to report and links to the matching issue form. This is a contributor guide, not a claim that tasks have been independently completed or that a public invitation has been sent. No recording, model, or private data is needed for these starts.

A regression test now ties the three guide links to their expected GitHub issue-form paths and confirms each referenced form exists in the repository. It prevents a common documentation-drift failure but does not test GitHub's hosted rendering, form submission or first-time contributor success.

Next measure whether a first-time contributor can choose a task and submit a useful report without maintainer guidance. Keep the report self-declared as independent, assisted or maintainer-led; a passing form or CI run does not prove adoption or biological validity.

## October 13 follow-up: make the evaluator report approachable

**Question:** does the public report form make the no-code browser route legible to a non-programmer while keeping enough provenance to review a result?

**Change:** renamed the default issue title from “Reproduction” to “Workflow report,” put the no-setup browser comparison first, linked the code route separately, and added plain-language examples for page/version, device/browser, actions and usefulness. An evaluator may enter “unknown” for a software version they cannot identify. The relationship choices still default to unverified; public-report privacy warnings and the boundary for counting an independent code reproduction remain.

**Verification and limits:** a repository regression protects the visible browser route, no-code reassurance, unknown-version allowance, failure reporting and unverified default. The local issue-form YAML parses. This verifies source consistency, not GitHub-hosted rendering, first-time comprehension, screen-reader behavior or independent use. No issue was opened or submitted; independent reproduction remains zero. Next evidence must come from an outside person using the form and reporting what was confusing.

## October 12 maintainer check: source-suggestion draft flow

**Question.** Can a visitor prepare a source suggestion without a GitHub account, understand what will be shared and stop before posting?

**Observed.** On the public [source and research-question helper](https://metivity.github.io/talk2nature/contribute/source/), the empty preview action returned focus to the required title field. A completed synthetic draft displayed its contribution type, source URL, declared review depth, rationale and the disclaimer that Talk2Nature had not independently validated it. The generated GitHub issue URL contained that same draft. Source review of `web/assets/hub.js` and `web/assets/hub-model.mjs` confirms that the form validates and builds the preview/link locally; the submit handler contains no network request. The page states that drafts are not autosaved and choosing the GitHub link transmits the draft for review; creating the issue remains a separate GitHub action. I did not open the generated link or submit anything.

**Result and limits.** The basic browser flow behaved as described in this maintainer-run check. All three focused `tests/hub.test.mjs` cases passed, including configured-repository routing and rejection of unsafe or oversized drafts. The example used `example.org` and an explicit synthetic-only rationale; it is not a source proposal or contribution. I did not inspect browser network logs, so this is not a full network audit. The check also does not establish independent usability, mobile layout, screen-reader behavior, or successful GitHub issue creation. Keep independently verified contributions at zero until an outside contributor completes and reports a task without maintainer guidance.

**Next.** Narrow-phone and keyboard checks are recorded below; a screen-reader check and independent first-time contributor report remain open. Do not count a preview or generated issue link as a contribution.

## October 12 follow-up: narrow-phone and keyboard check

Checked the same public helper in Chrome at a 390 × 844 viewport. The form controls remained within the viewport, and the visible labels supplied names for the textboxes and selectors. Starting at the title field, keyboard Tab moved in order through the source URL, review-depth selector, rationale and preview button. The focused preview button had a clear outline and remained above the fixed bottom navigation. The form was left blank; no draft was generated or sent.

This confirms one maintainer-run narrow-viewport and keyboard path. It is not a physical-phone or virtual-keyboard test, a screen-reader audit, an independent usability test, or evidence across every breakpoint. No product change was needed from this check. Keep those other checks open before broad contributor outreach.

## Measures that fit the project

Review these quarterly, using issue/PR records and voluntary reports rather than adding analytics or collecting user media:

| Measure | What it tells us | Current interpretation |
| --- | --- | --- |
| Independent workflow reproductions with exact revision and assistance level | Whether instructions and outputs work beyond the maintainer | Zero independently verified reproductions is the current baseline; a maintainer rerun does not count. |
| Tasks completed, blocked and the reasons people report | Whether the tool solves a real job and where it fails | Collect a small number of specific reports before expanding features. |
| Time to first useful response and age of unresolved issues | Whether the current maintainer capacity matches the support surface | Best-effort support only; use trends to narrow scope or recruit help, not to promise an SLA. |
| Contributions by kind: corrections, tests, documentation, accessibility, methods review and code | Whether there are meaningful ways to participate beyond software engineering | Credit useful work; do not treat volume or a particular mix as a target. |
| Maintainer time and continuity risks | Whether maintenance can continue safely | One maintainer is a real operational limitation. Pause invitations that exceed available review capacity. |

Do not rank contributors by volume, equate issue closure with quality, or use stars as the project's scientific-impact measure. CHAOSS recommends interpreting responsiveness and sustainability in context, not treating one metric as a verdict. See its [starter model](https://www.chaoss.community/kb/metrics-model-starter-project-health/) and [practitioner guidance](https://www.chaoss.community/unlocking-insights-practitioner-guides-for-interpreting-open-source-metrics/).

## Next steps

1. **Publish one coherent release.** Keep the repository tip, checked public build and deployed site aligned. Record the exact commit and live verification; do not claim a local-only feature as public.
2. **Learn from a few real workflows.** Start with the synthetic university evaluation and one independent reproducibility report. Ask what task was attempted, what failed and which existing tool already works better. Do not ask for recordings or partnership endorsements.
3. **Keep the contribution queue small and legible.** Offer a few bounded tasks with an expected result, owner and review path. Close stale requests honestly when capacity or evidence is missing; never encourage data submissions while intake is closed.
4. **Strengthen continuity before broad recruitment.** Seek a second trusted software maintainer and an independent scientific reviewer through real contributions and explicit role agreement. Do not describe an advisor, institution or partner until they have agreed.
5. **Reassess quarterly.** Use task completion, reproduction quality, response load and maintainer continuity to choose what to build, maintain, delegate or stop. Do not add a forum, telemetry or cloud intake without demonstrated need and the capacity to govern it.

## Current limits

Raviv is the sole maintainer and sole recipient for private conduct and security reports. The [continuity procedure](../GOVERNANCE.md#continuity-and-succession) documents a maintenance pause and a possible handoff, but no successor or independent appeal panel is appointed. There is no response-time commitment, public data portal, archival DOI, independent scientific lead or external reproduction yet. State these limits rather than implying organizational capacity that does not exist. Improve the project by addressing a real gap with an accountable person and a tested procedure, not by adding empty committee titles or badges.

## October 13 follow-up: pin the Pages runtime and runner image

The last Pages release passed, but GitHub warned that the pinned publication actions still invoked Node.js 20 and that `ubuntu-latest` was scheduled to move to Ubuntu 26. The official immutable `configure-pages` v6.0.0 action metadata and `deploy-pages` v5.0.1 metadata specify Node.js 24. The official `upload-pages-artifact` v5.0.0 composite definition pins `actions/upload-artifact` v7.0.0, whose action metadata also specifies Node.js 24. GitHub's runner-image notice says the `ubuntu-latest` transition to 26.04 begins October 19 and is planned to finish November 19, 2026.

Updated the manual Pages workflow to those release commit SHAs and pinned both jobs to `ubuntu-24.04`, matching the existing public/private check workflows. The workflow remains manually dispatched, keeps its read-only build permissions and separate Pages deploy permissions, and uploads only the checked `dist/` artifact. This avoids an unplanned hosted-OS change and removes the known Node.js 20 action versions without relying on floating action tags. Sources: [configure-pages v6](https://github.com/actions/configure-pages/releases/tag/v6.0.0), [deploy-pages v5.0.1](https://github.com/actions/deploy-pages/releases/tag/v5.0.1), [upload-pages-artifact v5.0.0](https://github.com/actions/upload-pages-artifact/releases/tag/v5.0.0), [artifact action metadata at the pinned commit](https://github.com/actions/upload-artifact/blob/bbbca2ddaa5d8feaa63e36b76fdaad77386f024f/action.yml), and [runner migration notice](https://github.com/actions/runner-images/issues/14748).

Local verification: the workflow parses as YAML; all 92 Python and 98 Node tests pass; the public build produces 91 pages plus 404; and the site checker validates 92 HTML documents, 4,306 links and 91 reachable public pages. PR [#65](https://github.com/Metivity/talk2nature/pull/65) passed the repository checks and merged as `d3f9b9e66e62d07296eaf2f508ac5b5ea8dd51a7`. Its manual Pages deployment [#38315358703](https://github.com/Metivity/talk2nature/actions/runs/38315358703) passed both build and deploy jobs. The run logs contained no Node.js 20, `ubuntu-latest`, Ubuntu 26 or deprecated-action matches; the two job check-runs had zero annotations. Live HTTPS checks returned 200 for the home page, Field Companion, parrot research note and sitemap. The Pages workflow maintenance acceptance check is met. These results do not establish search indexing, research validity or project adoption.


## October 13 current-main source-archive rehearsal

The researcher kit was rechecked from a fresh source archive of public `main` at `156ad928db3bc49baa200fc31e46f580efef64ac`. The synthetic annotation and grouped-split commands matched their recorded results; 103 Python tests, 105 Node tests, 82 resource validations, the 96-page local build and the 97-HTML/4,539-link site check passed. The temporary source came from an exact shallow public clone and excluded ignored/private workspace data. A macOS CRLF mismatch affected only the Windows Gradle wrapper in the clone; test execution used a `git archive HEAD` extraction and left the wrapper unchanged.

This increases confidence that the published software instructions match the current public source. It remains maintainer-run. The project still has zero independently verified reproductions and has not received a scientific specialist review. See the detailed outputs and checksums in [`RESEARCHER_START.md`](RESEARCHER_START.md).

## October 13 follow-up: recheck the moving public main branch

Public `main` advanced to `c03a928738a3b8d1086426025df1680e86308972` after the prior `156ad928` check. Repeated the researcher workflow, all Python and Node tests, catalog validation and both noindex/public-origin build checks from an exact archive of the new public commit. The tests passed (104 Python, 107 Node), 90 resources validated, and the public-origin checker found all 99 generated routes reachable. The synthetic split output remained internally consistent; the exact revision and hashes are recorded in `docs/RESEARCHER_START.md`.

The depth-one macOS clone again marked only the Windows wrapper dirty because of CRLF handling; it was left unchanged. This is a maintainer-run check, not independent reproduction. The count remains zero until a non-maintainer report is reviewed. Local worktree metadata is ahead of public `main`; do not conflate the local 112-record catalog with the 90-record published revision. No outreach or deployment occurred.

### Clone hygiene follow-up

The attribute-only fix, `native-android/gradlew.bat -text whitespace=cr-at-eol`, was published in PR #95. A fresh depth-one clone of `main` at `9a48c6509f2f52f504190ee4663b678732bc6139` now has a clean worktree; the wrapper's committed blob matches the checked-out file and its 94 CRLF lines are preserved. This closes the false dirty status for this maintainer's macOS clone. The verification remains maintainer-run and does not count as an independent reproduction. Full commands and results are in [`RESEARCHER_START.md`](RESEARCHER_START.md).

## October 25, 2026 — funding readiness is evidence of adoption

The current [CZI Science Funding directory](https://chanzuckerberg.com/science/science-funding/) lists EOSS Cycle 6 as closed and no later cycle. Its [Cycle 6 RFA](https://chanzuckerberg.com/rfa/essential-open-source-software-for-science/) is a 2023 call, not an open opportunity or a forecast of future terms. That RFA evaluated demonstrated scientific impact and adoption in biomedicine, project maturity and outside contributions; it said early-stage projects without broad use and tools with little biomedical adoption were less likely to succeed. It accepted organizations rather than individuals and described a fiscal-sponsor route.

**Talk2Nature implication:** treat this as a historical readiness benchmark only. The execution board still records zero independent reproductions, and no biomedical adoption or applicant organization/fiscal sponsor is established. Prioritize a documented outside research workflow, a useful independent reproduction, external contributions and evidence for any biomedical application before spending time on a future EOSS application. Recheck the next RFA from its official source; do not carry Cycle 6 dates, amounts or criteria forward as current terms. The source records and closed-call entry are in `content/sources.json` and `content/opportunities.json`.

## October 26 follow-up — keep pinned workflow actions maintainable

**Question:** can Talk2Nature keep its GitHub Actions pinned to immutable commits while reducing the chance that those pins silently go stale?

**Evidence:** the three current workflow files contain five `uses:` references, all pinned to 40-character commit SHAs; no `dependabot.yml` existed. The official OpenSSF Scorecard API endpoint for `github.com/Metivity/talk2nature` returned HTTP 404, so there is no current published Scorecard result to cite. Scorecard's own documentation says weekly API scans omit several checks and describes individual checks as heuristics; an aggregate badge would be a weak and potentially stale summary. GitHub documents `github-actions` as the Dependabot ecosystem and recommends schedules and grouping to control PR volume.

**Change:** added `.github/dependabot.yml` for monthly GitHub Actions version checks, grouped into a single update PR with at most one open PR. This preserves SHA pinning while creating a reviewable update path. It does not change Actions permissions, alter repository settings, enable security-update configuration, or publish a Scorecard result or badge.

**Limits and next decision:** the configuration is local to this candidate and has not yet run on GitHub; no result proves Dependabot recognized it or produced an update. After an authorized publication, verify the first configuration run and review any proposed SHA changes through the existing CI before merging. Do not report a Scorecard score until an actual current scan exists. Sources: [OpenSSF Scorecard README](https://github.com/ossf/scorecard/blob/main/README.md), [GitHub guide to action updates](https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/secure-your-dependencies/auto-update-actions), and [GitHub guidance on grouping update PRs](https://docs.github.com/en/code-security/tutorials/secure-your-dependencies/optimizing-pr-creation-version-updates).
