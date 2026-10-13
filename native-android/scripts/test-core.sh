#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
APP_ROOT="$REPO_ROOT/native-android/app"
TEST_CLASSES="$REPO_ROOT/native-android/build/core-test-classes"
mkdir -p "$TEST_CLASSES"
javac -d "$TEST_CLASSES" \
  "$APP_ROOT/src/main/java/org/talk2nature/station/engine/CaptureEngine.java" \
  "$APP_ROOT/src/main/java/org/talk2nature/station/SessionZip.java" \
  "$APP_ROOT/src/testCore/java/org/talk2nature/station/engine/CaptureEngineSelfTest.java"
java -cp "$TEST_CLASSES" org.talk2nature.station.engine.CaptureEngineSelfTest
