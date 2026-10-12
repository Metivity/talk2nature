import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {DEVICE_CHECK_SECONDS, DeviceCheckMeter} from '../web/assets/device-check-model.mjs';

test('phone check keeps aggregate readings and completes at the fixed sample count', () => {
  const meter = new DeviceCheckMeter(8000);
  assert.equal(DEVICE_CHECK_SECONDS, 8);
  const frame = new Float32Array(800).fill(.5);
  for (let i = 0; i < 80; i++) meter.push(frame);
  const result = meter.snapshot();
  assert.equal(meter.finished, true);
  assert.equal(result.processed_samples, 64000);
  assert.equal(result.duration_seconds, 8);
  assert.ok(Math.abs(result.average_level_dbfs - -6.02) < .02);
  assert.ok(Math.abs(result.peak_level_dbfs - -6.02) < .02);
  assert.equal(result.near_full_scale_fraction, 0);
  assert.equal(Object.hasOwn(meter, 'frames'), false);
  assert.equal(Object.keys(result).some(key => /audio|device|location|timestamp/i.test(key)), false);
});

test('near-maximum samples are counted without keeping their frame', () => {
  const meter = new DeviceCheckMeter(8000);
  meter.push(Float32Array.from([0, .25, .999, -1]));
  const result = meter.finish();
  assert.equal(result.processed_samples, 4);
  assert.equal(result.near_full_scale_fraction, .5);
  assert.equal(result.peak_level_dbfs, 0);
  assert.equal(Object.keys(meter).sort().join(','), 'finished,limit,nearFullScale,peak,sampleRate,samples,squares');
});

test('phone check input is bounded, rejects malformed frames, and ignores data after completion', () => {
  assert.throws(() => new DeviceCheckMeter(7999), /Unsupported/);
  const meter = new DeviceCheckMeter(8000);
  assert.throws(() => meter.push([0, 1]), /finite microphone frame/);
  assert.throws(() => meter.push(Float32Array.from([0, Number.NaN])), /finite/);
  assert.throws(() => meter.push(new Float32Array(1601)), /200 ms/);
  const full = new Float32Array(1600).fill(.1);
  for (let i = 0; i < 40; i++) meter.push(full);
  assert.equal(meter.finished, true);
  const completed = meter.snapshot();
  meter.push(new Float32Array(1600).fill(.9));
  assert.deepEqual(meter.snapshot(), completed);
  assert.equal(meter.samples, 64000);
});

test('phone-check UI has no media storage, export, playback or network-send path', async () => {
  const source = await readFile(new URL('../web/assets/device-check.js', import.meta.url), 'utf8');
  assert.doesNotMatch(source, /\b(?:fetch|localStorage|sessionStorage|indexedDB|sendBeacon|MediaRecorder)\b/);
  assert.doesNotMatch(source, /\.(?:play|download)\s*\(/);
});
