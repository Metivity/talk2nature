import test from 'node:test';
import assert from 'node:assert/strict';
import {initialState, transition} from '../web/assets/demo-model.mjs';

const checks = {rights: true, consent: true, privacy: true, label: true};
const submit = (state = initialState(), overrides = {}) => transition(state, {
  type: 'submit', behavior: 'moving', review: true, training: true, ...overrides,
});
const accept = state => transition(state, {type: 'accept', checks});

test('release requires review, all checks and separate training permission', () => {
  assert.throws(() => submit(initialState(), {review: false}));
  const queued = submit(initialState(), {training: false});
  assert.throws(() => transition(queued, {type: 'release'}));
  for (const key of Object.keys(checks)) {
    assert.throws(() => transition(queued, {type: 'accept', checks: {...checks, [key]: false}}));
  }
  const accepted = accept(queued);
  assert.throws(() => transition(accepted, {type: 'release'}));
  assert.equal(accepted.observation.training, false);
  assert.equal(accepted.observation.publication, false);
});

test('unknown and unsupported labels cannot pass acceptance even with every check', () => {
  for (const [scene, behavior] of [['visible', 'feeding'], ['visible', 'unknown'], ['hidden', 'moving'], ['hidden', 'unknown']]) {
    const state = transition(initialState(), {type: 'scene', scene});
    const queued = submit(state, {behavior});
    assert.throws(() => accept(queued));
    const rejected = transition(queued, {type: 'reject'});
    assert.throws(() => transition(rejected, {type: 'release'}));
  }
});

test('withdrawal removes the observation and revokes a dependent release', () => {
  const accepted = accept(submit());
  const released = transition(accepted, {type: 'release'});
  assert.equal(released.release, 'available');
  assert.throws(() => transition(released, {type: 'release'}));
  const withdrawn = transition(released, {type: 'withdraw'});
  assert.equal(withdrawn.observation, null);
  assert.equal(withdrawn.release, 'revoked');
  assert.throws(() => transition(withdrawn, {type: 'release'}));
  assert.throws(() => accept(withdrawn));
  assert.deepEqual(transition(withdrawn, {type: 'reset'}), initialState());
});

test('queued evidence cannot be relabeled or moved to another scene', () => {
  const state = initialState();
  const queued = submit(state);
  assert.equal(state.observation, null);
  assert.throws(() => submit(queued, {behavior: 'feeding'}));
  assert.throws(() => transition(queued, {type: 'scene', scene: 'hidden'}));
  assert.throws(() => submit(initialState(), {behavior: 'happy'}));
  assert.throws(() => submit(initialState(), {training: 'true'}));
  assert.equal(transition(queued, {type: 'withdraw'}).release, 'none');
});
