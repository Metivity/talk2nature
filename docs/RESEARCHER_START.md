# Evaluate Talk2Nature with a small, reproducible task

Updated October 23, 2026. For researchers, research software engineers and prospective reviewers. This is a software evaluation kit, not a validated biological benchmark. It needs no account, animal recording, cloud service, model download or paid dependency.

The current research decision is recorded in the [candidate run card](BENCHMARK_CANDIDATE_RUN_CARD.md): bat interaction-context prediction is the closest current ML candidate to a communication question, while CEB detection and parrot caller-identity remain separate tasks. The bat candidate is not ready for reproduction until data joins/groups and rights are verified and independent reviewers approve the design. AutoResearch remains **NOT READY**.

**Latest maintainer check:** on October 23, a fresh public clone of [`main` at `76c4c768`](https://github.com/Metivity/talk2nature/commit/76c4c7687a83db3f057fd0b601b9019465f7f8bc) passed the synthetic examples, 153 Python and 115 Node tests, validation of 173 catalog resources, and local plus public-origin site checks. The Wytham page and sitemap were also checked. This does not count as an independent reproduction; dated checks are preserved in the [verification history](RESEARCHER_START_HISTORY.md), and current evidence and limits are in [project status](STATUS.md).

## Choose one route

**Quick browser route (a few minutes; no setup):** open [Compare moments](https://metivity.github.io/talk2nature/app/compare/) and choose **Try an example pair**. Compare the complete and partial sessions, their observer-entered notes and the sampling differences. Ask yourself: what does the interface let you describe, and what would be an unsupported claim about animal behavior? Close one session and confirm the other remains available. No microphone, playback or upload is needed. For a deeper file-format check, use the optional [Sound Handoff Lab](https://metivity.github.io/talk2nature/tools/interop/); it takes about 20 minutes and Audacity is only needed for that route. To report a barrier or useful gap, use the [public workflow report form](https://github.com/Metivity/talk2nature/issues/new?template=reproduction.yml), include the page URL and access date, and keep private media and research details out of the report. Trying the workflow needs no account; posting to GitHub requires sign-in and creates a public issue. The time estimate is a project estimate; independent first-use timing has not yet been measured.

**Research-code route:** use the public repository and the synthetic fixtures below. The code is standard-library Python 3.10+. Node is required only for the optional browser-module tests. The command block pins a historical exact-output baseline, `aa7119b7635aa3390bd1f7b3bb982e3b596f438d`; it does not claim that revision is the current deployed `main`. To reproduce the historical baseline and its expected checksum, check out that exact revision and verify the printed commit before running the commands:

```sh
git clone https://github.com/Metivity/talk2nature.git
cd talk2nature
git checkout aa7119b7635aa3390bd1f7b3bb982e3b596f438d
git rev-parse HEAD
python3 --version
python3 -m talk2nature.annotations examples/annotations.synthetic.json
python3 -m talk2nature.manifest examples/recordings.synthetic.json --output tmp/reproduction/split.json
```

The two fixtures exercise **separate** tools. The annotation report is not converted or admitted into the evaluation manifest.

## Expected observations

| Check | Expected for these committed synthetic fixtures | Interpretation |
| --- | --- | --- |
| Annotation report | 8-second declared duration; two marked events; 2 seconds of interval-union coverage; zero seconds with observed context | Marked coverage is not detection accuracy. |
| Annotation warnings | Unknown context; unknown animal/session identity; synthetic origin | A valid file can still be unsuitable for a research claim. |
| Metadata split | 10 connected groups; 12 train, 4 validation and 4 test records | These are invented declarations, not independent animals observed in a study. |
| `manifest_sha256` in generated split | `4ce3aaa1f5ead99af3343d4baed5ac682e4862df9b65d4f08858d34aea93dd90` | Identifies the source metadata manifest; it does not authenticate recordings or consent. |
| Generated split-file SHA-256 | `f2188833c5476cde4db5ec9a21198ad2483691d59264e795e0df9a9829e12bc4` | Checksum of the entire JSON output in this software revision and environment. |

The default seed is `talk2nature-v1`. Repeating the splitter with unchanged input and seed should produce the same file. Record the commit if a future fixture changes. At the pinned release, the splitter groups declared individual IDs, sessions and exact source hashes transitively. Ten fixture groups are not a sample-size recommendation.

### Multi-animal interactions

For an event involving more than one animal, list **every known participant** in `individual_ids`, regardless of caller, recipient or observer role. The splitter connects records transitively: if A interacts with B and B later interacts with C, all records for A, B and C stay in one partition. Omitting a participant defeats that safeguard. Do not invent an identity or use one shared placeholder such as `unknown`; this manifest rejects unresolved identity values. Resolve identities from an appropriate source, or keep the record out of this individual-holdout evaluation until a reviewer approves a different policy.

The current-main validator rejects common placeholder tokens (`unknown`, `na`, `n/a`, `none`, `null`, `tbd`, `pending`) in animal IDs and session IDs. A placeholder is not a pseudonymous identity: if a required grouping key is unresolved, fix the source manifest or exclude those records under a documented rule before making a split. The historical exact-output revision above predates this added validation; use the current source for the stricter check.

Try the invented dyadic example:

```sh
python3 -m talk2nature.manifest examples/interactions.dyadic.synthetic.json --output tmp/reproduction/dyadic-split.json
```

It should report 10 connected groups. The first three events form a transitive chain and must receive one split assignment. The example has no animal, person, recording or observed interaction; it tests software behavior only. Grouping can enforce only declared identities and other selected dimensions. It cannot discover omitted participants, validate biological identity, establish label quality, or determine whether treatment, site, device, time or pretrained-model overlap also needs to be held out.

Optional software checks:

```sh
python3 -m unittest discover -s tests -v
node --test tests/*.test.mjs
```

A passing run establishes behavior on tested inputs, not scientific validity. Record the actual output and failures, rather than copying the expected values into a success report. Use the [workflow report form](https://github.com/Metivity/talk2nature/issues/new?template=reproduction.yml). Redact local usernames and paths; do not attach private media, environment files, credentials or participant details. A maintainer/AI rerun is not an independent reproduction.

## Three useful first contributions

1. **Reproduce:** run either route on a clean device or checkout and describe where the instructions fail. An honest failure report is useful.
2. **Review:** critique one part of the [passive parrot draft](PILOT_PROTOCOL_DRAFT.md): visible-label definitions, missing observations, caller uncertainty or household/device confounding. State your relevant expertise and exact review scope; a comment is not automatic protocol approval.
3. **Connect:** identify one existing tool your team uses and a concrete export mismatch. Bring a synthetic example and a versioned format specification. We should measure preserved and lost information before calling an adapter interoperable.

## A proposed interoperability contribution

The Safe & Sound project has explored adapting Camtrap DP to passive acoustic monitoring. Its [team discussion](https://wildlabs.net/en/discussion/safe-and-sound-standard-bioacoustic-data) and [TABMON account](https://tabmon-eu.nina.no/news/2025-09-safe_and_sound/) identify deployment, recording settings, clocks and processing provenance as important. A March 2026 comment links a project report; that report could not be retrieved in this review. The full current schema and conformance suite have **not** been reviewed. This is a collaboration lead, not a claim of compliance or partnership.

| Information | Talk2Nature today | Work before an adapter |
| --- | --- | --- |
| Sampling effort | Whole-window and detected-highlight modes; incomplete/discard status | Preserve mode and missingness; never convert selected highlights into continuous monitoring effort. |
| Clock and device | Device wall clock explicitly unverified; sample-relative offsets; capture settings | Distinguish unknown calibration/device identity from a measured property; review target requirements. |
| Behavior and source | Observer-entered notes and explicit uncertainty | Keep notes separate from independently reviewed labels and model predictions. |
| Rights and location | Public app files stay local; no research admission; public atlas contains literature regions | An adapter must not invent consent, a deployment location or a public-release license. |
| Models | No model execution in the public capture tools | Leave model fields absent where required; never manufacture a detection run. |

First session-format adapter acceptance: one documented destination version, synthetic complete/partial/discard examples, a loss report and target-tool validation. If the target cannot express an essential distinction, report the incompatibility rather than silently dropping it. No Safe & Sound bridge is implemented.

October 5 software continuation: a narrower [Audacity export](AUDACITY_EXPORT.md) now packages an individual WAV, timed annotations, full original metadata and a conversion report. It does not convert an entire Station session, infer monitoring effort or implement Safe & Sound. It is a prototype for evaluation; external demand and native verification scope are recorded separately.

## Credit and use

[CITATION.cff](../CITATION.cff) identifies the original software. Include the exact commit in methods; cite papers and external data separately. There is no archival DOI yet. Confirm release authors and archive scope before a future Zenodo deposit; copying a whole mixed-license repository into a software archive deserves an explicit review. See [reuse boundaries](OPEN_SOURCE.md).

The kit can establish whether the workflow is understandable and reproducible. Real research still needs the [pilot gates](PILOT_PROTOCOL_DRAFT.md), a scientific reviewer, appropriate data rights and approved storage. No animal playback, recruitment or real-data intake is enabled here.
