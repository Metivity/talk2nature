import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';

const activity = await readFile(new URL('../native-android/app/src/main/java/org/talk2nature/station/MainActivity.java', import.meta.url), 'utf8');
const service = await readFile(new URL('../native-android/app/src/main/java/org/talk2nature/station/CaptureService.java', import.meta.url), 'utf8');

test('native note input clears only after a confirmed service result', () => {
  assert.match(activity, /new ResultReceiver\(handler\)/);
  assert.match(activity, /putExtra\(CaptureService\.EXTRA_NOTE_RESULT,receiver\)/);
  assert.match(activity, /completeNoteRequest\(requestId,note,resultCode==CaptureService\.NOTE_SAVED,false\)/);
  assert.match(activity, /ObservationNoteDelivery\.shouldClearSubmittedText\(saved,submitted,current\)/);
  assert.match(activity, /noteField\.setError\(timedOut\s*\?/);
});

test('native service acknowledges a note only after local persistence and reports failures', () => {
  const start = service.indexOf('if (ACTION_NOTE.equals(action))');
  const end = service.indexOf('if (!ACTION_START.equals(action)', start);
  assert.ok(start >= 0 && end > start, 'note action handler is present');
  const handler = service.slice(start, end);
  const persist = handler.indexOf('addNote(intent.getStringExtra("note"))');
  const acknowledgement = handler.indexOf('receiver.send(saved ? NOTE_SAVED : NOTE_NOT_SAVED');
  assert.ok(persist >= 0 && acknowledgement > persist, 'acknowledgement follows local note persistence');
  assert.match(handler, /catch \(Exception ignored\) \{ saved = false; \}/);
  assert.match(service, /currentStore\.addMarker\(current\.marker\(note\)\)/);
});
