import test from 'node:test';
import assert from 'node:assert/strict';
import {sessionLabel} from '../web/assets/session-label.mjs';

test('old built-in aliases display as readable moment names without rewriting the saved value',()=>{
  for(const [alias,label] of [
    ['my-listening-place','Listening session'],
    ['outdoor-place','Outdoor moment'],
    ['companion-place','Shared moment'],
    ['parrot-visit','Parrot visit'],
    ['rehearsal','Practice session']
  ]) assert.equal(sessionLabel(alias),label);
});

test('user-chosen session labels remain readable and empty legacy values get a safe fallback',()=>{
  assert.equal(sessionLabel('Window beside the feeder'),'Window beside the feeder');
  assert.equal(sessionLabel('  Morning notes  '),'Morning notes');
  assert.equal(sessionLabel(''),'Saved moment');
  assert.equal(sessionLabel(undefined),'Saved moment');
});
