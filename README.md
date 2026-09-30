# Talk2Nature

**Listen closely. Understand carefully.**

An early-stage project documenting the science of nonhuman communication and building tools for reproducible animal-sound research. No general animal translator or trained Talk2Nature model exists yet.

Website: https://metivity.github.io/talk2nature/

## Start locally

Python 3.10+; no third-party package required for the website or research toolkit.

```sh
python3 web/build.py
python3 -m http.server 4173 --bind 127.0.0.1 --directory dist
```

Open http://127.0.0.1:4173. Local builds are marked noindex.

```sh
python3 -m talk2nature.manifest examples/recordings.synthetic.json --output tmp/demo-split.json
python3 -m unittest discover -s tests -v
python3 scripts/check_site.py
```

The example is invented metadata for testing software behavior. It is not a dataset, experiment or model result. The split tool prevents shared individuals, sessions and exact source hashes from appearing in different partitions. It cannot detect unrecorded identities, near-duplicate audio or foundation-model training overlap.

## Public release

```sh
python3 web/build.py --public --base-url https://metivity.github.io/talk2nature --repo-url https://github.com/Metivity/talk2nature
python3 scripts/check_site.py
```

Publish only `dist/`. See [deployment notes](docs/DEPLOYMENT.md), [scope](docs/GOAL.md), [current status](docs/STATUS.md) and [contribution guide](CONTRIBUTING.md).

## Repository map

- `content/`: public evidence notes, opportunity records and source inventory.
- `web/`: static website builder and assets.
- `talk2nature/`: reproducible research utilities.
- `examples/`: clearly labeled synthetic examples.
- `tests/`: validation, leakage and website tests.
- `research/build_audit.py`: local-only earlier audit builder; requires ReportLab if regenerated and is excluded from the public repository.
- `funding/`: ignored local application drafts; never included in the website.

## Licensing

Original software: Apache-2.0 (see `LICENSE`). Original public summaries in `content/`: CC BY 4.0, attributed to Talk2Nature contributors. Source titles, bibliographic facts, linked articles, recordings, model weights and third-party material retain their own terms. No third-party audio or weights are distributed. See `NOTICE`.

## Private research workspace (phase two)

The local `admin/` prototype provides owner-only Google identity verification, a responsive observation form, review gates, synthetic metadata releases and withdrawal. Provider setup is still pending; this is not a live Google-authenticated service. Real observations and audio uploads are disabled. See [setup](admin/README.md), [mobile and AI plan](docs/PHASE_TWO_PLAN.md), and [private architecture](docs/PRIVATE_ARCHITECTURE.md). This code and its private runtime data are separate from the public static build.
