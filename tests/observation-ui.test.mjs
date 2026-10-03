import test from 'node:test';
import assert from 'node:assert/strict';
import {addQuickObservation, sessionRecap} from '../web/assets/observation-ui.mjs';
import {WindowSession} from '../web/assets/window-model.mjs';
import {StationSession} from '../web/assets/station-model.mjs';
import {sessionFiles} from '../web/assets/station-export.mjs';

test('quick notes preserve observed time, uncertainty and human provenance in the download', async () => {
  const s = new WindowSession(8000);
  s.push(new Float32Array(800));
  addQuickObservation(s, 'movement'); addQuickObservation(s, 'uncertain');
  assert.equal(sessionRecap(s), null);
  assert.throws(() => addQuickObservation(s, 'happy'));
  assert.throws(() => addQuickObservation(s, 'toString'));
  assert.equal(s.markers.length, 2);
  s.stop();
  assert.throws(() => addQuickObservation(s, 'another_animal'));
  const files = await sessionFiles(s, 'practice', {});
  const record = JSON.parse(new TextDecoder().decode(files[0].bytes));
  assert.equal(record.markers[0].at_seconds, .1);
  assert.equal(record.markers[0].provenance, 'user-entered');
  assert.equal(record.markers[1].note, 'I am not sure what happened.');
  assert.equal(record.events[0].source_label, 'unreviewed');
  assert.match(sessionRecap(s).title, /partial/);
  assert.match(sessionRecap(s).detail, /Invented practice audio.*2 notes/);
});

test('review summary distinguishes complete, discarded, empty and threshold-selected sessions', () => {
  const full = new WindowSession(8000, {origin:'microphone'});
  for (let i=0; i<300; i++) full.push(new Float32Array(800));
  assert.equal(sessionRecap(full).title, 'A whole 30-second moment.');
  assert.match(sessionRecap(full).detail, /Microphone audio/);
  full.discard(1);
  assert.equal(sessionRecap(full).title, 'No audio retained.');
  assert.match(sessionRecap(full).detail, /discard records/);
  const empty = new StationSession(8000); empty.stop();
  assert.equal(sessionRecap(empty).title, 'No audio retained.');
  const highlights = new StationSession(8000);
  for (let i=0; i<35; i++) highlights.push(new Float32Array(800).fill(.001));
  highlights.push(new Float32Array(800).fill(.2)); highlights.stop();
  assert.match(sessionRecap(highlights).title, /sound highlight/);
  assert.doesNotMatch(sessionRecap(highlights).title, /whole|complete/);
});

test('quick observations honor the existing bounded marker limit', () => {
  const s = new WindowSession(8000);
  for (let i=0; i<100; i++) addQuickObservation(s, 'surroundings');
  assert.throws(() => addQuickObservation(s, 'movement'));
  assert.equal(s.markers.length,100);
});
