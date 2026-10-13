# Contributing

Start with an evidence correction, a reproducibility improvement or a scoped experiment. Include a primary-source URL, the claim being changed, what you actually reviewed and the study's limits. An abstract review must not be marked as a full-paper review. Organizations listed in the library are not project partners.

Do not submit raw private recordings, precise sensitive locations, personal applicant details or credentials. Recording contributions require documented ownership, consent and per-item license review. At this stage, submit metadata proposals rather than animal recordings.

Run the commands in `README.md` for relevant changes. Keep generated `dist/` output, funding drafts and temporary files out of Git. Changes to scientific claims need a source-based review; model accuracy needs an evaluation artifact and leakage audit.

Original code contributions are under Apache-2.0; original public summary contributions under CC BY 4.0. Do not contribute material you cannot license. Disclose substantive AI assistance and verify generated claims, sources and code.

## A useful first change

You do not need to upload a recording, train a model or have a GitHub account just to try the public tools. Pick one small task and report what actually happened; a useful failure is as valuable as a clean run.

1. **Try the phone workflow without a microphone.** Open the [Field Companion](https://metivity.github.io/talk2nature/app/), choose “Try without a microphone,” add a marker, stop, and inspect the recap. Use the [good first phone task](https://github.com/Metivity/talk2nature/issues/115) to share whether you finished and what was unclear; trying the app needs no account, but posting publicly requires GitHub sign-in. The task offers email as an alternative. If you find a reproducible software bug, use the [mobile-check form](https://github.com/Metivity/talk2nature/issues/new?template=mobile-check.yml). Do not grant microphone permission, attach recordings or share sensitive details for this check.
2. **Try the research workflow.** Start with the no-setup [browser comparison](https://metivity.github.io/talk2nature/app/compare/); no code, account, recording or upload is needed. If you want to check the software kit, follow [Researcher start](docs/RESEARCHER_START.md) from a clean checkout. Use the [workflow report form](https://github.com/Metivity/talk2nature/issues/new?template=reproduction.yml) to describe what you tried, the page or code version, your device/browser if known, and what happened. “Unknown” is an acceptable environment detail. The form defaults to “Not sure / not independently verified”; select an evaluator relationship only when accurate. An outside walkthrough is not automatically a software reproduction: only a maintainer-reviewed run of the documented software commands counts toward independent reproduction. Redact local paths.
3. **Check one research claim.** Choose a library note, follow its primary-source link, and report the specific claim, source section or timestamp, what you reviewed, and any limitation or correction in the [source-review form](https://github.com/Metivity/talk2nature/issues/new?template=research-source.yml). Link to the original; do not paste article text or submit raw media.
4. **Review a scientific method.** For the bounded Egyptian fruit-bat context-prediction question, read the [focused methods brief](docs/BAT_CONTEXT_REVIEW.md) and use the [scientific review form](https://github.com/Metivity/talk2nature/issues/new?template=scientific-review.yml). You can review only the parts within your expertise; state what you actually inspected and what remains unavailable. This is not a request to reproduce the model or share data.

A repository test checks that these four links still point to the expected GitHub forms and that each local issue-form file exists. It also protects the workflow form's unverified default and its plain-language browser path. These checks do not verify GitHub's hosted form rendering or independent usability.

Search existing issues before opening a new report. For a bug, include the page, device/browser, steps, expected and actual behavior. A redacted screenshot can help. If GitHub is unfamiliar, use the site's [draft helper](https://metivity.github.io/talk2nature/contribute/source/) or contact route; drafting there does not post anything until you choose the GitHub link.

A pull request should explain the user problem, resulting behavior and checks run. Include a regression check for a data-loss or correctness fix. Website changes need local build/link checks and meaningful narrow-screen interaction testing. Public checks run on pull requests with read-only permissions; publishing remains a separate manual action. Passing CI does not authorize deployment or establish a scientific result.

For help choosing an evaluation or report route, read [SUPPORT.md](SUPPORT.md). University groups can use the [bounded synthetic evaluation brief](docs/UNIVERSITY_EVALUATION.md); it is not a request for research data or a claim of partnership.

Read [governance](GOVERNANCE.md), [community conduct](CODE_OF_CONDUCT.md) and [security reporting](SECURITY.md). Code and summary contributions retain their stated licenses; no contributor license assignment is requested. A substantive AI-generated contribution must be disclosed and its sources and behavior checked by its contributor.
