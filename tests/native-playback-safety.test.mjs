import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';

const activity = await readFile(new URL('../native-android/app/src/main/java/org/talk2nature/station/MainActivity.java', import.meta.url), 'utf8');

test('native audio review warns against animal-directed playback and requires confirmation', () => {
  assert.ok(activity.includes('button("Review audio"'), 'the control is labeled as human review');
  assert.ok(activity.includes('play.setOnClickListener(v -> confirmHumanReviewPlayback(id))'), 'playback starts behind a confirmation');

  const start = activity.indexOf('private void confirmHumanReviewPlayback(int id)');
  const end = activity.indexOf('private void playEvent(int id)', start);
  assert.ok(start >= 0 && end > start, 'the confirmation handler is present');
  const confirmation = activity.slice(start, end);
  assert.match(confirmation, /Do not play it to an animal/);
  assert.match(confirmation, /headphones or after leaving the animal's space/);
  assert.match(confirmation, /setNegativeButton\("Cancel",null\)/);
  assert.match(confirmation, /setPositiveButton\("Play for review",\(dialog,which\)->playEvent\(id\)\)/);
});
