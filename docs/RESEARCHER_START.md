# Evaluate Talk2Nature with a small, reproducible task

Updated October 31, 2026. For researchers, research software engineers and prospective reviewers. This is a software evaluation kit, not a validated biological benchmark. It needs no account, animal recording, cloud service, model download or paid dependency.

## Start here

**Try the browser workflow (a few minutes, no setup):** open [Compare moments](https://metivity.github.io/talk2nature/app/compare/) and choose **Try an example pair**. Compare the complete and partial invented sessions, their observer-entered notes and sampling differences. Close one session and confirm the other remains available. Ask what the interface lets you describe and which claims about animal behavior it cannot support. No microphone, playback or upload is needed. For a deeper file-format check, try the optional [Sound Handoff Lab](https://metivity.github.io/talk2nature/tools/interop/); Audacity is only needed for that route. A project estimate puts it at about 20 minutes; independent completion time has not been measured.

**Run the research-code example (optional):** Git and Python 3.10+; no extra packages or animal media. From a terminal:

```sh
git clone --depth 1 --branch main https://github.com/Metivity/talk2nature.git
cd talk2nature
git rev-parse HEAD
python3 --version
python3 -m talk2nature.annotations examples/annotations.synthetic.json
python3 -m talk2nature.manifest examples/recordings.synthetic.json --output tmp/reproduction/standard.json
python3 -m talk2nature.manifest examples/interactions.dyadic.synthetic.json --output tmp/reproduction/dyadic.json
```

Record the commit printed by `git rev-parse HEAD` with any report. The annotation and split fixtures exercise **separate** tools; the annotation report is not converted or admitted into either evaluation manifest. Split files go under ignored `tmp/reproduction/`.

To share a usability barrier, use the [short first-use form](https://github.com/Metivity/talk2nature/issues/new?template=first-use.yml); one sentence is enough and device details are optional. Posting requires GitHub sign-in and creates a public issue. For a technical rerun, use the [workflow report form](https://github.com/Metivity/talk2nature/issues/new?template=reproduction.yml). Keep private media and research details out of either report.

**Current clean-clone maintainer verification (October 31):** checked public `main` from a fresh depth-one HTTPS clone at [`b715fe3ce38ee4fb8b35f30e12a38ee482df92fd`](https://github.com/Metivity/talk2nature/commit/b715fe3ce38ee4fb8b35f30e12a38ee482df92fd). Environment: Python **3.12.5**, Node **22.22.1**, Git **2.53.0**; no packages were installed. All three research-code commands above succeeded. The invented annotation example reported an 8-second sample, two marked events, 2 seconds of marked coverage and zero observed context. The standard and dyadic outputs match expected SHA-256 values `814ccb3495156ef56ae43ccfe79faa4584843402c90d0d30462df93a52ebb35b` and `6a7e742f3f4056ad972d57d751837014c7a6ad4ac78d1046430b967165c9e139`; each declares policy SHA-256 `5d483661cbb78bb1f62578c2cf3dbe17c6ffb075d52f4fe2e3acf5c2281eb8d9`. Full suites passed: Python **244 tests, 1 skipped**; Node **171/171**. The local noindex build produced **162 pages plus 404** (checker: **163 HTML documents / 11,320 links**). The explicit-origin public-format build produced the same routes and the checker verified **163 HTML documents / 11,483 links / 162 reachable public routes**. Generated split files remained ignored under `tmp/reproduction/`, and the fresh clone remained tracked-clean. This is a maintainer reproduction of synthetic software fixtures, not independent researcher use, usability research, scientific validation or a biological result.

**Previous clean-clone verification (October 31):** public `main` at [`cc30c724753c83233d4b5a42f805a73235c2ac3f`](https://github.com/Metivity/talk2nature/commit/cc30c724753c83233d4b5a42f805a73235c2ac3f) passed the same three commands. Its dated full-suite, catalog and public-build details remain part of that historical check; the latest result above is the current baseline.

**Previous full researcher-kit check (October 29):** a fresh depth-one HTTPS clone checked public `main` at [`d8cfd41a2bb65874057c432ba1c735f725b1aad3`](https://github.com/Metivity/talk2nature/commit/d8cfd41a2bb65874057c432ba1c735f725b1aad3). Environment: Python 3.12.5, Node v22.22.1 and Git 2.53.0; no packages were installed, and `data/external/` was absent.

The annotation fixture reported an invented 8-second recording, two marked events, 2 seconds of interval-union coverage and zero observed context. The standard split produced 10 connected groups and 12/4/4 train/validation/test records (6/2/2 groups); the dyadic split produced 10 groups and 6/2/4 records (6/2/2 groups). Repeated runs were byte-identical: standard SHA-256 `814ccb3495156ef56ae43ccfe79faa4584843402c90d0d30462df93a52ebb35b`; dyadic `6a7e742f3f4056ad972d57d751837014c7a6ad4ac78d1046430b967165c9e139`.

The catalog validator accepted 284 resources. All 237 Python tests passed with one intentional skip, and all 161 Node tests passed. The local noindex build produced 154 pages plus 404 and passed the checker (155 HTML documents, 10,586 links). The explicit public-origin build also produced 154 pages plus 404 and passed the checker (155 HTML documents, 10,742 links; all 154 public routes reachable). Comparing its sitemap with the live sitemap preserved all 154 routes, with no missing or added URLs. The tracked clone remained clean after checks.

This is maintainer-run verification with synthetic fixtures, not independent reproduction, user research, scientific validation or a biological result. No raw parrot table, animal/participant data, third-party media or model weights were used. Independent reproduction remains unverified; AutoResearch remains **NOT READY**. See the [verification history](RESEARCHER_START_HISTORY.md) and [project status](STATUS.md).

Choose by question, not by dataset size. The [cross-species F0 note](https://metivity.github.io/talk2nature/research/bioacoustic-f0-estimation-cross-species-2025/) describes a pitch-estimation candidate with 13 waveform taxa and 233 monk-parakeet calls; it measures a signal feature, not call meaning, and remains metadata-only. Great-tit song structure, zebra-finch turn-taking, bat context prediction and the parrot phone-app cohort are separate research paths with different open gates. See the [species and dataset decision](FIRST_ANIMAL_PLAN.md) for the evidence and limits. No current candidate establishes call meaning; the bat candidate run card is a review lead, not a ready benchmark. AutoResearch remains **NOT READY**.

**For team annotation:** groups that need synchronized video and multi-person event coding can review our [Praat++ note](../praatplusplus-annotation-tool-2026/). The note concerns the pinned source revision only: static review found a hard-coded Flask session secret, a server binding to all interfaces, and first-login account setup for unregistered allowlisted names. Do not expose that revision on a shared network or use it with sensitive media. This was not a runtime or complete security test, and it says nothing about later revisions. Praat++ is not part of the Field Companion or a Talk2Nature service; any institutional use needs a current-revision security and privacy review.

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

## BORIS: complementary behavior coding, not a drop-in backend

[BORIS](https://www.boris.unito.it/) is an established free/open-source desktop tool for video/audio coding and live event logging. Its official [download page](https://www.boris.unito.it/download/) and [v10.0.2 release](https://github.com/olivierfriard/BORIS/releases/tag/v10.0.2) agree on the current version, dated October 16, 2026; the linked [user guide still says it applies to v9.15.0](https://www.boris.unito.it/user_guide/). The export guide covers subject, behavior/category/modifier, independent-variable, STATE/POINT, timing and media/image-frame fields. The official [features page](https://www.boris.unito.it/features/) lists CSV/TSV, spreadsheets, SQL, SDIS, Python/R dataframes, Praat TextGrid and other outputs.

Talk2Nature's current annotation schema is narrower: sound kind, bounded context, observation source, confidence and notes. Its Audacity bridge moves a selected WAV and a one-way label/JSON package; it is not a BORIS project importer. Mapping only timestamps would lose or misstate ethogram and subject semantics.

| Before any BORIS adapter | Acceptance evidence |
| --- | --- |
| Actual need | A researcher describes a concrete workflow and the exact BORIS version they use. No need is inferred from BORIS's existence. |
| Rights and example | A synthetic or rights-cleared sample export and representative project structure, with file-level terms checked. |
| Mapping | Field-by-field source-to-target map, explicit unknown/unsupported values and a machine-readable loss report; never convert a human observation into a model label. |
| Version validation | Test a synthetic complete/partial case in the named BORIS version and verify the reopened project/export, IDs, labels, timing and provenance. The v9.15.0 guide alone does not validate v10.0.2. |

Until those gates pass, recommend BORIS only as a complementary external analysis tool. No BORIS software, code, project or media has been acquired or tested here; no adapter or BORIS partnership is claimed.

## Arbimon: existing hosted acoustic research infrastructure

[Arbimon](https://arbimon.org/support/arbimon/get-started/getting-started-with-arbimon/) documents collaborative projects and sites, passive-audio upload, visual inspection, analysis jobs, human validation, insights and optional publishing. Its separate [desktop Uploader](https://arbimon.org/support/arbimon/import/using-the-arbimon-uploader-app/) imports WAV/FLAC and segments files into one-minute recordings; its [project backup](https://arbimon.org/support/arbimon/settings/exporting-project-backups/) documents metadata, validations and analysis results, with some derived Insight material exported separately. This is a credible existing destination to evaluate for university workflows, not evidence that Talk2Nature is integrated or that all uploaded data are open.

**Zero Command boundary:** Talk2Nature's Field Companion remains user-started, passive and local-first. Do not silently upload recordings or add playback/cues. A future researcher handoff must be a deliberate export of permitted files to a named destination, with provenance and a loss report. Start with a synthetic fixture; review training use, retention, deletion/withdrawal, region, access, export, institutional rules and reversibility before considering real data. The device acceptance gate still requires a named phone and no-animal rehearsal.

**Arbimon terms review (31 October 2026):** RFCx's [privacy policy](https://rfcx.org/privacy-policy) says Arbimon-submitted audio, labels and metadata may be used for ML training; newly submitted data can be opted out from future training, but effects already incorporated into models cannot be removed, and annotations/labels may be retained indefinitely. Its [terms](https://rfcx.org/terms-of-service) describe a perpetual, irrevocable license covering submitted recordings, metadata, annotations and derived data for RFCx and its ML partners. The terms also require written disclosure for users affiliated with a competing or substantially similar platform and restrict using Arbimon to inform development of competing products. Talk2Nature's status under those clauses is unresolved; this summary is not a legal determination.

**Decision:** Arbimon remains public prior-art documentation only. Do not create an account, use it to benchmark or develop Talk2Nature, add a connector, or hand off project data until an authorized review resolves applicability and any required written disclosure or permission. Keep the field workflow local-first and platform-neutral; evaluate another named destination only after a researcher documents a concrete need. No account, app, recording, upload, API or backup was tested; no partner or institution has approved a workflow.

October 5 software continuation: a narrower [Audacity export](AUDACITY_EXPORT.md) now packages an individual WAV, timed annotations, full original metadata and a conversion report. It does not convert an entire Station session, infer monitoring effort or implement Safe & Sound. It is a prototype for evaluation; external demand and native verification scope are recorded separately.

## Credit and use

[CITATION.cff](../CITATION.cff) identifies the original software. Include the exact commit in methods; cite papers and external data separately. There is no archival DOI yet. Confirm release authors and archive scope before a future Zenodo deposit; copying a whole mixed-license repository into a software archive deserves an explicit review. See [reuse boundaries](OPEN_SOURCE.md).

The kit can establish whether the workflow is understandable and reproducible. Real research still needs the [pilot gates](PILOT_PROTOCOL_DRAFT.md), a scientific reviewer, appropriate data rights and approved storage. No animal playback, recruitment or real-data intake is enabled here.
