# Next atlas and observation goals

Reviewed October 4, 2026. Public board: https://metivity.github.io/talk2nature/research/atlas/goals/

These milestones describe the next program work. They are not claims of funding, recruitment, scientific approval, partnership or a release of participant data. The bounded October 4 software/research task is to expand geography and publish this board; completing it does not complete every future milestone.

| Goal | Current state | Completion evidence | Next action |
| --- | --- | --- | --- |
| 20 notes with supported geography | 20 of 20; coverage target reached | Primary-source location passage, correct location role, coarse public point and review date on each note | Deepen abstract-only reviews and retain explicit unknowns in the remaining unmapped notes |
| Three historical source notes | Three of three; coverage target reached | Three distinct notes with original source years before 2000, review depth and observation/source-date separation | Obtain full methods for the new historical notes and continue checking later reassessments |
| One reviewed passive parrot pilot | Needs reviewer and access | Confirmed carers/species, avian specialist review, consent, independent labels, a successful physical-phone rehearsal | Resolve the access/reviewer checklist in `PILOT_PROTOCOL_DRAFT.md`; do not recruit or ingest real data prematurely |
| First protected observation release | Needs consent and hosting review | Reviewed protocol/rights, private hosting, tested withdrawal, human review and an independently checked public location projection | Finish the existing hosting/consent gates before implementing public participant pins |

## How progress is maintained

`content/atlas-goals.json` is the editorial goal register. `talk2nature.atlas.atlas_goals` calculates the two coverage counts from the validated atlas at build time. A note with two or more places counts once. Historical coverage uses the note's latest displayed study/source year and a strict pre-2000 boundary. The new historical notes explicitly label their original study years (1980 and 1985); later reassessments are separately dated citations, not newer experiments represented by those notes. Metrics cannot count unreviewed uploads, and unknown metric names or invalid targets fail the build. Scientific and infrastructure milestones remain visible plans without fabricated percentage completion. Goal completion criteria are readable on the public page without JavaScript.

Public literature notes and private studies use immutable evidence versions. New location/source metadata creates new versions without changing evidence already frozen into a study. Research collection, participant observations and public release remain separate decisions.

## A practical next sequence

1. Finish the remaining location review queue. For unresolved records, document whether the obstacle is missing geography, unavailable full text, ambiguous dataset linkage or multi-site scope. Do not create a place from an author's address.
2. Add two historical notes only after obtaining suitable primary passages and reviewing later criticism or limitations. The recent reef/honeyguide additions do not count as pre-2000 history.
3. Confirm Raviv's access to one species of companion parrot and an appropriate independent reviewer. Keep the current budgerigar choice provisional; a wild monk-parakeet corpus does not validate a household budgerigar protocol.
4. Rehearse capture on actual Android/iPhone hardware and independently annotate a bounded permitted sample. Do not report browser emulation as physical-device verification.
5. Resolve hosted storage, consent and withdrawal before opening real-data admission. Review location sensitivity independently from coordinate rounding; public sharing is optional.

No outreach messages, provider agreements, purchases or scientific endorsements were made in this expansion. Those steps retain the existing authorization and review requirements.

## October 4 continuation

The two catalog coverage targets are reached: 20 mapped notes and three historical notes. Six original short notes add vervet development, changing humpback songs, raven gestures, wolf howling, grouper–moray coordination and dolphin addressing. These are coverage milestones, not six independently validated findings. Several entries rely on primary abstracts or indexed selected passages; each says so. The parrot and participant-release gates remain open.

Raviv also requested an idea/open-source audit. The public implementation guide is `OPEN_SOURCE.md`. Name clearance, legal operator, independent scientific review and a reproducible baseline are the next decisions; no license, entity or name was changed. A preliminary founder-facing audit is saved locally in ignored output and is not part of the public site.
