# Talk2Nature

**Listen closely. Understand carefully.**

An early-stage project documenting the science of nonhuman communication and building tools for reproducible animal-sound research. No general animal translator or trained Talk2Nature model exists yet.

**Current source release:** [v0.1.0](https://github.com/Metivity/talk2nature/releases/tag/v0.1.0), an early pre-1.0 version whose interfaces and formats may change. Cite the software with [`CITATION.cff`](CITATION.cff) and record the exact commit used.

Website: https://metivity.github.io/talk2nature/

**Mobile:** [Open the Field Companion](https://metivity.github.io/talk2nature/app/) for outdoor listening, companion observations and WAV review. [Install guide and share page](https://metivity.github.io/talk2nature/mobile/) · [Product audit](docs/MOBILE_AUDIT.md). The observation-practice exercise and its limits are documented in [its project record](docs/OBSERVATION_PRACTICE.md). Optional offline support saves public app files only; export your audio and notes before leaving. An experimental [Android Station source preview](native-android/README.md) now builds locally; it is not a store release or a validated field recorder.

**First tools:** [Nature Station](https://metivity.github.io/talk2nature/tools/station/) captures user-started, foreground-only sound observations and optional encounter markers. [Compare](https://metivity.github.io/talk2nature/app/compare/) reviews a saved session ZIP; [Listen](https://metivity.github.io/talk2nature/tools/listen/) annotates WAVs or notebooks and can open that ZIP locally to select one clip. The notebook keeps the complete session journal as source context—not annotation labels—and is unencrypted, so review it before sharing. A [Python report](docs/LISTEN.md) examines labels and a metadata splitter groups declared related animals/sessions. Start with synthetic examples; no animal meaning is inferred. Read the [station, device and AI architecture](docs/NATURE_STATION.md).

**Use another sound editor:** [Continue in Audacity](docs/AUDACITY_EXPORT.md) packages a local WAV, timed labels and complete original annotations with a conversion report. This is a one-way prototype for evaluation; Audacity edits do not update the Talk2Nature notebook.

**Research annotation exchange:** Listen has an experimental one-way [AOEF 1.1 export](docs/INTEROPERABILITY.md) for a separate annotation workbench. Synthetic serialization passed with soundevent 2.10.0; Whombat application import is still untested. The export is local-only and preserves a full, unencrypted provenance sidecar.

**Research atlas:** [Explore places and historical work](https://metivity.github.io/talk2nature/research/atlas/) alongside our evidence connections. All library notes remain visible; pins require cited locations. Read the [coverage, provenance and contribution guide](docs/RESEARCH_ATLAS.md).

## Participate

**For researchers:** use the [evaluation starter pack](docs/RESEARCHER_START.md) for a browser walkthrough or reproducible synthetic command-line example, expected outputs and an honest failure-report route. [CITATION.cff](CITATION.cff) provides software citation metadata; record the exact commit used and cite underlying papers/data separately. No archival DOI or scientific validation is implied.

Start with a small [contribution](CONTRIBUTING.md). See [governance](GOVERNANCE.md), [community conduct](CODE_OF_CONDUCT.md), [security reports](SECURITY.md) and the [open-science/community map](https://metivity.github.io/talk2nature/community/). We have no confirmed institutional partners or DPG recognition.

For a future agent-assisted ML study, read the [AutoResearch adaptation](docs/AUTORESEARCH_ADAPTATION.md) and its [not-ready agent program](research/autoresearch/program.md). These define experiment safeguards; they do not start model training or approve real-data use.

Our [open-source health and adoption plan](docs/OPEN_SOURCE_PRACTICE.md) explains how we make contributions useful, measure progress without vanity metrics and keep the project maintainable.

Need help? See [SUPPORT.md](SUPPORT.md). University and research-software groups can start with the [synthetic evaluation brief](docs/UNIVERSITY_EVALUATION.md); it makes a narrow request for independent workflow feedback and sets out what is not yet ready for a real research pilot.

## Start locally

Python 3.10+; no third-party package required for the website or research toolkit.

```sh
python3 web/build.py
python3 -m http.server 4173 --bind 127.0.0.1 --directory dist
```

Open http://127.0.0.1:4173. Local builds are marked noindex.

```sh
python3 -m talk2nature.manifest examples/recordings.synthetic.json --output tmp/demo-split.json
python3 -m talk2nature.annotations examples/annotations.synthetic.json
python3 -m unittest discover -s tests -v
node --test tests/*.test.mjs
python3 scripts/check_site.py
```

The example is invented metadata for testing software behavior. It is not a dataset, experiment or model result. The split tool prevents shared individuals, sessions and exact source hashes from appearing in different partitions. It cannot detect unrecorded identities, near-duplicate audio or foundation-model training overlap.

## Android source preview

The native Android project is a separate, experimental phone-station prototype. Read its [scope, build and test instructions](native-android/README.md) before installing it. The source preview is not published in an app store and has not passed physical-phone or field validation.

## Public release

```sh
python3 web/build.py --public --base-url https://metivity.github.io/talk2nature --repo-url https://github.com/Metivity/talk2nature
python3 scripts/check_site.py
```

Publish only `dist/`. See [deployment notes](docs/DEPLOYMENT.md), [scope](docs/GOAL.md), [current status](docs/STATUS.md), the [project audit](docs/PROJECT_AUDIT.md) and [contribution guide](CONTRIBUTING.md).

## Repository map

- `content/`: public evidence notes, opportunity records and source inventory.
- `web/`: static website builder and assets.
- `native-android/`: experimental Android Station source project; see its README for platform and release limits.
- `talk2nature/`: reproducible research utilities.
- `research/resources.json`: versioned research/code/dataset catalog; see [collection decisions and commands](docs/COLLECTION.md).
- `data/external/`: ignored third-party samples and acquisition receipts; never website assets.
- `examples/`: clearly labeled synthetic examples.
- `tests/`: validation, leakage and website tests.
- `research/build_audit.py`: local-only earlier audit builder; requires ReportLab if regenerated and is excluded from the public repository.
- `funding/`: ignored local application drafts; never included in the website.

## Licensing

Original software: Apache-2.0 (see `LICENSE`). Original public summaries in `content/`: CC BY 4.0, attributed to Talk2Nature contributors. Source titles, bibliographic facts, linked articles, recordings, model weights and third-party material retain their own terms. No third-party audio or weights are distributed. See `NOTICE`.

Read the [open-source scope and reuse guide](docs/OPEN_SOURCE.md) for commercial reuse, forks, contributor rights, model-license checks and the distinction between open code and permission to publish data. See the [preliminary name-risk review](docs/BRAND_REVIEW.md) before using or promoting the Talk2Nature name. Talk2Nature is a working name; no trademark clearance or registered nonprofit status is claimed.

## Private research workspace (phase two)

The local `admin/` prototype provides owner-only Google identity verification, a responsive observation form, review gates, synthetic metadata releases and withdrawal. Local owner Google sign-in and wrong-account denial have been verified; hosted provider setup remains pending. Real observations and audio uploads are disabled. See [setup](admin/README.md), [mobile and AI plan](docs/PHASE_TWO_PLAN.md), and [private architecture](docs/PRIVATE_ARCHITECTURE.md). This code and its private runtime data are separate from the public static build.

[Field Notes](https://metivity.github.io/talk2nature/field-notes/) introduces the app publicly. The local study planner connects protocols, sessions and observations to versioned research evidence in the database; see the [implemented workflow and next gates](docs/FIELD_NOTES.md).

[Try the interactive demo](https://metivity.github.io/talk2nature/field-notes/demo/): invented observations, separate permissions, practice review, simulated release and withdrawal. Choices stay in browser memory; no connection to the private database. Run its checks with `node --test tests/demo.test.mjs`.

The private database has a [local recovery rehearsal](admin/README.md#local-recovery-rehearsal) that restores a separate verified copy without activating it or copying live login sessions.
