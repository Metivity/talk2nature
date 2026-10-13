# Digital Public Goods readiness review

Reviewed October 13, 2026 against the Digital Public Goods Alliance's currently published Standard page and application FAQ. This is an evidence-based maintainer self-assessment, not an eligibility-tool result, application, recognition or legal certification. The live Standard page lists nine indicators, with the ninth split into 9A, 9B and 9C. The page does not state a version number, so this review records the exact page and access date rather than inferring one.

## Candidate scope

If the project later pursues the DPGA process, assess one component first: the public Field Companion and its open-source software repository. Do not submit “Talk2Nature” as an undifferentiated bundle. The private owner workbench, public evidence/content collection, third-party datasets, and any future AI model have different access, ownership, license, privacy and readiness conditions. The private backend is not a public research service; real-data intake is closed, and AutoResearch remains **NOT READY**.

The DPGA says its review focuses on a solution's core design, not local implementations. Its FAQ describes a two-reviewer assessment and annual validity. Registry inclusion can improve discovery among governments, NGOs and other stakeholders, but it is not evidence of deployment, scientific validity, a UN endorsement, funding eligibility or user adoption.

## Indicator-by-indicator evidence

| Indicator | Current evidence for the public software candidate | Assessment and next evidence |
| --- | --- | --- |
| 1. SDG relevance | The tool supports careful observation and open research documentation. UN SDG 15.5 on biodiversity and SDG 4.7 on education for sustainable development are plausible connections. | **Not demonstrated yet.** These are potential pathways, not measured outcomes. Select the most relevant target, explain the product-to-target mechanism and define a credible outcome before claiming contribution. Do not claim SDG impact from page views, recordings or model scores. |
| 2. Open licensing | Root `LICENSE` is Apache-2.0 for original software. `NOTICE`, `GOVERNANCE.md` and `docs/OPEN_SOURCE.md` distinguish original summaries (CC BY 4.0) from third-party works. | **Strong for the scoped software; verify the release inventory.** Confirm every bundled asset and dependency in the nominated release, and do not fold datasets or noncommercial model weights into this claim. |
| 3. Clear ownership | `GOVERNANCE.md`, `CONTRIBUTING.md`, `NOTICE` and `docs/OPEN_SOURCE.md` identify the founder/maintainer, contributor copyright and artifact licenses. | **Partly documented.** The public project has no confirmed separate legal entity; the working name is not trademark-cleared. Define ownership and permitted use for user-created exports and any future service before accepting real research data. |
| 4. Platform independence | The public app is built as static web output using the standard-library Python builder and browser APIs. The source can be built separately from GitHub Pages; no hosted model or private account is required for the public workflow. | **Promising; portability evidence is incomplete.** Rebuild and serve the same release on a second compatible static host, and list required browser capabilities and graceful fallbacks. Treat the experimental Android source and private admin service as separate components. |
| 5. Documentation | README quickstart, architecture and scope notes, `docs/RESEARCHER_START.md`, user-facing guides, contribution workflow, tests and synthetic examples support setup and review. | **Strong for the present software scope.** Keep the clean-checkout reproduction instructions synchronized with each release and test them from a clean source archive or clone. |
| 6. Non-PII data extraction | The app exports user-controlled ZIP, JSON, CSV and WAV artifacts; journal-only JSON and documented annotation interchange are available. It does not send recordings to a Talk2Nature server. | **Good export mechanism, with a privacy boundary.** Audio, voices, free-text notes and precise locations can still identify people or sensitive wildlife. Document which outputs may contain sensitive information; do not call an export non-PII without examining its fields and context. |
| 7. Privacy and applicable laws | The public About & privacy page describes local processing, microphone use, exports, GitHub Pages request data and the optional YouTube connection. The project has no public account or research-upload service. | **Legal compliance is not established.** No jurisdiction-by-jurisdiction legal review or compliance certification is recorded. Before a hosted service, participant intake or wider deployment, identify the operator, data roles, locations, purposes, retention, rights and applicable laws with qualified counsel. |
| 8. Standards and best practices | The repository uses documented JSON/CSV/WAV formats, source-linked records, testable schemas, accessibility checks and explicit research limits. `docs/DATA_INTEROPERABILITY.md` records that no Darwin Core conformance is claimed. | **Partly demonstrated.** Publish a concise standards map for the nominated release, name validators and unresolved interoperability work, and keep “compatible with” distinct from formal conformance. |
| 9A. Data privacy and security | Data minimization is strong in the public app: no account, upload or server-side recording store; recording is user-started and local. `SECURITY.md` supplies a private report route. The owner backend remains synthetic-only. | **Risk is reduced, not independently assessed.** No external security review or hosted threat model is recorded. Before enabling real accounts or data, review access control, backups, deletion/withdrawal, incident handling and recovery against the exact deployed architecture. |
| 9B. Inappropriate and illegal content | The project does not offer public recording uploads or a social feed; contribution guidance prohibits private recordings, sensitive locations and personal information. | **Limited exposure by design; process still needed for accidental or future submissions.** Document triage, removal, reporting and retention for material posted through project-controlled channels before accepting user content. |
| 9C. Protection from harassment | `CODE_OF_CONDUCT.md` covers project-managed discussions and describes a private report route and possible responses. The app itself has no user-to-user messaging. | **Partly documented.** The founder is the sole maintainer and report recipient, so there is no independent appeal route; underage-user safeguards are not fully specified. Define an escalation and child-safety plan before scaling public interaction or inviting minors. |

## Decision and sequence

Do not nominate the current project yet. The decisive gaps are a defensible SDG contribution statement, a precise public component/release boundary, evidence for privacy and applicable-law claims, and complete 9B/9C procedures. A software-only nomination would not certify the research library, private database, datasets or future model.

1. Keep the candidate limited to the public Field Companion and its source release; make an artifact/asset inventory for that exact release.
2. Ask the owner to choose a specific SDG target and a measurable contribution pathway. Until then, describe SDG relevance as a hypothesis.
3. Obtain qualified privacy/legal and security review before changing the current no-upload, no-real-data boundary.
4. Close content-handling, maintainer-conflict and underage-user procedures without inventing an independent reviewer or team member.
5. Test a clean build on an alternate static host and publish a concise standards-and-accessibility evidence map.
6. Only after these checks, use the DPGA eligibility tool and decide whether to prepare a nomination. The FAQ says applications are reviewed by two people; no application or contact was made for this review.

## Official sources

- [DPGA Digital Public Goods Standard](https://www.digitalpublicgoods.net/standard) — current published indicators, scope and standard license; reviewed October 13, 2026.
- [DPGA application FAQ](https://www.digitalpublicgoods.net/digital-public-goods/faqs) — review process, registry discovery and annual validity; reviewed October 13, 2026.
- [UN SDG 15](https://sdgs.un.org/goals/goal15) and [UN SDG 4](https://sdgs.un.org/goals/goal4) — targets 15.5 and 4.7 considered as potential, not established, relevance.

This review is a project planning document. Only the DPGA can determine recognition under its current review process, and the project makes no DPG status claim.
