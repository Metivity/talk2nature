import test from 'node:test';
import assert from 'node:assert/strict';
import {emptyEventsMessage, nextEventFocusId} from '../web/assets/station-review-ui.mjs';

test('empty review distinguishes active, silent-looking, discarded and storage-limited highlights', () => {
  assert.equal(emptyEventsMessage(null), 'Your first sound event will appear here.');
  assert.match(emptyEventsMessage({mode: 'events', discarded: []}, true), /does not prove silence/);
  assert.match(emptyEventsMessage({mode: 'events', discarded: []}), /does not establish that the setting was silent/);
  assert.match(emptyEventsMessage({mode: 'events', discarded: [{id: 1, onset_seconds: 4}] }), /1 clip was discarded; event IDs and timing remain/);
  assert.match(emptyEventsMessage({mode: 'events', discarded: [{id: 1, reason: 'storage_limit'}]}), /could not be kept because the local storage limit was reached/);
  assert.match(emptyEventsMessage({mode: 'window', discarded: [{id: 1, onset_seconds: null}]}), /audio was discarded/);
});

test('empty window review does not imply completeness after a stop or interruption', () => {
  assert.match(emptyEventsMessage({mode: 'window', discarded: []}, true), /will appear here when recording stops/);
  assert.match(emptyEventsMessage({mode: 'window', discarded: []}), /not a complete 30-second observation/);
});

test('keyboard discard handoff chooses the next clip, or the previous clip when the last is removed', () => {
  assert.equal(nextEventFocusId([{id: 2}, {id: 3}], 0), 2);
  assert.equal(nextEventFocusId([{id: 1}, {id: 2}], 1), 2);
  assert.equal(nextEventFocusId([], 0), null);
  assert.equal(nextEventFocusId([{id: 2}], -1), null);
});
