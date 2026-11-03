Warning: truncated output (original token count: 8160)
Total output lines: 179

# Nature Station: from encounters to shared signals

Decision and implementation record, October 1, 2026. Talk2Nature / Metivity/talk2nature. This updates the device sequence in [PHASE_TWO_PLAN.md](PHASE_TWO_PLAN.md) following Raviv's request for spare phones, encounter histories and a more ambitious learning system. The long-term vision is a distributed observatory of nonhuman communication. Only the bounded browser prototype below is implemented.

## Three connected products

1. **Nature Station:** give a spare phone a listening role. Capture permitted sound events, device quality and periods of observation. A native version should work through screen locking and temporary loss of connectivity, within explicit schedules and limits.
2. **Encounter Journal:** connect sounds to independently observed actions, a person's naturally occurring voice, timing, uncertainty and unsuccessful attempts. A useful personal journal comes before any translation claim.
3. **Signal Lab:** a later scientist-led environment for a small, voluntary exchange with a defined animal population. Distinguish understanding an animal's existing signals from teaching a new shared interface. Both are interesting; success in one does not establish the other.

The *Project Hail Mary* analogy is productive: start with shared observations, repeated patterns and tests of hypotheses. Unlike fiction, an attractive interpretation must survive alternative explanations. A system that says “I am hungry” fluently is not evidence that a recording means that.

## What works now

[Nature Station](https://metivity.github.io/talk2nature/tools/station/) is a public, local-only browser tool. No account, server call for recordings, browser persistence, trained model or admission to the private database is involved.

The device-output invariant and a separate physical-phone checklist are in [ZERO_COMMAND.md](ZERO_COMMAND.md). Passing browser checks does not verify a physical phone or its operating-system cues.

- Explicit microphone start after a recording-permission declaration and the browser's own permission. Stop cancels a pending permission request; a late-granted stream is immediately stopped.
- A silent synthetic mode runs invented tones through the same AudioContext/worklet, without opening a microphone. The worklet zeros every speaker output. Live microphone monitoring and automatic animal playback are absent.
- Three seconds of baseline estimation, then a simple level threshold. Roughly one second of pre-roll and half a second of trailing quiet surround a detected event; sustained sound is split at approximately six seconds per clip. Wind, speech and machinery can trigger it. There is no species or speech classifier.
- A five-minute foreground limit, 24-clip / 24 MiB stored-audio limits, explicit stop, and stop on hidden page, interrupted audio or missing frames. A wake lock is requested where supported, but is not a background-recording guarantee.
- Timestamped voice and observation markers on the audio sample clock. Ten-second windows report a following detected sound, none detected, an incomplete window, or a discarded sound. Calibration is not counted as a complete quiet window. A detected sound may be the observer's own voice.
- After stopping: review source labels and notes, load a clip for human review, save individual PCM16 mono WAVs, export `talk2nature.station.v1` JSON, or discard. Station loads audio into a hidden, controls-free player; its custom Play/Pause control asks for a safety confirmation immediately before every play or replay. Cancel never calls `play()`. The confirmation cannot verify headphones or distance, and an exported WAV can be played in another app. Station pauses and clears a loaded review clip when hidden or leaving the page. JSON does not embed audio. Listen can open an exported WAV for finer annotation; it does not import the Station journal.
- Discarding a clip removes its audio and review text from the session, while retaining it…6160 tokens truncated…xclusion notice, and a confirmed new session clears it. Countdown updates avoid redundant text writes and live-region chatter; recording state, marker feedback and export status are announced separately. The demo now defaults to a 30-second whole moment. The exact offline allowlist includes the new UI module. Physical devices and scientific protocols remain separate requirements.

## October 13: optional soundscape context

After capture stops, a visitor may mark broad soundscape categories they personally noticed: people or machines, other animals, weather or water, another surrounding sound, or mixed/uncertain. The optional `soundscape_context` field is scoped to the whole session and records `user-entered` provenance. It does not identify a clip, animal, signal meaning or causal response. No selection is `not_recorded`, not evidence that a category or sound was absent. Compare displays the same caution when reopening sessions. Older journals without this field remain supported; this addition does not admit observations to the research database or training.

## October 13: phone microphones are accessible sensors, not a standard

The research library now compares two primary studies: citizen-science nightingale recordings and built-in phone microphones for selected low-frequency bat calls. Both show useful, species- and task-specific applications; both also report device or recording-quality variation. In the bat study, calls near the tested 24 kHz upper limit became harder to detect with distance, and some tested phone models produced aliasing artifacts. Neither paper validates today's phones, the browser's processing chain, every animal or Talk2Nature's capture path. See the source-linked mobile-recording synthesis and its separate metadata-only paper and dataset records.

The browser Station now presents a short notice before the capture controls: phone microphones may filter or change sounds, its level meter is not calibrated, and it does not identify animals. The separate eight-second phone rehearsal remains a temporary input check, not a sensor certification. For any later scientific comparison, first test the exact phone/app path against a reference recorder for the target species and frequency band; retain device/session grouping and expert verification in a reviewed protocol. No recordings, participant intake or model training were added by this decision.

## November 3: treat the station as one stage in a sensor-to-insight workflow

Kitzes et al. (2026) describe six connected stages: hardware, field deployment, data management, AI analysis, statistical inference and ecological insight. Their review highlights that directionality, self-noise, background conditions, compression and missing recorder settings can change what later analyses appear to show. Model scores also do not automatically behave as calibrated probabilities, and feeding location or other covariates into a detector can bias later analyses that use the same variables. See the [source-linked workflow review](https://metivity.github.io/talk2nature/research/ecological-sensors-ai-workflow-kitzes-2026/).

**Design consequence, not implemented product behavior:** when a study is separately approved, a research export should preserve whatever is available about device/app version, recording settings, channels, source sample rate, format/compression, declared time and clock uncertainty, transformations and original-file checksum. Unknown values should remain explicitly unknown. Keep that provenance separate from observer notes and future model proposals. Collect only study-relevant context; expose no precise wildlife location in public outputs by default. A local provenance-rich export is the next reviewable interface for a university workflow; a central upload/database remains gated on approved protocol, rights, consent, storage and withdrawal requirements. The existing short phone check is not calibration, recorder equivalence or a field-readiness result.
