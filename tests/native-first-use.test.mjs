import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';

const activity = await readFile(new URL('../native-android/app/src/main/java/org/talk2nature/station/MainActivity.java', import.meta.url), 'utf8');

test('native practice button opens the no-microphone web demo directly', () => {
  assert.match(activity, /button\("Try invented example · no microphone"/);
  assert.match(activity, /https:\/\/metivity\.github\.io\/talk2nature\/app\/station\/\?mode=demo#station-console/);
});

test('native practice handoff discloses browser and internet requirements', () => {
  assert.match(activity, /Opens an invented browser example; it uses no microphone or animal audio, needs internet, and will not start this station\./);
});
