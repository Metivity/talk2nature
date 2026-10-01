# Talk2Nature success and international growth plan

Prepared October 1, 2026 for Raviv. Active initiative: Talk2Nature; repository: Metivity/talk2nature. This is a proposed operating plan, not a public launch announcement, partnership claim or authorization to spend beyond the existing hosting budget. No outreach has been sent.

Talk2Nature should earn international attention by producing a useful contribution that other people can test and reuse. The recommended first contribution is a reliable workflow for connecting bird vocalizations with independently observed behavior. Build a small scientific collaboration and a repeatable participant experience around that contribution, then use the resulting methods, tools and findings to grow internationally.

Worldwide recognition is a longer ambition. The next 90 days should establish evidence of scientific usefulness, repeated use and an audience that returns. Dates below assume a scientific lead and operational hosting can be secured in October. Research gates take precedence over launch dates.

## Where the project stands

The public website, research library, open repository and synthetic Field Notes demo are live. The private workbench contains 82 public catalog records. Local Google owner login, logout, identity pinning and denial of another account were verified. Subsequent Listen and Nature Station releases are recorded in STATUS.md; these establish software progress, not animal-communication results.

October 1 product update: Raviv requested a more ambitious station and encounter-learning direction. [Nature Station](NATURE_STATION.md) implements a bounded local browser prototype and defines the native-device and learning sequence. Use its synthetic encounter walkthrough for the next demonstration; retain the scientific lead, pilot and external-validation gates below. An installed browser prototype is not an operational worldwide sensor network.

The unfinished essentials are hosted operations and recovery, a committed scientific lead, a selected species and protocol, lawful real data, participant access and capture, external users, an empirical evaluation, and a confirmed funding applicant. Google billing completion and the separate Supabase agreement are pending. Details remain in the private setup record; see [current status](STATUS.md) and [hosting](HOSTING.md).

## The first audience and product

Start with one avian research or care team that already records behavior and struggles to produce consistent, reviewable observations. This team is the first prospective customer and study organizer. Invited adult bird carers or observers are contributors. Curious readers are the public audience. Each needs a different invitation and success measure.

Parrots are the leading candidate because of Raviv's interest and possible Kiki experience. Choose the actual species through access, scientific value, observable behavior and achievable independent sampling. Kiki's ownership and data rights must be established before any reuse. If a suitable parrot study cannot be arranged, select a partner-led question with lawful existing data or publish a methods/tooling study.

The first product is **Field Notes**: a phone-friendly observation journal and a researcher's review workspace. Immediate value comes from useful session history, clear observation instructions, quality feedback and exportable evidence. A contribution should give its author something useful even before a model is trained.

Current competition makes specificity essential. Cornell's September 9, 2026 BirdNET Live announcement describes offline smartphone identification, recording, review/export and survey modes. Earth Species Project already offers audio models, data access and annotation tools. Our proposed advantage is reducing the effort of producing permissioned, behavior-linked evidence across individuals. That is an untested product hypothesis; interviews and comparison with existing workflows must establish it. [Cornell announcement](https://www.birds.cornell.edu/home/birdnet-live-app-ai-powered-wildlife-identification/), [ESP tools](https://earthspecies.org/what-we-do/).

## People and decisions required

| Responsibility | Proposed owner | Concrete commitment needed |
| --- | --- | --- |
| Product, relationships and funding | Raviv | Reserve approximately six hours weekly for interviews, decisions and follow-up; adjust scope if less is available |
| Scientific question and welfare | Avian behavior or bioacoustics lead, not yet recruited | Review the protocol and labels, define permitted claims, and join a regular study review |
| Evaluation and reproducibility | ML or statistics collaborator, not yet recruited | Audit splits, confounds, baselines and uncertainty before seeing final results |
| Implementation and documentation | Raviv with coding assistance | Maintain tested software, traceable data versions and readable documentation |
| Contributor support and editorial review | Raviv initially; later a named coordinator | Resolve participant problems, review releases and maintain a sustainable publication cadence |

A small team can cover several roles. AI assistance does not supply scientific accountability, animal access, independent review or partner commitment. Budget for those capabilities or obtain explicit in-kind contributions. Do not list advisers until they agree to the role and public attribution.

Keep the current open foundation: Apache-2.0 original code and CC BY 4.0 original summaries. Check data and model rights separately. Test managed study hosting, onboarding and analysis support as a revenue hypothesis with research teams and sanctuaries. Decide the legal operator and grant applicant before contracts, paid pilots or applications. GitHub account ownership does not establish the applicant entity. A future nonprofit arrangement is a separate governance decision.

## The next 90 days

| Period | Deliverables | Gate to advance |
| --- | --- | --- |
| October 1 to 14 | Resolve hosting setup; complete hosted recovery/security checks; conduct 12 discovery conversations; select one species and question; secure a scientific lead; decide Tnufa readiness; draft public positioning and participation paths | One committed scientific lead, one prospective pilot organizer and a written protocol outline. If these are missing, continue discovery and lawful dataset review |
| October 15 to 31 | Finalize codebook, permissions and review rules; test annotation feasibility; add study-scoped contributor access; prepare short foreground recording and discard/review controls; test real devices and deletion | Scientist approves scope; participant isolation, withdrawal, storage quotas and recovery pass; independent labels are feasible. Until then, use synthetic examples |
| November | Invite up to 20 adults into a bounded feasibility pilot; measure repeated use and data quality; audit an initial 30 to 50 labeled events; choose independent sampling units; freeze analysis plan before final evaluation | Enough independent animals and sessions for the chosen claim, acceptable label agreement and manageable review effort. Clip count alone does not satisfy this gate |
| December | Run a licensed encoder plus simple baselines if data is admitted; publish protocol, tools and a limitations report; obtain an external reproduction or review; release only rights-cleared artifacts; test demand for a paid managed pilot | A reproducible result or a useful documented failure, plus evidence of repeated use. If empirical gates fail, publish the methods and feasibility outcome and narrow the next study |

The proposed scientific question is: **does vocalization audio improve prediction of one independently observed context on animals and sessions not used for training?** Choose an observable target with the scientific lead. A feeding observation does not establish that a call means “I am hungry.”

Labels must come from observation independent of model output. Compare majority, context-only, background-only, acoustic-only and combined baselines. Separate animals, households, sessions and relevant devices; check duplicates and possible model-pretraining overlap. Double-label a prespecified subset and retain disagreements. Set metrics, meaningful improvement and uncertainty criteria with the lead before evaluation. See [the existing experiment design](PHASE_TWO_PLAN.md) and [model decisions](MODEL_DATA_DECISION.md).

Reuse a suitable licensed audio encoder first. Sequence modeling and audio/video/context alignment are later experiments once the simpler evaluation exposes a specific limitation. An LLM can explain cited research or summarize reviewed observations. Generating a fluent English interpretation does not establish animal meaning. Controlled interaction requires separate scientific and welfare review; automated playback remains disabled.

## Product sequence

1. Complete the hosted owner workbench with durable storage, restart tests, restricted access, operational alerts and a recovery drill that reconciles later withdrawals.
2. Build participant invitations and study-scoped authorization separately from owner access. Every request must enforce membership; a participant must not inherit the owner's workspace or another household's records.
3. Add a short, participant-started mobile session with visible recording state, stop/discard, context annotation, review before upload and an explicit unknown label. Add bounded media storage, interruption tests and deletion across active records and retained copies before admitting real recordings.
4. Add a useful observation history, contribution status and correction feedback. Prioritize lower effort per usable observation and reviewer time over upload volume.
5. Evaluate a dedicated phone listening station only after this workflow works. Native background capture, television interfaces, plants and fungi remain separate later tracks.

The approved US$50/month hosting envelope covers the metadata prototype proposal. It is not an approved audio-storage, GPU, staffing or marketing budget. Measure costs and set quotas before media intake; propose a separate budget when usage requires it.

## Positioning and website changes

Keep **Talk2Nature — Listen closely. Understand carefully.** as the working identity. Before significant publicity spending, check name conflicts and domain options, then make one brand decision. No trademark clearance or domain purchase is claimed.

Suggested public introduction:

> Talk2Nature is building open tools to help people and scientists study animal communication. We are starting with birds: connecting sounds, observable behavior and reproducible evidence.

The website should guide visitors into three paths: explore the research, try the clearly marked synthetic demo, and express interest as a researcher or future pilot participant. Build and test the private interest workflow before displaying a working sign-up promise. A newsletter subscription is separate from study consent; no recording upload belongs in a public GitHub issue.

Add a concise progress page, research protocol page, founder biography, honest team status, correction process and downloadable media kit. Every claim should be labeled as established research, a Talk2Nature result, or proposed work. Shareable cards can explain a finding and its uncertainty, with links to original sources; use only owned or licensed images and media.

Start in English for international reach and Hebrew for founder relationships. Add another language only when there is sustained demand and someone qualified to review the translation and support contributors. Scientific labels should preserve stable meanings across translations.

## How international awareness should grow

Use three distinct releases with a concrete reason to pay attention.

| Release | Story and artifact | Distribution | Success signal |
| --- | --- | --- | --- |
| October public introduction | Founder motivation, existing demo, evidence library and a specific collaboration question | Raviv's professional network, invited science conversations, short original video and relevant communities after moderator approval | Qualified conversations and useful criticism |
| November pilot invitation | A scientist-reviewed protocol and a useful observation workflow, after collection gates pass | Pilot organizer, adult bird-care communities and a small number of relevant educators or creators | Activated contributors who return and supply usable observations |
| December methods release | Reproducible code, permitted data or aggregates, evaluation and limitations; negative results are valid | Research groups, GitHub, a technical demo post, specialist media and podcast pitches approved by Raviv | Independent use, reproduction, citations and new study requests |

International expansion follows a repeatable local pilot. Recruit a second organizer in another country, adapt permissions and instructions, and compare data quality before enlarging intake. An eventual coordinated “Listen and Observe Week” can connect partner groups around a standardized passive observation task. Public participation must fit the approved protocol; sharing a personal recording is always a separate decision.

Concentrate on a few channels:

- **Research relationships:** make a specific request about a protocol or workflow problem. Offer a usable tool, documented analysis or careful review. A concrete contribution provides a reason for an introduction.
- **GitHub:** maintain a short setup path, synthetic example, contribution guide, versioned releases and a few useful starter tasks. Credit real contributors. Seek independent reproduction before organizing a large hackathon.
- **Founder communication:** publish one substantial, reviewed piece every two weeks; derive one short video and two short posts from it. Use LinkedIn and one video channel initially. Each item should lead to a relevant demo, evidence note or participation path.
- **Search:** improve the existing best pages before adding volume. Explain specific questions, show sources and review dates, connect related notes, and make titles understandable. Diagnose the unresolved sitemap processing status in Search Console. Google recommends useful, reliable content made for people; rankings and indexing are outcomes to measure, not guarantees. [Google guidance](https://developers.google.com/search/docs/fundamentals/creating-helpful-content).
- **Press:** prepare a founder story and media kit now. Pitch broader scientific claims only with a reviewable result and the scientist's agreement. The podcast that inspired Raviv is a relevant future pitch, not an existing relationship or endorsement.

Six proposed editorial pieces are: what animal translation would require; identification versus observed context; how to annotate without guessing; why recordings from one animal are not independent subjects; a transparent comparison of existing tools; and the pilot's actual results and limitations. Original examples and useful methods should make these worth citing.

A manageable weekly rhythm is a short product review, two targeted conversations, one data-quality or literature-review session and one public progress update when there is meaningful news. Hold a monthly open methods session once someone can moderate it. This plan does not create a schedule or authorize sending messages.

## First collaboration prospects

These are researched prospects, not confirmed partners. All proposed outreach needs Raviv's authorization.

| Prospect | Why approach | First concrete request |
| --- | --- | --- |
| [Yossi Yovel and the TAU lab](https://en-sagol.tau.ac.il/researchers/Yossi-Yovel) | Animal behavior, sensing and computational methods; connected to the originating topic | A short critique of the proposed question and a referral to an appropriate study lead |
| [Lee Koren's lab](https://leekoren.wixsite.com/korenlab) | Behavioral ecology and natural observation; connected to the originating podcast | Advice on meaningful observable labels and the limits of claims about communication |
| [Earth Species Project](https://earthspecies.org/what-we-do/) | Existing audio models, datasets and annotation tools | Assess a specific interoperability or evaluation contribution after we have a protocol |
| [BirdNET team](https://birdnet.cornell.edu/contribute/) | Their contribution page invites annotated data, expertise and relevant research collaboration | Review a concrete export/annotation gap; explore contribution rather than duplicating their recording stack |
| [Project CETI](https://www.projectceti.org/research/index) | Interdisciplinary work linking communication with field context | Seek feedback on a documented method once we have something useful to share; keep whales outside the first pilot |
| One avian research, care or sanctuary team | Could provide the first real workflow and responsibly supervised access | Observe their current process and test whether Field Notes saves review effort; identify the organization during discovery |

Suggested first message, for later approval and personalization:

> I am building Talk2Nature, an early-stage open project connecting animal recordings with independently observed behavior. We have a synthetic workflow demo and are looking for one scientifically useful first question. Would you be willing to critique a one-page protocol or suggest someone appropriate? We can share the demo, metadata format and current limitations in advance.

## Funding and commercial validation

**Immediate decision by October 3:** determine whether an accurate, complete Tnufa application is feasible for the next deadline. The official page currently lists **October 8, 2026**, up to **NIS 200,000**, covering up to **80%** of approved costs. Eligibility, matching resources, novelty and obligations require applicant-specific review. We still need applicant identity, the technical research case and current application documents. A website and routine integration alone do not establish the required innovation. If the case is weak or incomplete, prepare properly for a later verified opportunity. [Tnufa program](https://innovationisrael.org.il/programs/מסלול-תנופה-קרן-ההזנק/).

**Future scientific recognition:** the Coller Dolittle page gives September 30, 2026 at noon CET as the deadline for its 2027 challenge. As of this plan it has passed, despite the page retaining an “open” heading. The US$100,000 annual prize requires work already performed and measurable receiver responses. Our passive feasibility study is an earlier milestone. Recheck a future call when there is qualifying research; do not make a prize win the operating budget. [Official rules](https://coller-dolittle-24.sites.tau.ac.il/).

**Nearer practical funding:** test a sponsored feasibility study, a university-supported collaboration or a paid managed pilot after discovery establishes value. A sponsor would fund a defined protocol, audited dataset and analysis report, with publication and data rights agreed. No funding or customer demand is secured.

An illustrative fundraising target is **US$15,000 for a 90-day feasibility phase**, assuming founder development is contributed in kind. This is a planning envelope, not supplier quotations or spending approval: US$6,000 scientific design/annotation, US$4,000 ML/statistical review, US$2,000 coordination and equipment, US$1,000 privacy/contract review, US$500 operations and US$1,500 contingency. Obtain quotes and map eligible costs before using any grant budget. Include researcher and founder time in the eventual full economic cost.

Test willingness to pay through five conversations with prospective study organizers. Ask what they use now, the cost of manual review, who controls the budget, and what measured improvement would justify a paid pilot. A possible continuation criterion is a 25% reduction in review time without lower quality, defined before comparison. It is a proposed test, not a current result or a market-established threshold.

## Measures and decisions

The primary measure is how many external teams can use or reproduce Talk2Nature's work. Website traffic supports that goal when visitors become informed contributors, collaborators or customers.

All counts below are planning targets, not forecasts or evidence that a scientific sample is adequate.

| Measure | By day 30 | By day 90 |
| --- | --- | --- |
| Discovery and scientific commitment | 12 completed conversations; one committed scientific lead; one prospective organizer | Two teams actively using or evaluating the workflow |
| Participation after collection approval | Cohort readiness assessed | Up to 20 invited adults; aim for at least 10 completing a usable session in each of two consecutive weeks |
| Research output | Protocol, label-feasibility findings and analysis plan | One reproducible baseline report if data passes admission; otherwise a transparent feasibility report |
| Independent contribution | Three actionable external reviews | One independently reproduced result or tool workflow and three external contributions |
| Audience | Measure initial demo use and qualified inquiries | 200 opted-in readers across at least three countries, with acquisition sources and conversion measured |
| Commercial evidence | Five organizer interviews planned or completed | One written willingness to fund a defined next pilot, or a documented explanation of why demand is insufficient |

Track retention by cohort, usable contribution rate, reviewer minutes per accepted observation, unresolved privacy/rights issues, cost per usable observation and external reuse. Define an activated contributor as someone who completes onboarding and one accepted session under the approved protocol. Keep traffic and email measurement consistent with the privacy disclosure; no analytics or mailing service is silently enabled by this plan.

A conditional 12-month ambition is five active studies or independent tool users across three countries, two independently reviewed research releases and one sustainable funding route. Scale audience spending only after the pilot is useful and support capacity exists. If no scientific lead commits by day 30, keep collection closed. If engagement or label quality is poor, simplify the workflow and question. If model performance depends on backgrounds or known animals, report that limitation and revise the study.

## The next seven days

1. Raviv resolves the pending hosting account steps, confirms founder availability and identifies the funding applicant.
2. Prepare a one-page scientific concept and a short demo video using the synthetic example.
3. Prepare five personalized collaboration drafts and an interview script; Raviv chooses recipients and authorizes sending.
4. Decide Tnufa readiness by October 3 using verified facts and current forms.
5. Compare the proposed workflow with the first organizer's existing tools; choose one measurable improvement.
6. Specify the next website change: clear positioning, three participation paths and a working, private interest process. Review name/domain options before spending on publicity.
7. Establish a small weekly scorecard and an October decision review. Revisit this plan after the first six conversations.

This document was prepared from the existing project records and the linked primary program, tool and institutional pages checked October 1, 2026. It is a targeted strategy review, not an exhaustive literature survey. The plan was initially saved locally. The October 1 implementation is tracked in `EXECUTION_BOARD.md`; this planning document is repository documentation, not a claim that its targets have been achieved. It has not been sent to prospects.
