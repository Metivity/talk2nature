# Talk2Nature

**Listen closely. Understand carefully.**

Talk2Nature documents research on nonhuman communication and builds tools for careful, reproducible animal-sound observation. It is an early-stage independent project: **there is no general animal translator or trained Talk2Nature model.**

Current source release: [v0.1.0](https://github.com/Metivity/talk2nature/releases/tag/v0.1.0), an early pre-1.0 version whose interfaces and formats may change. Cite the software with [`CITATION.cff`](CITATION.cff) and record the exact commit used.

Website: [metivity.github.io/talk2nature](https://metivity.github.io/talk2nature/)

## Start here

- **Just curious?** Open the [Field Companion](https://metivity.github.io/talk2nature/app/) and choose **Try without a microphone**. The invented practice session needs no account, microphone permission, recording or upload. The [install guide](https://metivity.github.io/talk2nature/mobile/) explains the optional public-only offline shell.
- **Want to try one small contribution?** Follow the [good first phone task](https://github.com/Metivity/talk2nature/issues/115), or read [CONTRIBUTING.md](CONTRIBUTING.md) for other no-recording tasks. Trying the app does not require GitHub; posting an issue does. The task also offers email as an alternative.
- **Researcher or research-software engineer?** Start with the [evaluation kit](docs/RESEARCHER_START.md): a no-setup browser walkthrough or reproducible synthetic command-line example. Then see the [candidate run card](docs/BENCHMARK_CANDIDATE_RUN_CARD.md) for current research questions and the evidence still missing before any model run.
- **Scientific reviewer?** The [bat-context methods brief](docs/BAT_CONTEXT_REVIEW.md) asks for bounded feedback on one published evaluation design. Public-source review only; it does not request recordings or claim a partnership.
- **Need help or found a problem?** Choose the right route in [SUPPORT.md](SUPPORT.md). Keep private recordings, sensitive locations, credentials and participant information out of public reports.

## What is available

The [Field Companion](https://metivity.github.io/talk2nature/app/) guides outdoor listening, familiar-animal observation and WAV review. Its browser audio workflow is user-started and foreground-only; sessions require deliberate export. It does not promise background recording, animal identification or general translation. Audio and notes stay local, and exports may be unencrypted; inspect them before sharing. Read the [mobile audit](docs/MOBILE_AUDIT.md) for limits and open device checks.

[Nature Station](https://metivity.github.io/talk2nature/tools/station/) records bounded, foreground observations and optional encounter notes. [Compare](https://metivity.github.io/talk2nature/app/compare/) reviews invented or user-selected session exports. [Listen](https://metivity.github.io/talk2nature/tools/listen/) annotates WAVs and local notebooks and can open a session ZIP locally. A notebook keeps the full session journal as source context, not as annotation labels. These tools do not upload recordings. Start with the [station and AI architecture](docs/NATURE_STATION.md) and [Listen guide](docs/LISTEN.md) for technical details.

The public [research atlas](https://metivity.github.io/talk2nature/research/atlas/) connects literature to cited, coarse locations. The evidence library records what was reviewed, what each source supports and where uncertainty remains. Source links do not mean that Talk2Nature has read every paper or partnered with listed organizations.

Several advanced exchange paths are prototypes, not general integrations:

- [Audacity export](docs/AUDACITY_EXPORT.md) is a one-way local package for a WAV, timed labels and provenance.
- [AOEF 1.1 export](docs/INTEROPERABILITY.md) was imported into Whombat using invented audio; this verifies one synthetic format path, not scientific suitability or compatibility with every dataset.
- [Darwin Core and Audubon Core notes](docs/DATA_INTEROPERABILITY.md) are future metadata references; Talk2Nature does not claim conformance to either standard.
- The [Field Notes demo](https://metivity.github.io/talk2nature/field-notes/demo/) rehearses permission and withdrawal steps with invented entries stored only in browser memory; it does not connect to the private database.
- The [Android Station source preview](native-android/README.md) is experimental, not an app-store release or validated field recorder.

## Current research boundaries

The first communication-adjacent ML candidate is Egyptian fruit-bat interaction-context prediction; bird sound detection and parrot caller identity are separate tasks. All remain research candidates. Dataset joins, rights, reviewer input and leakage-safe evaluation still need review. [Read the candidate run card](docs/BENCHMARK_CANDIDATE_RUN_CARD.md).

The [AutoResearch adaptation](docs/AUTORESEARCH_ADAPTATION.md) and [agent program](research/autoresearch/program.md) describe safeguards for a possible future experiment. The program is **NOT READY**; the documents do not start training or authorize real-data use. We have no confirmed institutional partners or DPG recognition.

## Develop locally

Python 3.10+; the static website and research toolkit use the standard library. Node is only needed for browser-module tests.

```sh
python3 web/build.py
python3 -m http.server 4173 --bind 127.0.0.1 --directory dist
```

Open http://127.0.0.1:4173. Local builds are marked noindex. Synthetic examples are invented metadata for checking software behavior, not datasets, experiments or model results.

```sh
python3 -m talk2nature.manifest examples/recordings.synthetic.json --output tmp/demo-split.json
python3 -m talk2nature.annotations examples/annotations.synthetic.json
python3 -m unittest discover -s tests -v
node --test tests/*.test.mjs
python3 scripts/check_site.py
```

For a public build, provide the actual site origin explicitly and publish only `dist/`:

```sh
python3 web/build.py --public --base-url https://metivity.github.io/talk2nature --repo-url https://github.com/Metivity/talk2nature
python3 scripts/check_site.py
```

See [deployment notes](docs/DEPLOYMENT.md), [current status](docs/STATUS.md) and [project scope](docs/GOAL.md). Passing software checks does not establish a scientific result or authorize deployment.

## Repository map

- `content/`: public research summaries, opportunity records and source inventory.
- `web/`: static website builder and assets.
- `talk2nature/`: reproducible research utilities.
- `research/resources.json`: versioned research, code and dataset catalog; see [collection and rights decisions](docs/COLLECTION.md).
- `examples/`: clearly labeled synthetic examples.
- `tests/`: validation, split and website tests.
- `data/external/`: ignored third-party samples and receipts; never website assets.
- `funding/`: ignored local application drafts; never included in the website.
- `admin/`: separate owner-only local prototype; real observations and uploads remain disabled. See [setup](admin/README.md), [private architecture](docs/PRIVATE_ARCHITECTURE.md) and [Field Notes gates](docs/FIELD_NOTES.md).

## Licensing and reuse

Original software: Apache-2.0 (`LICENSE`). Original public summaries in `content/`: CC BY 4.0, attributed to contributors. Linked papers, source recordings, datasets, model weights and other third-party material retain their own terms; no third-party audio or weights are distributed. See [`NOTICE`](NOTICE) and the [open-source reuse guide](docs/OPEN_SOURCE.md).

Talk2Nature is a working name; no trademark clearance or nonprofit registration is claimed. See the [preliminary name-risk review](docs/BRAND_REVIEW.md). The Metivity repository does not establish a separate funding applicant or scientific institution. Our [open-source health and adoption plan](docs/OPEN_SOURCE_PRACTICE.md) tracks how we build sustainable, useful participation.
