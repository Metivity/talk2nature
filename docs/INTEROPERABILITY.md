# Research annotation interoperability: AOEF export

Status: experimental, local-only, one-way export. Synthetic Whombat 0.9.0 UI interoperability verified October 13, 2026; scientific suitability and real recordings remain unreviewed.

## Decision

Talk2Nature now offers an optional advanced export in Listen using [Audio Object Exchange Format (AOEF) 1.1.0](https://mbsantiago.github.io/soundevent/generated/gallery/1_saving_and_loading/). This is a small bridge to an existing research workflow, not a second annotation application. The [Whombat dataset guide](https://mbsantiago.github.io/whombat/user_guide/datasets/) documents the AOEF dataset plus audio-directory inputs, and its [import guide](https://mbsantiago.github.io/whombat/user_guide/guides/import/) says to load the dataset first, then the annotation project. The [annotation-project guide](https://mbsantiago.github.io/whombat/user_guide/annotation_projects/) describes the corresponding human annotation structure. That order is included in the package instructions.

The generated package was loaded with the pinned [soundevent 2.10.0 library](https://pypi.org/project/soundevent/2.10.0/) and imported through the Whombat 0.9.0 desktop UI using an invented eight-second WAV. In Python 3.12.5 on macOS 26.4, the importer created one recording, two timed sound events, two human annotations, two notes, one task and four project tags. The project page showed all four tags associated with both sound events, and the annotation view loaded the recording. The imported annotation records had no creator ID. The resolved core test stack was FastAPI 0.112.2, fastapi-users 12.1.3, Starlette 0.38.6 and SQLAlchemy 2.0.54. This is a format-compatibility check only; keep the feature experimental until an independent specialist reviews the mapping.

## What the package contains

The downloadable ZIP contains `recording.wav`, `dataset.aoef.json`, `annotation-project.aoef.json`, `talk2nature-annotations.json`, `export-report.json`, and `READ-ME.txt`. The WAV bytes remain unchanged. The AOEF recording points to the relative filename `recording.wav` and carries its checksum, duration, channel count, and sample rate.

| Talk2Nature record | AOEF representation | Limit |
| --- | --- | --- |
| Timed sound event | `SoundEvent` with a `TimeInterval` in seconds | The event is an observer annotation, not a detected or translated message. |
| Kind, context, context source and confidence | Namespaced `talk2nature.*` tags on a human `SoundEventAnnotation`; the annotation project also lists those IDs in `project_tags` | These are user-entered values, not model outputs or validated biological labels. `unknown` remains explicit. |
| Observation note | AOEF note attached to that annotation | Notes can reveal identities or sensitive details. |
| Recording, session, individual and annotator IDs; declared animal context; Station journal | Preserved in the Talk2Nature JSON sidecar | These do not become AOEF identity fields. The sidecar may contain aliases, timestamps, location details or notes. |
| Model predictions | Not included | Predictions stay separate from human annotations; no model runs here. |

`export-report.json` maps each Talk2Nature event ID to generated AOEF object IDs. Keep the original `.t2n` notebook: export edits cannot be imported back into Talk2Nature, and the sidecar remains the source record. The full ZIP is unencrypted, so inspect every file before sharing. The AOEF records omit creator names, usernames and email fields; the Talk2Nature sidecar still retains the original metadata.

## Synthetic verification

The version-pinned Whombat wheel's local SHA-256 matched the value published by PyPI. Using invented tones and labels, `soundevent 2.10.0` loaded both exported files and preserved the relative WAV reference, checksum, interval coordinates, tags, notes and anonymous creator state. The exact export from the current code then passed the Whombat 0.9.0 UI flow: import dataset, then annotation project. The app reported one recording, and the project view showed four tags, each used by two sound events. A database inspection confirmed intervals `[1, 2]` and `[4, 5]`, both notes, the matching WAV checksum and null `created_by_id` values. The test user and all test data were synthetic and confined to a temporary local SQLite database. No biological or participant data were used, and no third-party library is bundled in the application or its runtime dependencies. The temporary Whombat wheel, environment, database and screenshots were removed after verification.

Whombat checks whether recording paths stay under its configured audio root. Use the same canonical absolute path for the configured root and the selected package directory. On macOS, `/tmp` may resolve to `/private/tmp`; inconsistent aliases caused one import to skip the recording and another to fail. The successful run used the canonical path. The app import page lets the user choose the dataset audio directory; importing the annotation project then uses the configured audio root.

The official [Whombat evaluation guide](https://mbsantiago.github.io/whombat/user_guide/evaluation/) distinguishes machine predictions from annotations; the [installation guide](https://mbsantiago.github.io/whombat/user_guide/installation/) warns that exported records may include user identity. Those details informed this mapping and the privacy warning. Article, Whombat code, soundevent code, dependencies, media and model assets each have separate rights. This implementation imports no Whombat or soundevent code.

## Remaining acceptance check

Have a bioacoustics or research-software specialist assess the field mapping before recommending it for a study. Other Whombat and dependency versions, mobile behavior, real recordings, study admission and scientific label quality remain unverified. Do not admit recordings to a research database or treat labels as evidence of animal meaning.

## Separate team-annotation option: Praat++

[Praat++](../praatplusplus-annotation-tool-2026/) is a current external option for teams that need synchronized audio/video annotation, multiple human label tiers and TextGrid import/export. Its source repository declares MIT at the reviewed commit. This is complementary to the Field Companion's passive capture and provenance path; it is not integrated or hosted by Talk2Nature.

The ACL 2026 paper describes a feature-comparison evaluation, not a controlled user study. No independent performance, mobile, privacy, security, backup or deletion review was found. Its optional PANNs pre-annotation produces editable generic sound-event candidates; the paper says the selected tier is overwritten when candidates are written. A future comparison should use a copy of invented media, confirm saved-work recovery and TextGrid round-trip, and avoid any real recording until the institution reviews storage, access, retention, withdrawal and all component licenses. No integration or team demand is established.
