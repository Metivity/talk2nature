# Talk2Nature goals

Established September 30, 2026. The public repository and website are launched. Raviv explicitly requested a new data, code and research collection goal on September 30; funding and the scientific pilot remain open.

## Completed milestone: deploy the website and build Field Notes around a database

Requested September 30, 2026. Deploy the updated public research library and an honest Field Notes product page using Metivity/talk2nature and the existing Pages origin. Verify the live build, research navigation, mobile layout and metadata.

Extend the private owner workbench with persisted study protocols, sessions and linked synthetic observations. Import the reviewed research/source/code/dataset catalogs into the private database with version fingerprints and idempotent synchronization. Define the eventual media-storage boundary and a phone-first observation workflow. Preserve the current authentication, consent, review and withdrawal rules.

Acceptance: successful public deployment and live checks; tested database persistence, evidence links and access controls; a browser-tested study/session/observation rehearsal; reproducible catalog import; current project documentation. Google policy acceptance, paid hosting, real participants, audio capture and playback remain separate unresolved gates, not claims made by this milestone.

Acceptance checks completed September 30: deployed public release `3870313`, verified 34 live files, imported 82 database catalog records idempotently, tested study/session/observation persistence and access with 31 backend tests, and completed a synthetic browser rehearsal including a 390-pixel layout. This bounded milestone is complete; live private access and participant collection remain future work.

## Completed goal: first data, code and research collection

Build a reproducible first collection of primary research, reusable code and suitable public datasets. Start with birds/parrots and the existing evidence library. Record exact sources/versions, review depth, labels, component-specific licenses, attribution, access and limitations. Rank resources by usefulness for predicting independently observed context on held-out individuals and sessions; keep identification benchmarks and plant/fungal sensing separate.

The first deliverable is a validated machine-readable resource catalog, a tested bounded acquisition tool, a small permitted sample with checksums and provenance, and a prioritized baseline/acquisition recommendation. Store third-party samples outside Git and website output. Do not execute downloaded research code or treat a catalog license declaration as proof of scientific suitability. Unresolved licenses remain blocked from acquisition.

This goal proceeds independently of Google Sign-In. It does not authorize paid storage/compute, new household recordings, Kiki imports without ownership confirmation, partner outreach, bulk article reproduction or a claimed animal translator. Detailed collection decisions and reproducible commands belong in `COLLECTION.md`.

Completion requires validated records, tests of acquisition limits and provenance, an inspected lawful sample (or a documented reason none qualifies), and updated continuity. Further collection and model training remain explicit next milestones.

First collection acceptance checks passed September 30: eight resource records, nine acquired files, aggregate annotation inspection, 23 repository tests and a checked local site build. This bounded goal is complete; the broader scientific program and private-product work are not.

## Pending work: private research product foundation

September 30 continuation: built and deployed the public Field Notes interactive demo using invented scenes, with browser-only choices and no research intake. Added and ran a private local database recovery rehearsal that strips active authentication state, verifies restored content and never replaces the running database. This is completed preparation within the existing project scope, not a completed hosted pilot. The next product milestone remains real owner sign-in and durable private hosting, followed by an approved invited study.

Create a mobile-product and AI architecture plan, a private owner workbench with Google Sign-In restricted to raviv@metivity.com, controlled contribution/review/release/withdrawal workflows, and a tested local vertical slice. Progress to a hosted pilot after the dedicated cloud project, real identity configuration and spending limit are resolved. Passive observation comes first. No real household recordings, automated animal playback or public recording intake before protocol and permissions are ready.

The detailed product gates are in `PHASE_TWO_PLAN.md`; server, identity and data controls are in `PRIVATE_ARCHITECTURE.md`. Local implementation lives in `admin/`, outside the static website. This work remains unfinished, with Google policy acceptance pending. A code-level auth implementation is not a verified live Google login.

October 1 continuation: the PostgreSQL adapter is implemented and the complete workbench flow is tested locally with a restricted database role. Hosted startup is guarded against missing identity and durable storage. `docs/HOSTING.md` contains the concrete provider/capacity/budget proposal. Google agreement acceptance and the paid-hosting decision remain pending; no private service is live. Completing this preparation does not complete the hosted-product milestone.

## Founding objective

Create a credible, useful center for understanding nonhuman communication, with an evidence library, reproducible research tools, a public website and a path to funded scientific work.

## Working identity

**Talk2Nature — Listen closely. Understand carefully.**

Mission: make the science of nonhuman communication understandable, testable and easier to build on.

The name is provisional. A preliminary web search found existing uses of Talk2Nature in outdoor recreation; this is not a trademark clearance or a domain-availability check. Avoid claiming exclusive ownership. Visual direction: forest green, warm paper, restrained yellow, expressive serif headlines and original signal illustrations. No third-party research logos or implied affiliations.

## Decision: an open foundation

Use Apache-2.0 for new original software and CC BY 4.0 for original public research summaries. Recordings, model weights, third-party articles and trademarks are not covered by those grants. A paid managed pilot or hosted workspace can fund continued work. No foundation/company incorporation decision is required to build the first release. Before grant-funded IP or commercial model integration, inspect the exact obligations and rights.

## First scientific direction

Focus on observed bird communication, with a parrot/Kiki feasibility study as a candidate once ownership, data access and a qualified scientific collaborator are confirmed. First question: can acoustic features improve prediction of a pre-defined observable context on genuinely held-out recordings, compared with context-only and background baselines?

The first code milestone validates recording metadata and constructs grouped evaluation splits. It does not decode animal language. Native-call studies and voluntarily learned interfaces are distinct research directions; choose one protocol before collecting training data. Trees and fungi remain in the evidence library, outside the first experiment.

## Milestones and acceptance

1. **Foundation:** project rules, scope, license boundaries, local repository, funding draft and a prioritized research backlog.
2. **Reviewable website:** home, evidence library, methods, roadmap, opportunities and contribution guidance; cited summaries with review depth and limitations; usable mobile navigation/search; original branding; accessible semantic HTML.
3. **Public launch:** confirmed GitHub owner and hosting account; repository published; exact tested build deployed; live routes/metadata/canonical URLs/sitemap checked; no private files in output. Custom domain only if supplied or explicitly purchased. Indexing is requested after ownership verification, not promised.
4. **Research foundation:** a tested metadata validator and deterministic split tool, synthetic demo, no false empirical performance claims. Select a properly licensed model and a real dataset only after rights/protocol review.
5. **Research library:** import the existing 48-source inventory; turn high-value sources into structured evidence notes; track full-text reviews separately from abstracts/documentation. No finite claim to have read all literature. Prioritize review by impact on the chosen experiment.
6. **Funding:** dated opportunity register; candidate/application matrix; factual applicant profile; eligible application drafts with budgets and evidence. Submit only accurate, eligible applications after applicant facts and required declarations are resolved. Log receipt/status. Do not submit a proposal to a completed-results prize.
7. **Pilot:** scientist-approved protocol and consent; baseline experiment; held-out evaluation; public results including negative results; a funded continuation or explicit pivot/stop decision.

## 90-day gates

- Days 1–14: 12 discovery conversations, three real workflows, one scientific lead, one feasible question and explicit data rights. These are targets, not completed work.
- Days 15–30: agreed codebook, independent labels, 30–50 reviewed examples and a private collection workflow.
- Days 31–60: collect only within approved scope; compare embeddings + a simple classifier against meaningful baselines; measure review time and uncertainty.
- Days 61–90: freeze evaluation, publish methods and limitations, decide on continuation. Collection counts are planning targets, not a power analysis.

## SEO and publication

Start with useful original pages about animal communication AI, bioacoustic models, animal-language evidence and open research methods. Each evidence note has a stable URL, clear title, concise description, sources and review date. Generate sitemap, canonical URLs, Open Graph and structured metadata. No fabricated author/reviewer credentials, scraped articles, keyword stuffing or guaranteed rankings. Search Console submission requires the actual site property and account.

## External dependencies

Confirmed: GitHub owner Metivity and GitHub Pages hosting, authorized September 30, 2026. Awaiting Raviv: funding applicant identity/country/entity; Kiki location and ownership; realistic budget/time commitment. These do not block local preparation. No external partner communication is authorized by the broad research goal alone.
