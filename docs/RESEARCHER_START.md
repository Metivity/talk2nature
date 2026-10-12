# Evaluate Talk2Nature with a small, reproducible task

Updated October 12, 2026. For researchers, research software engineers and prospective reviewers. This is a software evaluation kit, not a validated biological benchmark. It needs no account, animal recording, cloud service, model download or paid dependency.

## Choose one route

**Quick browser route (a few minutes; no setup):** open [Compare moments](https://metivity.github.io/talk2nature/app/compare/) and choose **Try an example pair**. Compare the complete and partial sessions, their observer-entered notes and the sampling differences. Ask yourself: what does the interface let you describe, and what would be an unsupported claim about animal behavior? Close one session and confirm the other remains available. No microphone, playback or upload is needed. For a deeper file-format check, use the optional [Sound Handoff Lab](https://metivity.github.io/talk2nature/tools/interop/); it takes about 20 minutes and Audacity is only needed for that route. To report a barrier or useful gap, use the [public reproduction and workflow form](https://github.com/Metivity/talk2nature/issues/new?template=reproduction.yml), include the page URL and access date, and keep private media and research details out of the report. The time estimate is a project estimate; independent first-use timing has not yet been measured.

**Research-code route:** use the public repository and the synthetic fixtures below. The code is standard-library Python 3.10+. Node is required only for the optional browser-module tests. The deployed software revision rehearsed for this kit is `aa7119b7635aa3390bd1f7b3bb982e3b596f438d`. To reproduce the recorded baseline, check out that exact revision and verify the printed commit before running the commands:

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

Optional software checks:

```sh
python3 -m unittest discover -s tests -v
node --test tests/*.test.mjs
```

A passing run establishes behavior on tested inputs, not scientific validity. Record the actual output and failures, rather than copying the expected values into a success report. Use the [reproduction report form](https://github.com/Metivity/talk2nature/issues/new?template=reproduction.yml). Redact local usernames and paths; do not attach private media, environment files, credentials or participant details. A maintainer/AI rerun is not an independent reproduction.

## Maintainer rehearsal — October 8, 2026

The pinned revision was cloned into a fresh public checkout and exercised on Darwin 25.4.0 arm64 with Python 3.12.5, Node v22.22.1 and Git 2.53.0. The annotation command returned the expected 8-second fixture, two marked events, 2 seconds of interval-union coverage and zero seconds with observed context. The split returned 10 connected groups and 12/4/4 records; repeating it with the same input and seed produced a byte-identical JSON file. The Python suite passed 51 tests and the Node suite passed 79 tests.

The live browser route was also inspected: its invented pair contained a 30-second complete and an 18-second partial budgerigar session, both with observer-declared labels. The comparison described the sampling difference without inferring biological change. Closing one session left the other open. No microphone, playback, upload, real observation, model or permission was used. These checks validate only the recorded software behavior. They were performed by the project maintainer and do **not** count as an independent reproduction or scientific review.

## Current-main clean-clone recheck — October 12, 2026

A fresh depth-one public clone of `main` at `a52876d6061f3eb73f0fd54cd436a6948bad59a2` ran the documented annotation and splitter commands, then the complete Python and Node suites. This main revision follows the deployed software revision `705daf95f19b2ed8a6e2ecdb60d607768a25b08d` only by a status-log edit; the software diff is empty. Python 3.12.5 reported 89 passing tests, and Node v22.22.1 reported 93 passing tests.

The annotation command returned an 8-second synthetic fixture with two marked events, 2 seconds of interval-union coverage and 0 seconds of observed context. The splitter returned 10 connected groups and 12/4/4 records, with policy SHA-256 `5d483661cbb78bb1f62578c2cf3dbe17c6ffb075d52f4fe2e3acf5c2281eb8d9`; the complete current-output SHA-256 was `814ccb3495156ef56ae43ccfe79faa4584843402c90d0d30462df93a52ebb35b`.

This maintainer-run public-clone check verifies current-source setup and tested software behavior; it is not an independent reproduction, scientific validation or biological result. Keep the older `aa7119b7635aa3390bd1f7b3bb982e3b596f438d` pin for its historical expected checksum. Current output includes the later context-label-presence diagnostic, so its complete JSON hash is intentionally different.

## Latest-main clean-clone recheck — October 12, 2026

A new depth-one public clone at `abbbd45a1606599a96b847d236c855a018da2158` (after the Station-to-Review release) ran the documented annotation and splitter commands, both complete test suites, the local build and the link/SEO boundary checker. Environment: Python 3.12.5, Node v22.22.1. The annotation report again showed an 8-second synthetic example, two marked events, 2 seconds of interval coverage and 0 seconds of observed context. The splitter produced 10 declared connected groups and 12/4/4 records; its complete output SHA-256 was `814ccb3495156ef56ae43ccfe79faa4584843402c90d0d30462df93a52ebb35b`.

The clean clone passed 89 Python tests and 98 Node tests. The noindex build produced 88 pages plus 404; the checker passed 89 HTML pages and 4,041 links. This is a maintainer-run clean-clone recheck, not an independent reproduction or a biological result. The live deployed code release is `cd74ccbe95c023fd40aca7ee72030bd0dd1ad05f`; `abbbd45` adds only the post-release status evidence to that release.

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

### October 11 maintainer recheck

A clean local clone was checked out at the pinned revision `aa7119b7635aa3390bd1f7b3bb982e3b596f438d` using Python 3.12.5 and Node v22.22.1. The documented annotation command returned the expected 8-second synthetic record, two marked events and 2 seconds of union coverage. The split command returned 10 connected groups and 12/4/4 records; its output SHA-256 matched `f2188833c5476cde4db5ec9a21198ad2483691d59264e795e0df9a9829e12bc4`. The pinned revision's Python suite passed 51 tests and its Node suite passed 79 tests. This was a maintainer rerun from a clean checkout, not an independent reproduction; the clone used the local Git object database.

### October 12 remote public-clone recheck

Cloned the public GitHub repository over HTTPS into a fresh temporary checkout and checked out the exact pinned revision `aa7119b7635aa3390bd1f7b3bb982e3b596f438d`. On Python 3.12.5 and Node v22.22.1, the documented annotation command reported an 8-second synthetic record, two events, 2 seconds of annotated interval coverage and zero seconds with observed context. The manifest command reported 10 declared groups and 12/4/4 train/validation/test records; its output SHA-256 matched the documented `f2188833c5476cde4db5ec9a21198ad2483691d59264e795e0df9a9829e12bc4`. All 51 Python tests and all 79 Node tests passed. This confirms the pinned instructions work from a remote public clone; it remains a maintainer rerun, not an independent reproduction, scientific validation or real-data result.

### October 12 release-candidate recheck

From a clean source archive of local commit `6841a18bc40a860b3fd7196941955afb7b77f982`, the documented annotation and split commands produced the expected 8-second/two-event report and 10 groups with 12/4/4 records. The generated split checksum remained `f2188833c5476cde4db5ec9a21198ad2483691d59264e795e0df9a9829e12bc4`. From the same archive, 63 Python tests, 86 JavaScript tests, the 31-record resource validator, the 80-page public build and the site checker (81 HTML pages, 3,542 links) passed.

This is a maintainer-run clean-archive check from the local Git object database, not an independent reproduction, remote clone or scientific result. Commit `6841a18` was not yet deployed when checked. Keep the public reproduction pin above until the candidate is published and verified.

### October 12 candidate: additional grouping controls

An unreleased candidate extends the synthetic fixture with invented household and device IDs. The default command remains grouped by declared animals, sessions and source hashes. To require more declared dimensions, pass each one explicitly:

```sh
python3 -m talk2nature.manifest examples/recordings.synthetic.json \
  --group-dimension household --group-dimension device \
  --output tmp/reproduction/split-household-device.json
```

Selected dimensions must be present on every record and are merged transitively with the built-in groups. The output now records the splitter algorithm, declared policy, policy fingerprint, manifest fingerprint, and both connected-group and record counts. With the current invented fixture, the default has 10 connected groups (6/2/2 by group; 12/4/4 by record); requiring household and device has 5 connected groups (3/1/1 by group; still 12/4/4 by record). The second result illustrates why record counts alone can obscure evaluation size.

| Candidate output | Manifest SHA-256 | Split-policy SHA-256 | Complete split JSON SHA-256 |
| --- | --- | --- | --- |
| Default dimensions | `08fe50c6caee487a3750788b52350243ea11e4ad2212f322bf7fd931d36a0778` | `5d483661cbb78bb1f62578c2cf3dbe17c6ffb075d52f4fe2e3acf5c2281eb8d9` | `74dc0a0d50cf3aa94360abc9b78e49c614081eec12126745342371a2a6884a26` |
| Household + device | `08fe50c6caee487a3750788b52350243ea11e4ad2212f322bf7fd931d36a0778` | `b0d33e62efb2fabb65ea7d643b9e045a96d3e18c77c003a76e3f4203cd6bbe68` | `82dc1755f9491ffe777faa3be1a96f9f798e2fc9fd12f06f99540b6540438b6d` |

These IDs and links are only declarations in a synthetic fixture: the program does not verify that two recordings truly share a household/device, infer missing IDs, detect near-duplicates, or test overlap with pretraining data. Real study design may also need site, time, treatment, microphone, acquisition batch and other dimensions. Five synthetic groups are deliberately too few to support a useful biological benchmark. AutoResearch remains **NOT READY**. This candidate has not been published; the pinned public instructions and their earlier checksums remain the supported release baseline until deployment is separately verified.

### October 12 current committed-snapshot recheck

Created a fresh source archive from local commit `43bf04ce5da38aaa6ed96f9c5b211c9afc0df290` and reproduced the documented synthetic annotation and default split using Python 3.12.5. The report again showed an 8-second fixture, two marked events, 2 seconds of interval-union coverage, and zero seconds with observed context. The splitter returned ten connected groups and 12/4/4 records; its policy hash was `5d483661cbb78bb1f62578c2cf3dbe17c6ffb075d52f4fe2e3acf5c2281eb8d9`, and the complete output hash was `74dc0a0d50cf3aa94360abc9b78e49c614081eec12126745342371a2a6884a26`, matching the default candidate row above. The resource validator accepted 37 records. The Python suite passed 75 tests and Node v22.22.1 passed 92 tests. The public-origin build produced 84 pages plus 404; the checker verified 85 HTML files and 3,796 links.

This was a maintainer-run archive created from the local Git object database, not a remote clone, independent reproduction or scientific result. It excludes uncommitted working-tree changes. The public reproduction instructions remain pinned to the deployed release above; this candidate was not deployed.

### October 12 candidate: context-label presence diagnostic

The unreleased schema-v3 split output adds an explicit list of declared context labels and, for each partition, labels present and missing. This makes a label-coverage gap visible before anyone interprets model scores. It does not assess class balance, annotation reliability, biological representativeness or whether the split is appropriate for a particular claim. The algorithm and split assignments are unchanged from the preceding candidate.

With the current invented fixture, the default output retains 10 groups and 12/4/4 records, with both declared labels present in every partition. The optional household/device output has five groups and the same record counts; it also has both labels in each partition. The added regression test moves one invented label into a single individual group and checks that the other partitions explicitly report it missing.

| Candidate output | Split-policy SHA-256 | Complete split JSON SHA-256 |
| --- | --- | --- |
| Default dimensions | `5d483661cbb78bb1f62578c2cf3dbe17c6ffb075d52f4fe2e3acf5c2281eb8d9` | `814ccb3495156ef56ae43ccfe79faa4584843402c90d0d30462df93a52ebb35b` |
| Household + device | `b0d33e62efb2fabb65ea7d643b9e045a96d3e18c77c003a76e3f4203cd6bbe68` | `587a8b0793a0e7009100343669c7a9c9169358077491f129f269a88679c36af8` |

Both checksums are for maintainer-generated synthetic output from the current source candidate; they are not a scientific benchmark result. The public reproduction pin is unchanged, and this candidate remains local pending the normal review/release route.

### October 12 current-candidate source-archive rehearsal

To check that the current candidate did not depend on the maintainer's working directory or ignored acquired data, made a fresh source archive from committed base `43bf04ce5da38aaa6ed96f9c5b211c9afc0df290`, then applied the current tracked diff. The archive had no `.git`, `.env`, ignored `data/external/` samples or private database. This is a maintainer-generated local source snapshot, not a GitHub clone or an independent reproduction.

On Python 3.12.5 and Node v22.22.1, the documented annotation fixture returned 8 seconds, two marked events and 2 seconds of interval-union coverage. The schema-v3 split returned 10 groups and 12/4/4 records; its full JSON SHA-256 was `814ccb3495156ef56ae43ccfe79faa4584843402c90d0d30462df93a52ebb35b`. All 79 Python tests and 93 Node tests passed. The 43-resource validator passed, and the public-origin build and site checker passed with 87 HTML pages and 3,946 checked links.

This rehearsal confirms the current local code and public source files work together without ignored acquisition data. It does not establish independent usability, external reproduction, scientific validity, live indexing or release readiness.

### October 12 candidate: source-table structure report

The repository now includes `research/figshare_bat_annotation_report.json`, an aggregate-only audit of the full video-derived Egyptian fruit-bat annotation table. It records 48 known participant IDs across role fields and a 136-pair graph across three components; it contains no raw rows or subject IDs. It is **not** the EUSIPCO paper's filtered 35,074-call subset, its fold files, a model run, or evidence that the published subject-independent split is valid.

To regenerate it, use the locally acquired source file only after reviewing the item terms, receipt and limits in [COLLECTION.md](COLLECTION.md): `python3 scripts/inspect_bat_annotations.py --output research/figshare_bat_annotation_report.json`. The script verifies the file against its acquisition receipt and refuses to run if it has changed; the raw CSV stays in ignored `data/external/` and `training_admitted` remains false. No audio or video is needed. This is a maintainer-verified aggregate reproduction, not an independent researcher reproduction.


### October 12 current candidate: clean-source recheck

Reconstructed the current 232-file source candidate from committed base `4b606c058d6d728c75e642ad0beb779d9e3ddbca` plus its tracked working-tree diff. Candidate fingerprint: `ca03693397bb5c621e55ea463f14d18244a5cd2fa285fd833471474d24e84292`. No nonignored untracked source files were present. The fresh copy had no `.git`, `.env` or ignored `data/external/` acquisitions.

On Python 3.12.5, Node v22.22.1 and Git 2.53.0, the documented annotation command returned the expected 8-second synthetic fixture, two marked events and 2 seconds of interval-union coverage. The split command returned 10 connected groups and 12/4/4 records, with policy SHA-256 `5d483661cbb78bb1f62578c2cf3dbe17c6ffb075d52f4fe2e3acf5c2281eb8d9`. The generated split matched the documented complete-file hash `814ccb3495156ef56ae43ccfe79faa4584843402c90d0d30462df93a52ebb35b`; a second run was byte-identical. All 89 Python tests, 93 Node tests and 57 resource validations passed. The public-origin build generated 88 pages plus 404; the site checker passed 89 HTML files, 4,120 links and all 88 public pages reachable from the homepage.

This is a maintainer-run clean-source rehearsal of the uncommitted candidate, not a remote clone, independent researcher reproduction, biological result or release. The public reproduction instructions remain pinned to the deployed revision until a separately reviewed release.
