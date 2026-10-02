# Media and model lineage foundation

October 2, 2026 · Talk2Nature · schema v2. This is an owner-only **synthetic metadata rehearsal**. It stores neither recordings nor model weights, does not execute training/inference, and cannot authorize publication or real-data admission.

## What is implemented

Five normalized tables extend the existing study/observation/release database on SQLite and PostgreSQL:

| Table | Meaning and linkage |
| --- | --- |
| `research_media` | An immutable, invented audio/video descriptor linked to an observation and its study session. Modality, codec, sample/frame rate, duration, declared byte count/hash and device alias are checked as metadata. There is no object key, URL or upload body. |
| `media_sync` | An explicit audio/video pairing from the same session, with offset, drift, uncertainty, method/version and a bounded validity interval. |
| `model_runs` | A registered synthetic specification tied to one reviewed, nonrevoked training release and frozen study codebook. Records code revision, checkpoint hash/license declaration, environment hash, seed, complete observation splits, media versions and alignment versions. Registration does not execute a model. |
| `model_inputs` | Foreign-key membership for the exact media metadata version used by a run. |
| `model_results` | An invented result on a run input and bounded interval, including a complete codebook probability distribution, abstention and explicitly unvalidated calibration. It never replaces a human observation. |

The knowledge graph now connects all of these to existing sources, studies, sessions, observations and releases. Relationships include `documents`, `captured_in`, `aligns`, `uses_release`, `uses_media`, `uses_alignment`, `produces` and `predicts_on`. These describe provenance, not biological meaning. The owner interface shows their plain-language names through Research connections. Public `/research/map/` remains a projection of public catalog files only.

## Admission and lifecycle

All new write endpoints use the existing owner Google subject check, same-origin protection, CSRF token and 16 KiB JSON limit. Every input requires strict `synthetic: true`. `false` is rejected. Invented hashes and device declarations are not verified media, identity, rights or consent. A person could misdescribe metadata; this rehearsal is not a scientific admission system.

1. Create a synthetic study and linked observation through the existing workflow.
2. Before observation review, register invented audio/video descriptors using `POST /api/media`. This boundary freezes media membership when review happens.
3. Register synchronization using `POST /api/media-alignments`. Both assets must belong to the same session and still be unreviewed. The mapping is `video_ms = audio_ms * (1 + drift_ppm / 1000000) + offset_ms`; its uncertainty envelope must fit both declared media durations.
4. Review the observation and make an existing synthetic training release. Rights, privacy, independent-label and training-permission checks still apply. That release remains explicitly metadata-only; attaching descriptors does not make it an acoustic dataset.
5. Register a specification using `POST /api/model-runs`. Inputs must cover exactly the release observations; splits cover each observation once. The same declared individual cannot cross split partitions. A multimodal run must include explicit alignments for every input. This checks declared identities, not physical identity or true statistical independence.
6. Register an invented output using `POST /api/model-results`. The run, release, media and alignment fingerprints are rechecked. Intervals must fit the media and any applicable alignment validity window. Probabilities must cover the frozen codebook and sum to one. No claims of measured performance or calibration are accepted.
7. Inspect the private records through `GET /api/lineage` and `GET /api/knowledge-graph`. Responses are owner-only and no-store. The graph excludes device aliases, raw annotation notes, probability values and media payloads.

Withdrawal is one transaction: redact media and alignment payloads, invalidate dependent runs, redact their results (including results on other inputs of the same run), revoke releases and remove the observation. Graph projections omit withdrawn assets, alignments and results and remove invalidated run edges. Opaque IDs, fingerprints, dependency rows and audit tombstones remain for reconciliation. Downloads and older backups require separate deletion/revocation reconciliation. No external object exists to delete in this phase.

## Migration and recovery

Runtime refuses an old schema rather than silently upgrading it. Stop the local service and create a scrubbed recovery rehearsal before migrating an existing SQLite database:

```sh
.venv/bin/python -m admin.recovery --name pre-lineage-v2-UNIQUE-NAME
.venv/bin/python -m admin.database migrate-sqlite --database data/private/admin.sqlite3
```

Migration is transactional and idempotent. It preserves the pinned owner and all existing catalog/study/observation records. Fresh SQLite stores are initialized at v2; existing unknown schema versions and symlinks are rejected. Recovery supports the legacy and v2 table inventories and scrubs live authentication state from copied artifacts. It never activates a restore.

For PostgreSQL, `admin.database init` creates v2 for a new database. Upgrade an existing v1 schema with the schema-owner connection supplied privately in `T2N_DATABASE_URL`:

```sh
.venv/bin/python -m admin.database migrate
```

Then apply `admin/schema/grant-runtime.sql` as the schema owner and return to the restricted runtime connection. Never initialize or migrate using runtime credentials. PostgreSQL startup checks version 2, does not create tables, and uses the existing transaction advisory lock. Migration and runtime grants are tested on a fresh disposable loopback database, not a cloud database. Hosted migration/recovery remains a deployment gate.

## Verification

`admin/tests/lineage_cases.py` is inherited by the complete owner-workbench suite on both adapters. It exercises restart persistence; authentication/CSRF; modality/hash/interval validation; session pairing; post-review freezing; exact release/input membership; grouped splits; complete multimodal alignment; fingerprint tampering; result/codebook bounds; label separation; withdrawal of cross-input derivatives; and full rollback after an injected withdrawal failure. Dedicated migration tests cover retained owner/data, idempotency, unknown schemas, failed-DDL rollback and restricted PostgreSQL runtime rights. The recovery test includes withdrawn media, alignment, model input and result tombstones.

```sh
.venv/bin/python scripts/test_postgres.py
python3 -m unittest discover -s tests -v
node --test tests/*.test.mjs
python3 web/build.py
python3 scripts/check_site.py
```

## What comes next

The [discovery plan](DISCOVERY_PLAN.md) still governs the scientific program. Media object storage, signed upload grants, bytes/checksum verification, real time-series/frame timestamps, automatic identity/pose estimates, model execution, benchmark metrics, real consent and participant roles are not implemented here. Permission remains on the existing observation record; consent documents, media retention deadlines and deletion jobs need the approved real-data schema. The next hosted milestone remains a synthetic owner workspace with actual provider authentication, persistence and recovery checks. This foundation makes provenance explicit without claiming that a metadata descriptor is a recording or that a prediction is communication.
