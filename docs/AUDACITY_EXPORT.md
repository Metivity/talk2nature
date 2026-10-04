# Continue an observation in Audacity

October 5, 2026. A local, one-way export from [Sound desk](https://metivity.github.io/talk2nature/app/review/) and [Listen](https://metivity.github.io/talk2nature/tools/listen/). This is an interoperability prototype for external evaluation, not evidence of researcher adoption or biological validation.

## Workflow

1. Open a permitted WAV or Talk2Nature notebook. For practice, choose **Try an example**; its tones are invented.
2. Add one or more events. Keep context unknown if it was not independently observed. Add or discard unfinished drafts before export.
3. Under **Your notebook**, expand **Continue in Audacity** and choose **Download Audacity package**. Check the download completed, then unzip it locally.
4. Open `recording.wav` in Audacity. Use **File → Import → Labels**, or the label editor's Import command, to open `labels.txt`. Menu names may differ by version. Do not trim, resample or shift the audio before comparing label alignment.
5. Inspect the labels against the sound. Playback is manual; use headphones away from animals. Keep the complete package and original notebook.

The default **Save notebook** remains the way to reopen work in Talk2Nature. This Audacity ZIP is neither a Station session nor a notebook. Changes in Audacity do not update the saved Talk2Nature observations; Audacity-label reimport is not supported. Keep any original Station journal alongside this package because a single WAV does not contain that session's sampling history.

## What travels, and what changes

| File | Content and limits |
| --- | --- |
| `recording.wav` | Original bytes, including both channels if present. Hash, sample rate, channel count and duration must match the annotation record before export. |
| `labels.txt` | UTF-8, three tab-separated columns: start seconds, end seconds, display text. Stable event IDs map rows to the original record. Overlapping intervals remain overlapping. |
| `annotations.json` | Complete validated original annotation document, including exact numeric times, notes, declared animal context when present and recording aliases. This is preliminary metadata, not a research-admission manifest. |
| `export-report.json` | Source hash, declared origin, row-to-event mapping, maximum time-rounding error and conversion limits. |
| `READ-ME.txt` | Import steps, privacy and interpretation guidance. |

Label times use six decimal places. Sub-microsecond intervals that collapse to a point at that precision are rejected. Six digits do not mean the device or annotation is accurate to a microsecond. The report quantifies formatting error only; exact original values stay in the JSON sidecar.

Label text includes declared origin, event kind, context, observation source and confidence. Notes are quoted using JSON string escapes, so embedded tabs, newlines and control characters cannot create fake rows. Ordinary Unicode text is retained. These fields are readable text in Audacity, not a structured codebook or channel/frequency annotation. There is no automatic species identity, caller assignment, frequency measurement, translation or verified consent.

The export snapshots audio and notes before asynchronous hashing. Replacing or clearing a session cancels its pending download. Errors preserve the open notebook and requested downloads never clear the unsaved-work warning. Audio remains subject to Listen's 120-second / 25 MiB bounds; metadata is limited to 2 MiB and the combined package payload to 26 MiB. An unusually large combination is rejected with guidance to keep the original notebook.

Everything is assembled on the device. No upload, browser media storage or automatic playback occurs. The unencrypted download can contain private speech or identifying notes; inspect it before sharing. A matching hash establishes equality, not ownership or research permission. Optional app offline setup includes the export module, never the exported package or user media.

## Format basis and verification scope

The adapter follows Audacity's documented [standard label format](https://manual.audacityteam.org/man/importing_and_exporting_labels.html), reviewed October 5, 2026. It does not emit the optional spectral extension. Audacity is a separate project, not a Talk2Nature partner. Desktop app import/export verification is recorded separately in STATUS.md; tests of our formatter alone do not establish native compatibility across versions.

Automated checks cover UTF-8 and control-character handling, overlapping events, row mapping, timing rounding/collapse, unmodified WAV bytes, metadata preservation, source mismatch, bounded metadata, asynchronous snapshots, draft protection, failed exports and cancellation after clearing. The existing ZIP writer and app offline tests remain in use. Release browser checks exercise an actual package download, mobile layout and offline operation. The intended next external check is a researcher's own permitted workflow and chosen Audacity version; no adoption claim is made.
