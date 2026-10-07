# Open-source health and adoption plan

**Reviewed:** October 8, 2026. This is a working project plan, not a claim of adoption or an external certification.

## What success means here

Success is a useful, trustworthy research tool that another person can understand, reproduce, correct and maintain. Stars, downloads and page views can describe reach, but they do not show that the tool solves a real workflow or supports sound science.

The plan follows GitHub's repository and community-health guidance, the Open Source Definition, CHAOSS project-health metrics and OpenSSF's security-practice guidance. These sources emphasize clear project purpose, recognized licenses, contribution and conduct paths, safe reporting, maintainable collaboration and contextual measures of responsiveness and sustainability. See [GitHub repository best practices](https://docs.github.com/en/repositories/creating-and-managing-repositories/best-practices-for-repositories), [GitHub community-health files](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file), the [Open Source Definition](https://opensource.org/osd), the [CHAOSS starter project-health model](https://www.chaoss.community/kb/metrics-model-starter-project-health/) and [OpenSSF Scorecard beginner checks](https://github.com/ossf/scorecard/blob/main/docs/beginner-checks.md).

## Current foundation

- **Purpose and boundaries:** the project describes a cited research library and local observation tools. It does not claim animal translation, a trained Talk2Nature model, public recording intake or a hosted research service.
- **Reuse:** original software is Apache-2.0 and original public summaries are CC BY 4.0. Third-party code, papers, recordings, datasets, weights and marks keep their separate rights. Contributions do not require copyright assignment.
- **Participation:** `CONTRIBUTING.md`, `SUPPORT.md`, `GOVERNANCE.md`, `CODE_OF_CONDUCT.md` and `SECURITY.md` route contributors and sensitive reports. Issue forms cover source corrections, research questions, software bugs, reproduction, mobile checks and audio-tool compatibility.
- **Quality and release:** public pull requests run Python and JavaScript suites plus the site checker with read-only workflow permissions. Actions are pinned to immutable commit references. The `main` branch now requires a pull request, the passing `checks` workflow and an up-to-date base; force-pushes and deletion are blocked, and the rule applies to administrators. Required approvals remain at zero until a second reviewer is available. Pages deployment is separate and manual; only the generated public `dist/` is uploaded.
- **Research integrity:** examples are synthetic, scientific summaries state their review depth and limits, citation metadata is present, and data admission remains closed until protocol, consent, rights and hosting gates are satisfied.

This release adds a pull-request checklist and issue-form contact links so a newcomer can find contribution, support, security and conduct guidance at the point they need it.

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

Raviv is the sole maintainer and sole recipient for private conduct and security reports. There is no independent appeal panel, response-time commitment, public data portal, archival DOI, independent scientific lead or external reproduction yet. The current policy states these limits rather than implying organizational capacity that does not exist. Improve the project by addressing a real gap with an accountable person and a tested procedure, not by adding empty committee titles or badges.
