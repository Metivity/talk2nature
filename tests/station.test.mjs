import test from 'node:test';
import assert from 'node:assert/strict';
import {StationSession, wavBytes} from '../web/assets/station-model.mjs';
import {FrameAccumulator} from '../web/assets/station-capture.mjs';
import {AudioSession} from '../web/assets/station-audio.mjs';
import {readWav} from '../web/assets/listen-model.mjs';

function feed(session, seconds, value = 0) {
  for (let n = 0; n < Math.round(seconds * 10); n++) session.push(new Float32Array(session.sampleRate / 10).fill(value));
}
test('sessions have separate export identities and a declared device clock', () => {
  const one=new StationSession(8000), two=new StationSession(8000);
  assert.notEqual(one.id,two.id); assert.notEqual(one.audioFilename(1),two.audioFilename(1));
  assert.ok(Number.isFinite(Date.parse(one.exportRecord().started_at_utc)));
  assert.match(one.exportRecord().clock,/not synchronized/);
  feed(one,4); feed(one,.5,.1); one.stop();
  assert.equal(one.exportRecord().events[0].audio_filename,one.audioFilename(1));
});
test('event capture includes pre-roll, stops after quiet and exports a Listen-compatible WAV', () => {
  const s = new StationSession(16000); feed(s, 4); feed(s, .5, .1); feed(s, .6);
  assert.equal(s.events.length, 1); const event = s.events[0];
  assert.equal(event.onset_seconds, 4); assert.equal(event.clip_start_seconds, 3);
  assert.equal(event.last_loud_seconds, 4.5); assert.equal(event.ended_by, 'quiet');
  const wav = readWav(wavBytes(event.pcm, s.sampleRate)); assert.ok(wav.duration >= 2 && wav.duration <= 2.1);
  assert.ok(Math.abs(wav.peak - .1) < .001); assert.equal(s.exportRecord().events[0].source_label, 'unreviewed');
});
test('marker outcomes retain absence, incompleteness, timing, reviewed source and discard history', () => {
  const s = new StationSession(8000); feed(s, 4); s.mark('person_voice'); assert.equal(s.markerWindows()[0].outcome, 'incomplete');
  feed(s, .5); feed(s, .3, .1); feed(s, .7); assert.equal(s.markerWindows()[0].lag_seconds, .5);
  s.review(1, 'person', 'This could be the observer.'); assert.equal(s.markerWindows()[0].source_label, 'person');
  s.discard(1); assert.equal(s.bytes, 0); assert.equal(s.markerWindows()[0].outcome, 'discarded_sound');
  s.mark('person_voice'); feed(s, 10); assert.equal(s.markerWindows()[1].outcome, 'no_detected_sound');
  s.mark('person_voice'); s.stop(); assert.equal(s.markerWindows()[2].outcome, 'incomplete');
  const serialized = JSON.stringify(s.exportRecord()); assert.ok(!serialized.includes('This could be')); assert.ok(!serialized.includes('"pcm"'));
});
test('storage, time and sustained-sound clip bounds stop collection', () => {
  const quota = new StationSession(8000, {maxBytes: 100}); feed(quota, 4); feed(quota, 1, .1); feed(quota, 1);
  assert.equal(quota.stopReason, 'storage_limit'); assert.equal(quota.events.length, 0);
  const timed = new StationSession(8000); feed(timed, 305); assert.equal(timed.stopReason, 'time_limit'); assert.equal(timed.elapsed, 300);
  const long = new StationSession(8000); feed(long, 4); feed(long, 10, .1); long.stop();
  assert.ok(long.events.length >= 2); assert.ok(long.events.every(e => e.pcm.length / 8000 <= 6.11));
});
test('calibration is not reported as a fully observed quiet window', () => {
  const s = new StationSession(8000); s.mark('person_voice'); feed(s, 12);
  assert.equal(s.markerWindows()[0].outcome, 'incomplete');
});
test('an event omitted for storage limits is not misreported as a quiet marker window', () => {
  const s = new StationSession(8000,{maxBytes:100}); feed(s,4); s.mark('person_voice'); feed(s,9); feed(s,4,.1); s.stop();
  assert.equal(s.events.length,0); assert.equal(s.markerWindows()[0].outcome,'discarded_sound');
  assert.equal(s.exportRecord().discarded_events[0].reason,'storage_limit');
});
test('worklet zeros every speaker channel while retaining input frames', async () => {
  let Processor; const frames = [];
  globalThis.sampleRate = 8000;
  globalThis.AudioWorkletProcessor = class { constructor() { this.port = {postMessage: frame => frames.push(frame)}; } };
  globalThis.registerProcessor = (name, cls) => { assert.equal(name, 'station-capture'); Processor = cls; };
  try {
    await import('../web/assets/station-capture.mjs?worklet-test');
    const processor = new Processor(), outputs = [[new Float32Array(800).fill(1), new Float32Array(800).fill(1)]];
    assert.equal(processor.process([[new Float32Array(800).fill(.25)]], outputs), true);
    assert.ok(outputs.flat().every(channel => channel.every(x => x === 0)));
    assert.equal(frames.length, 1); assert.equal(frames[0][0], .25);
  } finally { delete globalThis.sampleRate; delete globalThis.AudioWorkletProcessor; delete globalThis.registerProcessor; }
});
test('bad audio and labels are rejected, stopped sessions cannot ingest or mark', () => {
  const s = new StationSession(8000); assert.throws(() => s.push(new Float32Array([NaN])));
  assert.throws(() => s.push(new Float32Array(8000))); assert.throws(() => s.mark('reply'));
  assert.throws(() => new StationSession(192000)); assert.throws(() => new StationSession(8000, {margin: 0}));
  feed(s, 4); s.stop(); const elapsed = s.elapsed; feed(s, 1, 1); assert.equal(s.elapsed, elapsed); assert.throws(() => s.mark('person_voice'));
});
test('capture accumulator handles variable render quanta without dropping/repeating samples', () => {
  const frames = [], accumulator = new FrameAccumulator(8000, frame => frames.push(frame));
  accumulator.push(Float32Array.from({length: 128}, (_, i) => i)); accumulator.push(Float32Array.from({length: 1472}, (_, i) => i + 128));
  assert.equal(frames.length, 2); assert.equal(frames[0].length, 800); assert.equal(frames[0][799], 799); assert.equal(frames[1][0], 800); assert.equal(frames[1][799], 1599);
});

function resources() {
  const track = {stops: 0, stop() { this.stops++; }, getSettings: () => ({sampleRate: 48000, deviceId: 'do-not-export'}), addEventListener() {}};
  const stream = {getTracks: () => [track], getAudioTracks: () => [track]};
  const node = {port: {}, connect() {}, disconnect() {}};
  const source = {connect() {}, disconnect() {}};
  const context = {sampleRate: 48000, state: 'running', destination: {}, audioWorklet: {addModule: async () => {}}, resume: async () => {}, createMediaStreamSource: () => source, addEventListener() {}, close: async () => { context.state = 'closed'; }};
  return {track, stream, context, node};
}
test('cancelling while microphone permission is pending stops a later-granted stream', async () => {
  const r = resources(); let grant;
  const mic = new Promise(resolve => { grant = resolve; });
  const s = new AudioSession({getMicrophone: () => mic, createContext: () => r.context, createNode: () => r.node, moduleUrl: 'fixture', onFrame() {}, onEnded() {}});
  const pending = s.start(false); s.stop(); grant(r.stream); assert.equal(await pending, null); assert.equal(r.track.stops, 1);
});
test('failed worklet initialization releases microphone and context', async () => {
  const r = resources(); r.context.audioWorklet.addModule = async () => { throw Error('module failed'); };
  const s = new AudioSession({getMicrophone: async () => r.stream, createContext: () => r.context, createNode: () => r.node, moduleUrl: 'fixture', onFrame() {}, onEnded() {}});
  await assert.rejects(s.start(false), /module failed/); assert.equal(r.track.stops, 1); assert.equal(r.context.state, 'closed');
});
test('normal capture reports allowed settings and blocks late frames after stop', async () => {
  const r = resources(); let received = 0;
  const s = new AudioSession({getMicrophone: async () => r.stream, createContext: () => r.context, createNode: () => r.node, moduleUrl: 'fixture', onFrame() { received++; }, onEnded() {}});
  const info = await s.start(false); assert.equal(info.sampleRate, 48000); assert.ok(!JSON.stringify(info).includes('do-not-export'));
  const callback = r.node.port.onmessage; callback({data: new Float32Array(128)}); assert.equal(received, 1);
  s.stop(); callback({data: new Float32Array(128)}); assert.equal(received, 1); assert.equal(r.track.stops, 1); assert.equal(r.context.state, 'closed');
});
