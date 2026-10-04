# Evaluate Talk2Nature with a small, reproducible task

October 5, 2026. For researchers, research software engineers and prospective reviewers. This is a software evaluation kit, not a validated biological benchmark. It needs no account, animal recording, cloud service, model download or paid dependency.

## Choose one route

**Browser route:** open [Compare moments](https://metivity.github.io/talk2nature/app/compare/) and load the invented example pair. Inspect the complete and partial sessions, observer-entered notes and sampling differences. Prepare audio for manual playback only if useful, away from animals. Check whether you can explain why the two records do not establish a change in an animal. Close a session and confirm the other remains available. Report a confusing step or a workflow this could support; no file upload is needed.

**Research-code route:** use the public repository and the synthetic fixtures below. The code is standard-library Python 3.10+. Node is required only for the optional browser-module tests. Run in a fresh checkout or an existing clean checkout; use the exact revision recorded in the report.

```sh
git clone https://github.com/Metivity/talk2nature.git
cd talk2nature
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
| Canonical manifest hash | `4ce3aaa1f5ead99af3343d4baed5ac682e4862df9b65d4f08858d34aea93dd90` | Identifies this metadata fixture; it does not authenticate recordings or consent. |

The default seed is `talk2nature-v1`. Repeating the splitter with unchanged input and seed should produce the same file. Record the commit if a future fixture changes. The current splitter groups declared individual IDs, sessions and exact source hashes transitively. It **does not yet group households or devices**, detect near-duplicates or inspect pretrained-model overlap; the proposed parrot protocol requires those additional controls before an empirical evaluation. Ten fixture groups are not a sample-size recommendation.

Optional software checks:

```sh
python3 -m unittest discover -s tests -v
node --test tests/*.test.mjs
```

A passing run establishes behavior on tested inputs, not scientific validity. Record the actual output and failures, rather than copying the expected values into a success report. Use the [reproduction report form](https://github.com/Metivity/talk2nature/issues/new?template=reproduction.yml). Redact local usernames and paths; do not attach private media, environment files, credentials or participant details. A maintainer/AI rerun is not an independent reproduction.

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

First adapter acceptance: one documented destination version, synthetic complete/partial/discard examples, a loss report and target-tool validation. If the target cannot express an essential distinction, report the incompatibility rather than silently dropping it. No export bridge is implemented by this document.

## Credit and use

[CITATION.cff](../CITATION.cff) identifies the original software. Include the exact commit in methods; cite papers and external data separately. There is no archival DOI yet. Confirm release authors and archive scope before a future Zenodo deposit; copying a whole mixed-license repository into a software archive deserves an explicit review. See [reuse boundaries](OPEN_SOURCE.md).

The kit can establish whether the workflow is understandable and reproducible. Real research still needs the [pilot gates](PILOT_PROTOCOL_DRAFT.md), a scientific reviewer, appropriate data rights and approved storage. No animal playback, recruitment or real-data intake is enabled here.
