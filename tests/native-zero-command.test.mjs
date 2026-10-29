import test from 'node:test';
import assert from 'node:assert/strict';
import {readdirSync, readFileSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const appSource = path.join(root, 'native-android/app/src/main/java');

function javaFiles(directory) {
  return readdirSync(directory, {withFileTypes: true}).flatMap(entry => {
    const current = path.join(directory, entry.name);
    return entry.isDirectory() ? javaFiles(current) : entry.name.endsWith('.java') ? [current] : [];
  });
}

const files = javaFiles(appSource);
const sources = files.map(file => [path.relative(appSource, file), readFileSync(file, 'utf8')]);
const allJava = sources.map(([, source]) => source).join('\n');
const service = readFileSync(path.join(appSource, 'org/talk2nature/station/CaptureService.java'), 'utf8');
const activity = readFileSync(path.join(appSource, 'org/talk2nature/station/MainActivity.java'), 'utf8');
const stationPage = readFileSync(path.join(root, 'web/templates/station.html'), 'utf8');
const manifest = readFileSync(path.join(root, 'native-android/app/src/main/AndroidManifest.xml'), 'utf8');

test('Android recording notification is explicitly silent and non-vibrating', () => {
  assert.match(service, /CHANNEL_ID = \"nature_station_recording_quiet_v1\"/);
  const channel = service.match(/NotificationChannel channel = new NotificationChannel[\s\S]*?manager\.createNotificationChannel\(channel\);/)?.[0];
  assert.ok(channel, 'recording notification channel must be configured in CaptureService');
  assert.match(channel, /NotificationManager\.IMPORTANCE_LOW/);
  assert.match(channel, /setSound\(null,\s*null\)/);
  assert.match(channel, /enableVibration\(false\)/);
  assert.match(channel, /enableLights\(false\)/);
  assert.match(channel, /setShowBadge\(false\)/);
  const notification = service.match(/Notification notification = new Notification\.Builder[\s\S]*?\.build\(\);/)?.[0];
  assert.ok(notification, 'foreground status notification must be built explicitly');
  assert.doesNotMatch(notification, /\.set(?:Sound|Vibrate|Lights)\(/);
  assert.match(notification, /\.setOnlyAlertOnce\(true\)/);
  assert.match(notification, /Stop listening/);
});

test('Android capture is user-started and cannot restart itself after system process loss', () => {
  assert.match(manifest, /<service\s+android:name="\.CaptureService"\s+android:exported="false"\s+android:foregroundServiceType="microphone"\s*\/>/);
  assert.doesNotMatch(manifest, /<receiver\b|BOOT_COMPLETED|MY_PACKAGE_REPLACED/i);
  assert.match(service, /if \(!ACTION_START\.equals\(action\) \|\| capturing\) return START_NOT_STICKY;/);
  assert.match(service, /return START_NOT_STICKY;/);
  assert.doesNotMatch(allJava, /BOOT_COMPLETED|MY_PACKAGE_REPLACED/i);
  assert.match(service, /\.addAction\([\s\S]*?"Stop listening"/);
});

test('Android audio output is limited to separately confirmed human review', () => {
  assert.doesNotMatch(allJava, /\b(?:SoundPool|ToneGenerator|TextToSpeech|Vibrator|VibratorManager)\b/);
  assert.equal((allJava.match(/new AudioTrack\(/g) || []).length, 1, 'the only native audio output is the review player');
  assert.equal((allJava.match(/\.play\(\)/g) || []).length, 1, 'audio must not start from capture or session setup');
  const confirmation = activity.match(/private void confirmHumanReviewPlayback\(int id\) \{([\s\S]*?)\n    \}/)?.[1];
  assert.ok(confirmation, 'review playback must have an explicit confirmation method');
  assert.match(confirmation, /Do not play it to an animal/);
  assert.match(confirmation, /headphones or after leaving the animal's space/);
  assert.match(confirmation, /setNegativeButton\("Cancel"/);
  assert.match(confirmation, /setPositiveButton\("Play for review",\(dialog,which\)->playEvent\(id\)\)/);
});

test('public Station copy states the quiet-notification limit without claiming hardware validation', () => {
  assert.match(stationPage, /notification is configured without sound, vibration or indicator lights/i);
  assert.match(stationPage, /hardware behavior remains unverified/i);
});

test('native welcome screen states listen-only boundaries before practice and recording setup', () => {
  const disclosure = activity.indexOf('Listen only: this app never calls, imitates or prompts animals. Listening starts only after you tap Start and grant the required permissions.');
  const practice = activity.indexOf('Try practice · no microphone');
  const setup = activity.indexOf('01   Set up your observation');
  assert.ok(disclosure >= 0, 'the first screen must disclose the listen-only rule');
  assert.ok(disclosure < practice && disclosure < setup, 'the listen-only rule must appear before practice and recording setup');
});
