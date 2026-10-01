import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {readWav, syntheticWav, validateDocument, eventCsv} from '../web/assets/listen-model.mjs';

const fixture = () => JSON.parse(readFileSync(new URL('../examples/annotations.synthetic.json', import.meta.url)));
test('synthetic WAV has exact time, levels and matching fixture provenance', () => {
  const buffer = syntheticWav(), audio = readWav(buffer);
  assert.equal(audio.duration, 8); assert.equal(audio.sample_rate, 16000);
  assert.equal(audio.peak, 4500 / 32768); assert.equal(audio.near_full_scale_fraction, 0);
  assert.equal(createHash('sha256').update(new Uint8Array(buffer)).digest('hex'), fixture().recording.sha256);
});
test('reject corrupt, unsupported and misleading WAV layouts', () => {
  for (const [offset, value, size] of [[4, 0, 4], [20, 2, 2], [22, 30, 2], [28, 123, 4], [40, 123, 4]]) {
    const buffer = syntheticWav(), v = new DataView(buffer);
    size === 4 ? v.setUint32(offset, value, true) : v.setUint16(offset, value, true);
    assert.throws(() => readWav(buffer));
  }
  assert.throws(() => readWav(syntheticWav().slice(0, -8)));
});
test('stereo envelope retains opposite-phase channels', () => {
  const b = syntheticWav(), v = new DataView(b);
  v.setUint16(22, 2, true); v.setUint32(28, 64000, true); v.setUint16(32, 4, true);
  for (let p = 44; p < b.byteLength; p += 4) { v.setInt16(p, 10000, true); v.setInt16(p + 2, -10000, true); }
  const info = readWav(b);
  assert.equal(info.duration, 4); assert.ok(info.bins.every(([lo, hi]) => lo < 0 && hi > 0));
});
test('PCM24/32 and float32 retain signed extremes; float NaN is refused', () => {
  for (const [code, bits] of [[1, 24], [1, 32], [3, 32]]) {
    const bytes = bits / 8, buffer = new ArrayBuffer(44 + bytes * 2), v = new DataView(buffer);
    new Uint8Array(buffer, 0, 44).set(new Uint8Array(syntheticWav(), 0, 44));
    v.setUint32(4, buffer.byteLength - 8, true); v.setUint16(20, code, true); v.setUint32(28, 16000 * bytes, true); v.setUint16(32, bytes, true); v.setUint16(34, bits, true); v.setUint32(40, bytes * 2, true);
    if (bits === 24) { v.setUint8(46, 128); v.setUint8(49, 64); }
    else if (code === 1) { v.setInt32(44, -2147483648, true); v.setInt32(48, 1073741824, true); }
    else { v.setFloat32(44, -1, true); v.setFloat32(48, .5, true); }
    const info = readWav(buffer); assert.equal(info.peak, 1); assert.equal(info.near_full_scale_fraction, .5);
    assert.equal(info.bins[0][0], -1); assert.equal(info.bins[1][1], .5);
    if (code === 3) { v.setFloat32(44, NaN, true); assert.throws(() => readWav(buffer), /non-finite/); }
  }
});
test('excess duration and file size are rejected before sample analysis', () => {
  const buffer = new ArrayBuffer(44 + 8000 * 121 * 2), v = new DataView(buffer);
  new Uint8Array(buffer, 0, 44).set(new Uint8Array(syntheticWav(), 0, 44));
  v.setUint32(4, buffer.byteLength - 8, true); v.setUint32(24, 8000, true); v.setUint32(28, 16000, true); v.setUint32(40, buffer.byteLength - 44, true);
  assert.throws(() => readWav(buffer), /120 seconds/);
  assert.throws(() => readWav(new ArrayBuffer(25 * 1024 * 1024 + 1)), /25 MB/);
});
test('fixture is valid; unrelated audio or origin cannot inherit its labels', () => {
  const d = fixture(); validateDocument(d, d.recording);
  assert.throws(() => validateDocument(d, {...d.recording, sha256: '0'.repeat(64)}), /match/);
  assert.throws(() => validateDocument(d, {...d.recording, origin: 'user-supplied'}), /match/);
});
test('reject invalid intervals, unsupported context and duplicate IDs', () => {
  for (const patch of [{start_seconds: -1}, {end_seconds: 9}, {end_seconds: 1}, {end_seconds: NaN}, {context: 'feeding'}, {context_source: 'AI'}, {notes: 'x'.repeat(501)}]) {
    const d = fixture(); Object.assign(d.events[0], patch); assert.throws(() => validateDocument(d));
  }
  const d = fixture(); d.events.push({...d.events[0]}); assert.throws(() => validateDocument(d));
});
test('CSV quotes multiline content and guards spreadsheet formulas', () => {
  const d = fixture(); d.recording.recording_id = '=1+1'; d.events[0].notes = '  @SUM(1,2)\n"quoted"';
  const csv = eventCsv(d); assert.ok(csv.includes('"\'=1+1"')); assert.ok(csv.includes("'  @SUM")); assert.ok(csv.includes('""quoted""'));
});
