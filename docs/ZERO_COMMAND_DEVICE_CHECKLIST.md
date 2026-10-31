# Zero Command device acceptance checklist

**Status:** prepared for maintainer/device review; no physical-device run is claimed by this document. It is a software and welfare rehearsal, not an animal study or permission to recruit participants.

## Record the run

- Date and local build/release commit:
- Device model and OS version:
- Mode: browser tab / installed web app / native Android:
- Browser or app version:
- Screen-reader and keyboard setup, if reviewed:
- Reviewer role (maintainer or authorized reviewer; no personal identity in the public report):

Use only a private place with no animals and no bystanders. Do not play calls, imitation or other animal audio. Use the invented example for save/reopen checks. If testing the live microphone path, get permission from anyone who could be audible, keep the capture brief and local, and delete the test session and exported file after the checks. Do not upload recordings or keep screenshots that expose accounts, people, locations or permission settings.

Record only pass, fail, not run, or not applicable, with a short non-identifying note. Keep detailed device notes private; publish only the revision, device/browser family, outcomes and a summarized defect without personal or location data.

## Common first-use and playback checks

| Check | Expected result | Result / note |
| --- | --- | --- |
| Open the Field Companion or Android Station | The invented, microphone-free example is easy to find; opening the app does not start capture or request the microphone. | |
| Start the invented example | It is identified as invented practice material, not an animal recording. No permission prompt, animal-directed sound, automatic playback, upload or persistent research record occurs. | |
| Stop and review | Stop is visible during the session; completion opens review. The example remains clearly distinct from a real observation. | |
| Cancel a playback confirmation | No playback starts. | |
| Confirm human review | Playback requires a fresh action and confirmation; use headphones or a place far from animals. No automatic or repeated playback occurs. Record any app-controlled sound separately from OS/accessibility cues. | |
| Save and reopen | Save the invented session, open the same file in Compare, confirm its invented status and discard it afterward. No JSON editing or archive extraction is required. | |
| Keyboard / assistive technology | Controls have names and visible focus; startup waits and errors are announced without losing the ability to stop or recover. Record the actual keyboard, VoiceOver or TalkBack setup; mark untested modes not run. | |

## Browser Field Companion

Run in Safari on iPhone and Chrome on Android separately when available. An installed web app and a normal browser tab are separate runs.

| Check | Expected result | Result / note |
| --- | --- | --- |
| Before permission | The permission statement is visible, the checkbox is unchecked and Start is disabled. The invented example remains available without permission. | |
| Deny or cancel microphone permission | No session or recording is created. The page explains the outcome and returns to a usable Ready state. | |
| Grant permission and deliberately Start | The browser's permission prompt follows the person's Start action. Focus moves to the visible Stop control while startup is pending; capture status is visible. | |
| Stop | Stop works promptly and review begins; no new capture starts by itself. | |
| Hide, lock or interrupt the page | Capture ends according to the browser's foreground-only rule. Returning to the page does not silently resume. Record the trigger and resulting state. | |
| Browser reload / close | No recording resumes. Unsaved local material is not represented as uploaded or preserved. | |

Do not treat a browser tab becoming inactive as a valid background-recording test; the browser mode is expected to stop when hidden or interrupted.

## Native Android Station

Use the exact debug build/source revision under review. The source-only prototype is not a store release.

| Check | Expected result | Result / note |
| --- | --- | --- |
| Before permission | Start is unavailable until the person accepts the recording/wildlife-care statement and Android permissions are granted. The invented example does not start native capture. | |
| Deny notification permission | Capture does not start and no session file is created; recovery is clear. | |
| Deny microphone permission | Capture does not start and no session file is created; recovery is clear. | |
| Deliberately Start with required permissions | A foreground service starts only after Start, with a visible ongoing notification and Stop action. Record app-controlled notification cues separately from Android settings. | |
| Leave the screen / lock device | Capture behavior matches the native mode disclosure; the ongoing notification remains visible and usable. This differs from browser mode. | |
| Stop from app and notification | Both Stop routes end capture. The service does not silently resume after interruption or process loss. | |
| Reboot / reopen | Capture does not start on boot or app launch. | |
| Export and reopen invented fixture | The ZIP opens in the browser Compare flow and is identified as invented. Delete the unencrypted export after checking it. | |

## Report and decision

Keep separate rows for iPhone/Safari, Android/Chrome, installed web app and native Android; do not generalize one result to another. For each row, record the tested commit and whether the result is physical-device, emulator, desktop emulation or source-only. A missing device or assistive technology is **not run**, not pass.

Any unexpected capture, silent restart, loss of Stop, automatic playback, unclear invented-data label, or app-controlled cue directed toward animals is a fail: stop the run, preserve only a non-sensitive description, and open a focused issue before field use. OS, keyboard and accessibility cues should be documented separately; do not disable them broadly to make a test pass.

After a run, update the Zero Command section in [`GOAL.md`](GOAL.md) and the evidence log in [`STATUS.md`](STATUS.md). Do not claim physical-device acceptance from this checklist alone; the completed run and its evidence are required. Keep animal-data admission and AutoResearch gates unchanged.
