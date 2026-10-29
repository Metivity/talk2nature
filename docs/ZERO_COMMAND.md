# Zero-command observation rule

Talk2Nature's current observation tools listen only. They do not try to make an animal respond and do not translate animal communication. Here, **zero-command means zero output directed at animals**; it does not mean zero human controls or automatic recording. A person deliberately starts capture after the required permission and can stop it at any time. The microphone-free synthetic example is the default for practice.

## What the app may do

- Run invented sounds through the same silent capture path without requesting microphone access.
- Capture sound only after a person presses Start, grants microphone permission and acknowledges permission to record in that place. Capture remains foreground-only and locally processed.
- Let a person add observations about what they saw or heard. Unknown source, quiet, uncertainty and an incomplete session are valid.
- Let a person review a selected recording for themselves after the session. Each start or replay requires a fresh click and a confirmation that the animal cannot hear it; use headphones or move away. Cancel means no playback.

## Two capture modes

- **Browser Field Companion:** capture starts from the visible page and stops when the page is hidden, closed or interrupted. A screen wake lock, when available, is only a request to keep the display awake; it is not a promise of background capture.
- **Android Station:** after the person checks the recording and wildlife-care statement, grants Android's microphone and notification permissions, and taps Start, a microphone foreground service can continue while the app screen is away. Android shows an ongoing notification with a Stop action; the notification channel is configured without app-set sound, vibration or indicator lights. The service is not started on boot and returns `START_NOT_STICKY`, so Android will not be asked to recreate capture automatically after process death. Actual screen-lock, interruption and notification behavior still needs a named-device check.

These modes make “put the phone down” mean different things. The browser mode stops on leaving the page; the Android mode is explicitly started and remains visibly stoppable. Neither mode is an unattended recorder or sends a cue to an animal.

## What zero-command can and cannot guarantee on Android

The Android app initially creates its recording-notification channel without app-set sound, vibration or indicator lights. After a channel is created, Android lets the user change its behavior; the app cannot reset those channel settings programmatically. Android views may also provide default haptic feedback when device settings allow it. Keyboard, accessibility and other operating-system services can add their own cues. See [Android notification-channel settings](https://developer.android.com/develop/ui/compose/notifications/channels) and [Android view haptics](https://developer.android.com/develop/ui/views/haptics/haptics-apis).

Zero-command is a rule against deliberate Talk2Nature output toward animals; it is not a certification that the whole phone is silent. Do not override system or accessibility feedback as a blanket fix. During a no-animal device rehearsal, record app-controlled playback and notification behavior separately from system, keyboard, accessibility and device cues. Keep the platform marked unverified until that check is completed.

## What the observation app must not do

Do not add animal-directed calls, imitation, generated voice, automatic playback, adaptive prompts, or visual or haptic signals. Do not ask people to provoke a call, approach wildlife or change an animal's behavior to get a recording. No notification, voice assistant, TV or background process should prompt an animal or silently resume capture.

A detected sound, a sound after a human voice, a model prediction or a fluent output is not evidence of a reply, intention, meaning or translation. Predictions may help a person find material to review; keep them distinct from human observations.

Any future study of an animal-facing interface is a separate research project. It needs an independently reviewed protocol, appropriate animal-welfare oversight and a distinct implementation and release decision. It does not belong in the ordinary observation tools.

## Regression checks and limits

`node --test tests/zero-command.test.mjs tests/native-zero-command.test.mjs tests/station.test.mjs tests/station-ui.test.mjs tests/review-audio.test.mjs` guards against scripted animal-facing output, autoplay and unconfirmed playback. The Station worklet zeros all speaker channels. Station, Listen and Compare allow human review only after deliberate activation and a just-in-time confirmation. Behavior tests cover cancellation, pause, replay confirmation and browser playback rejection.

Source checks and desktop browser tests cannot establish what a physical phone, operating system, accessibility service, connected TV or native app may emit. A phone test must be a synthetic rehearsal in a place with no animal present. Record the device model, OS, browser/app revision and install mode; verify clear Start and Stop, background/page-hide behavior for the selected mode, interruption handling, no silent resume, save and reopen of the same invented session, and headphone-only manual review. Report app-controlled behavior separately from OS cues. Leave unavailable platforms marked unverified. Do not collect real animal recordings for this check.

Do not put account identifiers, personal recordings, exact locations, participant details or private OS screenshots in the public repository.
