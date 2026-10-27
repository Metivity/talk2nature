# Talk2Nature Android Station

This is an experimental, source-only Android prototype for a user-started phone listening station. It is not an app-store release, a validated field recorder, or a translator. No Talk2Nature model is included.

## What it does

The user chooses an observer-declared animal group, optionally enters a species and station alias, selects a 1-, 4- or 8-hour limit, checks the recording and wildlife-care statement, then starts from the visible app. Android's microphone permission and a persistent foreground-service notification make capture visible; the notification has a Stop action. Capture is not started on boot.

The prototype uses a simple energy threshold to retain up to 24 short sound clips or 24 MiB of audio, plus up to 100 user-entered notes. The selected 1-, 4- or 8-hour limit uses Android's monotonic elapsed clock as well as processed audio time; non-blocking reads let the service enforce that bound even if audio frames stop arriving. It does not classify species, infer behavior or meaning, establish a reply, or play sounds to animals. Quiet periods are not saved. A phone microphone is not verified for ultrasound, underwater or vibration sensing.

Before recording, the setup screen offers the browser Field Companion's synthetic example. The button opens the practice route directly; it needs internet and does not start this Android station, request microphone access, or create a native recording.

One working session is encrypted on the phone with AES-GCM and an Android Keystore key. Android backup and device-transfer rules exclude the app's files. Users can review and manually play a selected clip, delete clips or the whole session, and export a ZIP through Android's file picker. **The exported ZIP is unencrypted.** The app tells the user this before export; review the file and destination before sharing it. The v2 ZIP is intended to open in Talk2Nature's browser Compare workflow. Exporting does not establish recording consent, sharing rights, research admission or training rights.

## Build and test

Requirements: JDK 17, Android SDK Platform 36 and Build Tools 36.0.0, with `ANDROID_HOME` or `ANDROID_SDK_ROOT` pointing to the installed SDK. The Gradle 8.14.3 wrapper distribution is checksum-pinned; Android Gradle Plugin is declared in `build.gradle`.

From the repository root:

```sh
bash native-android/scripts/test-core.sh
node --test tests/native-session.test.mjs
(cd native-android && ./gradlew --no-daemon :app:lintDebug :app:assembleDebug :app:assembleRelease)
bash native-android/scripts/check-release-boundaries.sh
```

The core test exercises the threshold detector and strict ZIP headers without Android or third-party Java libraries. The Node test exercises browser-side v2 import and scheduled-duration bounds. The public-checks workflow runs the core test, assembles both Android variants and checks the release APK for the expected permission and network/debug boundaries. A successful build checks compilation and package contents; it does not validate a phone's microphone, battery, thermal behavior, accessibility or field reliability.

To install a local debug build on a connected Android device or emulator:

```sh
adb install -r native-android/app/build/outputs/apk/debug/app-debug.apk
```

The debug variant contains a permission-protected synthetic-session fixture for maintainer QA. It is absent from release sources. Use only synthetic data in this prototype; do not use it to collect participant or field-research data.

## Evidence and limits

Maintainer QA used an API 34 emulator to check runtime permission prompts, user-visible foreground capture state, the persistent Stop action, app-private encrypted files, manual clip review/deletion, and the file-picker export path. Denying microphone or notification permission leaves recording stopped and presents a recovery dialog with a route to app settings; notification denial was verified to create no session files and did not proceed to a microphone prompt. A synthetic emulator export opened in the browser importer as one event with one note. The emulator had no usable physical microphone, so capture quality was not tested.

Not yet verified: a physical phone; device-specific microphone response; screen-lock, call, interruption or permission-revocation behavior on hardware; 1- or 8-hour operation; battery or thermal limits; first-time-user comprehension; assistive-technology use; or store requirements. Keep this prototype outside real field studies until those checks have an approved protocol and a named device. Do not enable automatic boot capture, animal playback, uploads or real-data admission as part of this prototype.

October 25, 2026 follow-up QA added Start-button state-policy and manifest-before-audio-deletion tests. The API 34 synthetic emulator walkthrough also verified consent/session gating, notification-denial recovery before microphone permission, event tombstoning and whole-session cleanup. Consent and session-state copy is stored in Android resources for future translation; the app is still English-only. Debug lint and debug/release builds succeeded with zero errors and one warning about the pinned Gradle version. No microphone permission was granted, no recording was made, and the physical-device limitations above remain open.
