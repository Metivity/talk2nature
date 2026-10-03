# Compare moments

October 3, 2026. Public Field Companion tool at `/app/compare/`.

Open one or two original ZIP files created by Station’s **Save session**. Files are read into temporary memory on the device. A readable comparison shows declared animal context, complete/partial sampling, duration, retained/discarded audio, observer notes, with optional clock and processing details. Expand a session to read its notes and select a recording for manual playback. The example pair creates invented tones and scenes locally; no animal audio or model is involved.

This accepts both `talk2nature.station.v1` highlights and `talk2nature.observation-window.v1` whole moments. Older additive exports without animal context remain readable as unknown. Sound desk `.t2n` notebooks, annotation JSON and repacked/compressed ZIPs are different formats and remain unsupported here. Keep original downloads; closing, navigating away or reloading forgets open copies. No upload, browser media persistence, automatic playback, researcher admission or scientific result is added.

## Import and review boundaries

- Each input is limited to 27 MiB, at most 26 flat files and 26 MiB of uncompressed payload. The UI checks file size before reading. Only the original stored ZIP layout is accepted: one journal, the expected WAVs and `READ-ME.txt`. Reject compression/encryption, pathnames, duplicates, inconsistent headers, overlapping/gapped entries, extra files, trailing data and CRC failures. No archive extraction occurs.
- Journal size is limited to 256 KiB. Validate supported schemas, stopped state, origin declarations, bounded animal/observer fields, counts, timestamps relative to capture, discard identity and window completeness/sample consistency. Comparison uses explicitly selected fields; it does not endorse every optional journal field or older marker-outcome inference.
- Each retained WAV must match the generated PCM16 mono structure, journal rate, sample count and SHA-256. These checks establish consistency with the journal, not authenticity: both audio and declarations could be edited by a file’s author. Rights, consent, device identity, species identity and biological meaning remain unverified.
- A successful replacement is atomic per slot. Failed imports preserve the previous open session; stale or cancelled asynchronous loads cannot overwrite a later selection. Imported text is inserted as text, never HTML. The single player has no autoplay; replacing/closing its session revokes the object URL, hidden-page handling pauses playback, and page exit clears both sessions.
- The existing optional service worker caches only the exact public app pages and code, including this tool. It never caches user-selected ZIPs, audio, notes or runtime responses. No sign-in or private API is involved.

## Interpretation

Retained audio is a sum of file durations. Highlights may overlap, omit quieter sound and exclude calibration; this is not coverage or animal-call abundance. Discarded recordings are visibly absent, never counted as silence. Complete windows mean the specified number of processed samples was retained, not complete physical observation or unbiased sampling.

Warnings identify duplicate session IDs, different modes, durations, animal declarations, processing/detector settings, mixed synthetic/microphone origin, incomplete windows and discards. Even matching settings do not establish matching microphones, distance, surroundings or sampling. The tool makes no rate, biological-change, reply, causal or translation claim.

## Verification and next work

`node --test tests/compare.test.mjs` covers both schemas, old context-free exports, complete/partial/empty/discarded windows, malformed ZIPs, hashes, WAV/sample disagreement, forged completeness, observation bounds, comparison warnings and asynchronous replacement. A small DOM harness exercises the real file-change handler, literal untrusted notes, failed replacement preservation, manual-player preparation and page-exit cleanup. The existing mobile tests check public-shell cache boundaries; Python site tests require the comparison page/module in the allowlist.

Browser release checks cover mobile/desktop composition, the example pair, an actual prior browser-saved ZIP import, no autoplay, close/replacement behavior and offline use. Physical Android/iPhone file selection, real microphone fidelity and first-time participant usability remain subsequent checks. Detailed release receipts belong in `MOBILE_AUDIT.md` and `STATUS.md`.
