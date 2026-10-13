#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SDK_ROOT="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-}}"
if [[ -z "$SDK_ROOT" ]]; then
  echo "Set ANDROID_HOME or ANDROID_SDK_ROOT to the Android SDK directory." >&2
  exit 2
fi

AAPT="$SDK_ROOT/build-tools/36.0.0/aapt"
APK="$REPO_ROOT/native-android/app/build/outputs/apk/release/app-release-unsigned.apk"
if [[ ! -x "$AAPT" || ! -f "$APK" ]]; then
  echo "Build the release APK with Build Tools 36.0.0 before checking it." >&2
  exit 2
fi

permissions="$("$AAPT" dump permissions "$APK")"
manifest="$("$AAPT" dump xmltree "$APK" AndroidManifest.xml)"
for required in \
  android.permission.RECORD_AUDIO \
  android.permission.FOREGROUND_SERVICE_MICROPHONE; do
  if [[ "$permissions" != *"$required"* ]]; then
    echo "Release APK is missing required permission: $required" >&2
    exit 1
  fi
done
for forbidden in android.permission.INTERNET android.permission.DUMP; do
  if [[ "$permissions" == *"$forbidden"* ]]; then
    echo "Release APK unexpectedly includes permission: $forbidden" >&2
    exit 1
  fi
done
if [[ "$manifest" == *"DebugSessionSeedReceiver"* ]]; then
  echo "Release APK unexpectedly contains the synthetic debug receiver." >&2
  exit 1
fi
if [[ "$manifest" != *"android:allowBackup"*"0x0"* ]]; then
  echo "Release APK must disable Android backup." >&2
  exit 1
fi

echo "Release boundaries passed: microphone-only, no network/debug permissions or debug receiver, backup disabled."
