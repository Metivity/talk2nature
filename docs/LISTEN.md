# Listen v0.1: inspect a recording and export observations

Listen is an open-source, browser-local WAV annotation workbench. It prepares a preliminary observation log; it does not recognize a species, infer intention, train a model or approve a dataset.

Public entry: https://metivity.github.io/talk2nature/tools/listen/

## A reproducible five-minute walkthrough

1. Choose **Try an example · no file needed**. Computer-generated tones occur at 1–2 and 4–5 seconds. They are not animal sounds.
2. Enter start `1` and end `2`. Choose `other sound`, context `unknown`, source `not observed`, confidence `clear`. Add the event. Repeat for `4`–`5` seconds.
3. Export JSON. CSV is available for spreadsheet inspection; JSON preserves the complete record and can be reopened.
4. To reopen, select the same WAV (or synthetic example), then import the JSON. Checksum, duration, sample rate, channels and declared origin must match. Edit or remove individual events as needed.
5. Run the local Python report on the export:

```sh
python3 -m talk2nature.annotations /path/to/talk2nature-labels.json
```

The checked-in fixture makes the CLI reproducible without a browser:

```sh
python3 -m talk2nature.annotations examples/annotations.synthetic.json
```

Expected: two events, two seconds of union coverage, zero seconds of independently observed context, zero overlapping pairs, and warnings for unknown context/identity and synthetic origin. This checks software behavior, not animal communication. The generated WAV is deterministic; its SHA-256 is tested against this fixture.

`--output path/to/new-report.json` writes a new report and refuses replacement. Python 3.10+ is sufficient; no scientific packages, network requests or weights are needed.

## Constraints and interpretation

- WAV only: mono/stereo PCM 16/24/32-bit or IEEE float32, 8–192 kHz, at most 120 seconds and 25 MiB. Compressed WAV, WAVE_FORMAT_EXTENSIBLE, MP3 and phone M4A are unsupported. Prepare a short permitted WAV locally using an existing audio editor.
- The waveform displays a min/max envelope across channels, preserving opposite-phase stereo. Near-full-scale samples are a level diagnostic, not quality certification. There is no segmentation, denoising, spectrogram or model prediction.
- Non-unknown context needs a declared direct observation or synchronized video source. The tool cannot verify independence or accuracy. The starter labels are not a validated species-specific codebook.
- Overlap is allowed and flagged. Coverage is the union of intervals, not their sum. It does not measure recall, reviewer agreement or biological event count.
- Use aliases. Unknown animal/session identity remains explicit and cannot support an unseen-animal generalization claim.
- Use headphones away from animals for manual review. Do not disturb animals or broadcast sounds to them. No microphone access or automatic playback is provided.

## Data handling

Audio and labels are processed in tab memory. There is no upload, browser storage, analytics or background collection. Downloads remain on the user's device. Original filenames are omitted; aliases, SHA-256, timing, labels and notes are exported. Review files before sharing: checksums and notes can still identify a recording. The host receives ordinary website requests as explained in the site privacy notice.

Unexported saved annotations or changed identifiers trigger a discard confirmation before replacement, import or clearing, plus an unload warning where supported. In-progress form text is not an event until saved. Check the download completed before closing; the tool cannot confirm where the browser saved it. Mobile systems may discard tabs without warning.

`talk2nature.annotation.v1` is distinct from the research manifest. It lacks consent approval, verified licensing, study admission and reviewed identities. There is no automatic conversion to the evaluation manifest or private database. The private server continues to reject real observations. An approved study must independently establish provenance, permissions, labels and grouping before using `talk2nature.manifest`.

Imported JSON is bounded, validated and rendered as text. CSV cells are quoted and formula-leading text escaped. Consumers should still treat files as untrusted. Origin is a declaration, not tamper-proof certification. A checksum proves equality, not ownership or consent.

## Verification

```sh
python3 -m unittest discover -s tests -v
node --test tests/demo.test.mjs tests/listen.test.mjs
python3 web/build.py
python3 scripts/check_site.py
python3 -m http.server 4173 --bind 127.0.0.1 --directory dist
```

Browser checks cover the walkthrough, invalid context, edit/remove, export/reimport, mismatched-source rejection, WAV selection, clearing and mobile overflow. Automated tests cover binary parsing, schema validation, CSV escaping and report arithmetic. Desktop and narrow viewport checks do not establish physical iOS/Android compatibility.

Next candidates: independent reviewer comparison, species-specific codebooks, existing annotation-tool interoperability and mobile audio formats. Choose from organizer interviews.

Station now saves a ZIP containing WAV clips and a separate session journal. Unzip it and select one WAV here. Keep that journal alongside any new annotations; it is not a `talk2nature.annotation.v1` import.
