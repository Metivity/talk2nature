# Evaluate Talk2Nature with a small, reproducible task

Updated October 25, 2026. For researchers, research software engineers and prospective reviewers. This is a software evaluation kit, not a validated biological benchmark. It needs no account, animal recording, cloud service, model download or paid dependency.

Choose by question, not by dataset size. The [cross-species F0 note](https://metivity.github.io/talk2nature/research/bioacoustic-f0-estimation-cross-species-2025/) describes a pitch-estimation candidate with 13 waveform taxa and 233 monk-parakeet calls; it measures a signal feature, not call meaning, and remains metadata-only. Great-tit song structure, zebra-finch turn-taking, bat context prediction and the parrot phone-app cohort are separate research paths with different open gates. See the [species and dataset decision](FIRST_ANIMAL_PLAN.md) for the evidence and limits. No current candidate establishes call meaning; the bat candidate run card is a review lead, not a ready benchmark. AutoResearch remains **NOT READY**.

**Latest clean-clone check:** on October 25, a fresh depth-one HTTPS clone checked public `main` at [`9d3e083`](https://github.com/Metivity/talk2nature/commit/9d3e0835ca816401a504681ac8e5d8a7a863b123) with Python 3.12.5, Node 22.22.1 and Git 2.53.0; no packages were installed. The documented synthetic annotation and standard grouped-split examples matched their expected structure: an invented 8-second recording, two events, 2 seconds of interval-union coverage, zero observed context, then 10 connected groups with 12/4/4 records and 6/2/2 groups. All 172 Python tests passed with one intentional external-sample skip and all 122 Node tests passed. The local noindex build checked 139 HTML documents and 7,120 links; the public-origin build checked 139 HTML documents, 7,260 links and all 138 public routes. The fresh clone remained clean. This is maintainer-run evidence, not an independent reproduction or biological result; no animal data, third-party media or model weights were acquired or run. See the [verification history](RESEARCHER_START_HISTORY.md) and [project status](STATUS.md).

**Previous clean-clone check (e8dd073):** on October 25, a fresh depth-one HTTPS clone checked public `main` at [e8dd073](https://github.com/Metivity/talk2nature/commit/e8dd07306f30a1a254708d9a5d14053535043e45) with Python 3.12.5, Node 22.22.1 and Git 2.53.0; no packages were installed. The documented annotation and standard/dyadic split examples passed. The annotation fixture reported an invented 8-second recording, two marked events, 2 seconds of interval-union coverage and zero observed context. The standard split produced 10 connected groups and 12/4/4 train/validation/test records; repeating it at the same path produced the same SHA-256 (`814ccb3495156ef56ae43ccfe79faa4584843402c90d0d30462df93a52ebb35b`). The dyadic split produced 10 groups and 6/2/4 records, keeping its linked interaction chain together (SHA-256 `6a7e742f3f4056ad972d57d751837014c7a6ad4ac78d1046430b967165c9e139`). All 170 Python tests passed with one intentional external-sample skip and all 122 Node tests passed. The local noindex build checked 139 HTML documents and 7,090 links; the explicit public-origin build checked 139 HTML documents, 7,230 links and all 138 public routes. The fresh clone remained clean. This is a maintainer-run synthetic check, not an independent reproduction or biological result; no animal data, third-party media or model weights were acquired or run. See the [verification history](RESEARCHER_START_HISTORY.md) and [project status](STATUS.md).

## Choose one route

**Quick browser route (a few minutes; no setup):** open [Compare moments](https://metivity.github.io/talk2nature/app/compare/) and choose **Try an example pair**. Compare the complete and partial sessions, their observer-entered notes and the sampling differences. Ask yourself: what does the interface let you describe, and what would be an unsupported claim about animal behavior? Close one session and confirm the other remains available. No microphone, playback or upload is needed. For a deeper file-format check, use the optional [Sound Handoff Lab](https://metivity.github.io/talk2nature/tools/interop/); it takes about 20 minutes and Audacity is only needed for that route. To report a barrier or useful gap, use the [public workflow report form](https://github.com/Metivity/talk2nature/issues/new?template=reproduction.yml), include the page URL and access date, and keep private media and research details out of the report. Trying the workflow needs no account; posting to GitHub requires sign-in and creates a public issue. The time estimate is a project estimate; independent first-use timing has not yet been measured.

**Research-code route (optional):** use the current public repository and its synthetic fixtures. Git and Python 3.10+ are required; the Python tools use the standard library, so no extra packages or animal media are needed.

```sh
git clone --depth 1 --branch main https://github.com/Metivity/talk2nature.git
cd talk2nature
git rev-parse HEAD
python3 --version
python3 -m talk2nature.annotations examples/annotations.synthetic.json
python3 -m talk2nature.manifest examples/recordings.synthetic.json --output tmp/reproduction/standard.json
python3 -m talk2nature.manifest examples/interactions.dyadic.synthetic.json --output tmp/reproduction/dyadic.json
```

Record the commit printed by `git rev-parse HEAD` with any report. These commands use current `main`; the generated split files are written under ignored `tmp/reproduction/`. The annotation and split fixtures exercise **separate** tools. The annotation report is not converted or admitted into either evaluation manifest.

## Expected observations

| Check | Expected for these committed synthetic fixtures | What it does not establish |
| --- | --- | --- |
| Annotation report | 8-second declared duration; two marked events; 2 seconds of interval-union coverage; zero seconds with observed context | Marked coverage is not detection accuracy or a behavior label. |
| Annotation warnings | Unknown context; unknown animal/session identity; synthetic origin | The fixture contains no biological observation. |
| Standard metadata split | 10 connected groups; 12/4/4 train/validation/test records; 6/2/2 groups | The records and identities are invented, not independent animals from a study. |
| Dyadic metadata split | 10 connected groups; 6/2/4 train/validation/test records; the first three linked events stay together | The fixture tests declared-participant grouping, not whether identities or links in real data are true or complete. |

The splitter uses seed `talk2nature-v1` by default. Repeating a split with unchanged input, code revision and seed should produce the same file. Ten synthetic groups are not a sample-size recommendation. For the checksums from the older pinned baseline, see the dated [verification history](RESEARCHER_START_HISTORY.md); use those only when reproducing that exact historical revision.

### Multi-animal interactions

For an event involving more than one animal, list **every known participant** in `individual_ids`, regardless of caller, recipient or observer role. The splitter connects records transitively: if A interacts with B and B later interacts with C, all records for A, B and C stay in one partition. Omitting a participant defeats that safeguard. Do not invent an identity or use one shared placeholder such as `unknown`; this manifest rejects unresolved identity values. Resolve identities from an appropriate source, or keep the record out of this individual-holdout evaluation until a reviewer approves a different policy.

The validator rejects common placeholder tokens (`unknown`, `na`, `n/a`, `none`, `null`, `tbd`, `pending`) in animal IDs and session IDs. A placeholder is not a pseudonymous identity: if a required grouping key is unresolved, fix the source manifest or exclude those records under a documented rule.

The dyadic example has no animal, person, recording or observed interaction; it tests software behavior only. Grouping can enforce only declared identities and other selected dimensions. It cannot discover omitted participants, validate biological identity, establish label quality, or determine whether treatment, site, device, time or pretrained-model overlap also needs to be held out.

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
