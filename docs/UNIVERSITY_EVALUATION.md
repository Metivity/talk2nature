# University evaluation brief

Updated October 6, 2026. This is an invitation to evaluate an early research-software workflow. It is not a partnership announcement, study protocol, animal-communication claim or request for recordings.

## The right first ask

Talk2Nature is ready for a small **software and workflow evaluation with synthetic material**. A researcher, research-software engineer, librarian or student working with a supervisor can spend about 20 minutes asking whether one narrow workflow is understandable and useful:

1. Use the invented two-tone example in the browser-based Listen tool and mark two timed events.
2. Export the local package and import its WAV and timed labels in Audacity, if Audacity is already part of the evaluator's workflow.
3. Check whether the time spans and note text survive, compare the source checksums, and identify one confusing step, missing field or failed conversion.
4. Report the tested revision and software versions, how much help was needed, what happened, and whether this is a workflow the group would use.

The [researcher starter kit](RESEARCHER_START.md) provides the broader browser and Python evaluation routes. The [Sound Handoff Lab](https://metivity.github.io/talk2nature/tools/interop/) provides the focused export walkthrough. The evaluation requires no account, microphone, animal recording, model download, data upload or study data. The current native import check covers Audacity 4.0.1 on macOS arm64 only; it is not a claim of cross-platform conformance.

The question is deliberately modest: **does this help a researcher preserve and inspect an observation record, and what does it fail to represent?** It does not test whether a call has a meaning, identify an animal, measure a model, or demonstrate conversation with wildlife.

## Who can help now

| Role | Useful contribution now | Boundary |
| --- | --- | --- |
| Bioacoustics or animal-behavior researcher | Review the observation fields, uncertainty language and fit against one documented workflow | No claim of scientific validation; no upload of lab recordings or private records |
| Research-software engineer or digital-research librarian | Try the reproducible instructions, audit metadata and export loss, advise on citation and release practice | No promise of a maintained integration until its user and target format are identified |
| Accessibility or field-methods specialist | Test the browser steps on a real device and report barriers or missing field context | Physical-device validation is not yet complete |
| Student or class | Complete a bounded, supervised evaluation or a well-scoped issue with a learning objective | Do not treat students as unpaid substitute maintainers; agree supervision and appropriate credit before work starts |

An independent evaluator can report a failure without endorsing the project. Public issue reports must contain only information suitable for public release; keep private institutional information out of them. No lab, university or contributor will be named as a partner or quoted without permission.

## Plausible first conversations

These are **evidence-based fit hypotheses**, not known prospects, partners or endorsements. Verify current interests and ask permission before describing any conversation publicly.

- **Tel Aviv University, Bat Lab for Neuro-Ecology / Steinhardt Museum:** the university describes work on animal behavior, vocal communication, acoustics and signal processing, including ultrasonic microphone arrays synchronized with high-speed video. That makes the group a plausible source of advice on context and multimodal provenance. Talk2Nature has not validated ultrasonic WAV handling or audio-video synchronization, so the first ask should be a requirements review with synthetic material, not a claim that the current tool is ready for bat data.
- **Bar-Ilan University, Lee Koren's research group:** its public profile describes individually marked wildlife datasets combining behavior, vocalizations and proximity, and research questions about vocal communication. This suggests a useful methodological conversation about what context and uncertainty must accompany an annotation. No group data should be shared; the project does not currently admit real observations.
- **A university research-software, library or open-science team:** ask for a short reproducibility and stewardship review of the public code, contributor path, citation metadata and future archival release. This is different from recruiting a bioacoustics lab to adopt the tool.
- **Established bioacoustic software communities:** learn from the documented tools and formats they already use. Prefer one tested adapter or an upstream contribution over proposing another platform without demonstrated need.

Talk2Nature is still a single-maintainer initiative. It currently has contribution, governance, conduct and security policies, CI checks, a citation file, issue forms and synthetic evaluation instructions. It does not yet have an independent scientific reviewer, independent conduct appeal route, co-maintainer or succession plan, stable archival DOI, institutional research agreement or approved participant-data workflow. Those gaps are why the first request is a bounded software review, not a public dataset project.

## Reusable first email

Personalize the bracketed phrase with a specific public paper, workflow or tool after reading it. Write to one relevant person at a time; do not use a mass mailing or imply an existing connection.

> **Subject:** Could you review one small bioacoustic workflow?
>
> Hello [Name],
>
> I’m Raviv Yatom, founder and maintainer of Talk2Nature, an early independent project documenting animal-communication research and building local-first observation tools. I noticed your group's work on [specific public method or paper], especially [one concrete point relevant to annotation, acoustic context or research software].
>
> Would you or a research-software colleague be willing to try a short synthetic Listen-to-Audacity workflow and tell me one thing it preserves, one thing it misses, and whether this solves a task you actually have? The [evaluation kit](https://github.com/Metivity/talk2nature/blob/main/docs/UNIVERSITY_EVALUATION.md) uses invented material; no recordings or study data are requested. Talk2Nature does not currently translate animal communication or accept research recordings. I’m asking for independent feedback, not an endorsement, partnership or commitment.
>
> If useful, I’d be glad to arrange a 20-minute walkthrough. If it is not a fit, no reply is needed. I will not name or quote your group without permission.
>
> Thank you,
> Raviv

Send one tailored note, optionally one polite follow-up after 7–10 working days, then stop. If the question is about real animal data, human participants, field experiments, playback, sensitive locations, funding or data agreements, first ask the appropriate university scientific and ethics offices; this software evaluation is not an ethics determination. Do not start collection or playback as part of this invitation.

Keep prospective-contact notes private in the ignored `funding/` workspace. Record only the public basis for fit, date and status; do not copy private replies into GitHub or the website without consent. The project has no response or meeting capacity guarantee.

## What makes the pilot useful

Use the existing [execution board](EXECUTION_BOARD.md), not views or stars, to count success. The first useful result is one independent person completing or failing the exact task with a revision and environment recorded. Then ask:

- Which job were they trying to do, and what do they use now?
- Which context or provenance field was missing or ambiguous?
- Did the exported artifact open in their normal workflow, and what information was lost?
- Would they reuse it for this specific task? What evidence supports that answer?
- What should remain local, restricted or uncollected?

Summarize the result and any correction back to contributors. Credit substantive work; get permission before naming an evaluator. If a repeated user need appears, invite that user to shape a scoped issue or adapter. Expand roles and repository access only after demonstrated collaboration and an explicit scope. Add a new forum or mailing list only when someone can moderate and answer it; the current single maintainer should not promise channels it cannot support.

## Before a real research pilot

Software feedback with synthetic examples and research involving people, communities, or animals are different activities. Before any empirical collection or public data release, a university lead and relevant institutional offices must agree on the research question, protocol, animal-welfare boundaries, any human-participant/ethics review, consent and withdrawal, data rights, sensitive-location treatment, security, retention/deletion, independent labeling, evaluation design, authorship and benefit-sharing. The appropriate institution determines which reviews apply. Public code licenses do not supply these approvals. The private server's synthetic-only gate and the public tools' no-upload design remain in force.

## Sources checked

- [GitHub: community health files and support resources](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file), checked October 6, 2026.
- [Software Sustainability Institute: starting a community](https://www.software.ac.uk/guide/starting-community-taking-your-software-world) and [manager guides](https://www.software.ac.uk/guide/guides-managers), checked October 6, 2026. The guidance recommends starting with the audience one step removed, involving users in requirements and tests, and growing communication in line with capacity.
- [Ithaka S+R: sustaining open source software in the research enterprise](https://sr.ithaka.org/publications/sustaining-open-source-software-in-the-research-enterprise/), including its May 2026 practical guide, checked October 6, 2026. It highlights leadership succession, user/developer/institution representation, communication work and the risks of a single-person decision bottleneck.
- [European Citizen Science Association: Ten Principles](https://www.ecsa.ngo/10-principles/), checked October 6, 2026. The principles emphasize meaningful roles, a genuine scientific outcome, participant benefit and feedback, evaluation and ethics; they are a useful gate before inviting the public to contribute observations.
- [Tel Aviv University: Yossi Yovel](https://english.tau.ac.il/profile/yossiy) and [Bar-Ilan University: Lee Koren](https://dsai.biu.ac.il/team/prof-lee-koren/), checked October 6, 2026. Profiles support the potential topical fit above; they do not demonstrate interest in Talk2Nature.
- [BirdNET's tools and collaboration](https://birdnet.cornell.edu/tools/), checked October 6, 2026. It illustrates an existing research-software ecosystem to learn from and complement, not a project affiliation.
