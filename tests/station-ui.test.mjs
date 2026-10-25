import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {webcrypto} from 'node:crypto';
import {animalPicker} from '../web/assets/animal-picker.mjs';
import {addQuickObservation, sessionRecap} from '../web/assets/observation-ui.mjs';
import {WindowSession, WINDOW_SECONDS} from '../web/assets/window-model.mjs';
import {stationPreset} from '../web/assets/station-preset.mjs';
import {StationSession, SOURCE_LABELS, wavBytes} from '../web/assets/station-model.mjs';
import {sessionFiles, zipFiles} from '../web/assets/station-export.mjs';
import {openSessionBundle, sessionSummary} from '../web/assets/session-import.mjs';
import {emptyEventsMessage, nextEventFocusId} from '../web/assets/station-review-ui.mjs';

function setup() {
  const elements = new Map();
  const state = {confirm: false, confirmations: 0, capture: null, downloads: [], objectUrls: new Map()};
  let document;
  const canvasContext = {scale() {}, beginPath() {}, moveTo() {}, lineTo() {}, stroke() {}, setLineDash() {}};

  function element(id = '') {
    return {
      id, value: id === 'station-capture-mode' ? 'events' : id === 'station-alias' ? 'practice station' : id === 'station-animal-group' ? 'unknown' : id === 'station-margin' ? '12' : '',
      _text: '', get textContent() { return this._text; }, set textContent(value) { this._text = String(value); },
      hidden: false, open: false, disabled: false, checked: false, readOnly: false,
      dataset: {}, children: [], handlers: {}, clientWidth: 320, clientHeight: 80,
      classList: {toggle() {}, add() {}, remove() {}},
      addEventListener(name, handler) { this.handlers[name] = handler; },
      async fire(name, event = {}) { return await this.handlers[name]?.(event); },
      click() {
        if (this.download) state.downloads.push({name: this.download, blob: state.objectUrls.get(this.href)});
      },
      append(...nodes) { this.children.push(...nodes); },
      replaceChildren(...nodes) { this.children = nodes; },
      setAttribute(name, value) { (this.attributes ??= {})[name] = value; },
      removeAttribute(name) { delete this.attributes?.[name]; },
      pause() {}, load() {}, remove() {}, scrollIntoView() {},
      focus() { document.activeElement = this; },
      matches(selector) { return selector === '[data-observation]' && Boolean(this.dataset.observation); },
      getContext() { return canvasContext; }
    };
  }
  const get = id => {
    if (!elements.has(id)) elements.set(id, element(id));
    return elements.get(id);
  };
  const steps = ['setup', 'recording', 'review'].map(step => Object.assign(element(), {dataset: {step}}));
  const observations = ['movement', 'another_animal', 'surroundings', 'uncertain'].map(observation => Object.assign(element(), {dataset: {observation}}));
  document = {
    activeElement: null, hidden: false, body: get('body'), getElementById: get,
    createElement: () => element(),
    addEventListener() {},
    querySelectorAll(selector) {
      if (selector === '[data-step]') return steps;
      if (selector === '[data-observation]') return observations;
      return [];
    }
  };
  const window = {
    devicePixelRatio: 1, AudioContext: function AudioContext() {}, AudioWorkletNode: function AudioWorkletNode() {},
    confirm() { state.confirmations++; return state.confirm; },
    addEventListener() {}
  };
  class TestURL extends URL {}
  TestURL.createObjectURL = blob => {
    const url = `blob:station-test/${state.objectUrls.size}`;
    state.objectUrls.set(url, blob);
    return url;
  };
  TestURL.revokeObjectURL = url => state.objectUrls.delete(url);
  class SyntheticAudioSession {
    constructor(options) { this.options = options; this.stopped = 0; state.capture = this; }
    async start(synthetic) {
      this.synthetic = synthetic;
      if (!synthetic) throw new Error('This test must never request microphone capture.');
      return {sampleRate: 8000, settings: {auto_gain_control: false, noise_suppression: false, echo_cancellation: false}};
    }
    frame(samples) { this.options.onFrame(samples); }
    stop() { this.stopped++; }
  }
  const source = fs.readFileSync(new URL('../web/assets/station.js', import.meta.url), 'utf8')
    .replace(/^import .*;\n/gm, '')
    .replaceAll('import.meta.url', '"https://talk2nature.test/assets/station.js"');
  vm.runInNewContext(source, {
    addQuickObservation, sessionRecap, WindowSession, WINDOW_SECONDS, animalPicker, stationPreset,
    StationSession, wavBytes, SOURCE_LABELS, sessionFiles, zipFiles, AudioSession: SyntheticAudioSession,
    emptyEventsMessage, nextEventFocusId, document, window, navigator: {},
    location: {href: 'https://talk2nature.test/app/station/?mode=companion#station-console'},
    URL: TestURL, Blob, crypto: webcrypto, performance: {now: () => 1000},
    setTimeout: () => 1, clearTimeout() {}, setInterval: () => 2, clearInterval() {}
  });
  return {get, observations, state};
}

test('companion rehearsal stays microphone-free and discard returns a marked review to Ready', async () => {
  const h = setup();
  assert.equal(h.get('station-capture-mode').value, 'window');
  assert.equal(h.get('station-animal-group').value, 'unknown');
  assert.equal(h.get('station-permission').checked, false);
  assert.equal(h.get('station-start').disabled, true);
  assert.equal(h.get('station-demo').disabled, false);

  await h.get('station-demo').fire('click');
  assert.equal(h.state.capture.synthetic, true);
  assert.equal(h.get('station-console').dataset.phase, 'recording', h.get('station-status').textContent);
  h.state.capture.frame(new Float32Array(800).fill(0.04));
  await h.observations[0].fire('click');
  await h.get('station-stop').fire('click');
  assert.equal(h.get('station-console').dataset.phase, 'review', h.get('station-status').textContent);
  assert.match(h.get('station-recap-detail').textContent, /Invented practice audio/);
  assert.equal(h.get('station-event-total').textContent, '1');
  assert.equal(h.get('station-markers').children.length, 1);

  await h.get('station-bundle').fire('click');
  assert.equal(h.state.downloads.length, 1);
  const saved = h.state.downloads[0];
  assert.match(saved.name, /^talk2nature-[0-9a-f-]+\.zip$/);
  assert.equal(saved.blob.type, 'application/zip');
  assert.match(h.get('station-save-status').textContent, /download requested/);
  const reopened = await openSessionBundle(await saved.blob.arrayBuffer());
  assert.equal(sessionSummary(reopened).kind, 'Whole moment · partial');
  assert.equal(reopened.record.origin, 'synthetic');
  assert.equal(reopened.record.animal_context.group, 'unknown');
  assert.equal(reopened.record.markers[0].kind, 'observation');
  assert.equal(reopened.clips.length, 1);

  await h.get('station-clear').fire('click');
  assert.equal(h.state.confirmations, 1);
  assert.equal(h.get('station-console').dataset.phase, 'review');
  assert.equal(h.get('station-markers').children.length, 1);

  h.state.confirm = true;
  await h.get('station-clear').fire('click');
  assert.equal(h.state.confirmations, 2);
  assert.equal(h.state.capture.stopped, 1);
  assert.equal(h.get('station-console').dataset.phase, 'setup');
  assert.equal(h.get('station-state').textContent, 'Ready');
  assert.equal(h.get('station-status').textContent, 'Ready for a new moment. Nothing is recording.');
  assert.equal(h.get('station-event-total').textContent, '0');
  assert.equal(h.get('station-memory').textContent, '0.0 MB');
  assert.equal(h.get('station-recap').hidden, true);
  assert.equal(h.get('station-markers').children.length, 0);
  assert.equal(h.get('station-events').children.length, 1);
  assert.equal(h.get('station-save-status').hidden, true);
  assert.equal(h.get('station-save-ack').hidden, true);
  assert.equal(h.get('station-player').hidden, true);
  assert.equal(h.get('station-permission').checked, false);
  assert.equal(h.get('station-start').disabled, true);
});
