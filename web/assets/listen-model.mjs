import {validateAnimal} from './animal-model.mjs';
// Local annotation format. No upload, model prediction or research admission.
export const VERSION = '0.1.0';
export const MAX_BYTES = 25 * 1024 * 1024;
export const MAX_SECONDS = 120;
export const CONTEXTS = ['unknown', 'feeding', 'resting', 'moving', 'social interaction'];
export const SOURCES = ['not observed', 'direct observation', 'synchronized video'];
export const KINDS = ['uncertain', 'vocalization', 'other sound'];
export const CONFIDENCE = ['uncertain', 'clear'];

export function readWav(buffer) {
  if (!(buffer instanceof ArrayBuffer) || buffer.byteLength < 44 || buffer.byteLength > MAX_BYTES) throw Error('Choose a WAV file between 44 bytes and 25 MB.');
  const view = new DataView(buffer);
  const tag = p => String.fromCharCode(...new Uint8Array(buffer, p, 4));
  if (tag(0) !== 'RIFF' || tag(8) !== 'WAVE' || view.getUint32(4, true) + 8 !== buffer.byteLength) throw Error('Expected a complete RIFF/WAVE file.');
  let format, data;
  for (let p = 12; p + 8 <= buffer.byteLength;) {
    const name = tag(p), length = view.getUint32(p + 4, true), start = p + 8;
    if (start + length > buffer.byteLength) throw Error('The WAV file is truncated.');
    if (name === 'fmt ') {
      if (format || length < 16) throw Error('Invalid WAV format chunk.');
      format = {code: view.getUint16(start, true), channels: view.getUint16(start + 2, true), sample_rate: view.getUint32(start + 4, true), byteRate: view.getUint32(start + 8, true), align: view.getUint16(start + 12, true), bits: view.getUint16(start + 14, true)};
    }
    if (name === 'data') {
      if (data) throw Error('Multiple audio chunks are not supported.');
      data = {start, length};
    }
    p = start + length + (length % 2);
  }
  if (!format || !data) throw Error('WAV format or audio chunk is missing.');
  const f = format, bytes = f.bits / 8;
  if (![1, 2].includes(f.channels) || f.sample_rate < 8000 || f.sample_rate > 192000 || !((f.code === 1 && [16, 24, 32].includes(f.bits)) || (f.code === 3 && f.bits === 32))) throw Error('Use mono/stereo PCM 16/24/32-bit or float32 WAV, at 8–192 kHz.');
  if (f.align !== f.channels * bytes || f.byteRate !== f.sample_rate * f.align || !data.length || data.length % f.align) throw Error('Invalid WAV frame layout.');
  const frames = data.length / f.align, duration = frames / f.sample_rate;
  if (duration > MAX_SECONDS) throw Error('Use a recording of at most 120 seconds.');
  // Envelope includes both channels; opposite-phase stereo cannot cancel.
  const bins = Array.from({length: Math.min(1200, frames)}, () => [1, -1]);
  let peak = 0, squares = 0, clipped = 0;
  for (let frame = 0; frame < frames; frame++) {
    const bin = bins[Math.min(bins.length - 1, Math.floor(frame * bins.length / frames))];
    for (let channel = 0; channel < f.channels; channel++) {
      const p = data.start + frame * f.align + channel * bytes;
      let sample;
      if (f.code === 3) sample = view.getFloat32(p, true);
      else if (f.bits === 16) sample = view.getInt16(p, true) / 32768;
      else if (f.bits === 32) sample = view.getInt32(p, true) / 2147483648;
      else { let n = view.getUint8(p) | (view.getUint8(p + 1) << 8) | (view.getUint8(p + 2) << 16); if (n & 0x800000) n -= 0x1000000; sample = n / 8388608; }
      if (!Number.isFinite(sample)) throw Error('The WAV file contains non-finite samples.');
      const magnitude = Math.abs(sample);
      peak = Math.max(peak, magnitude); squares += sample * sample;
      if (magnitude >= 0.999) clipped++;
      bin[0] = Math.min(bin[0], sample); bin[1] = Math.max(bin[1], sample);
    }
  }
  return {duration, sample_rate: f.sample_rate, channels: f.channels, bits: f.bits, bins, peak, rms: Math.sqrt(squares / (frames * f.channels)), near_full_scale_fraction: clipped / (frames * f.channels)};
}

export function syntheticWav() {
  const rate = 16000, seconds = 8, buffer = new ArrayBuffer(44 + rate * seconds * 2), v = new DataView(buffer);
  const tag = (p, s) => [...s].forEach((c, i) => v.setUint8(p + i, c.charCodeAt(0)));
  tag(0, 'RIFF'); v.setUint32(4, buffer.byteLength - 8, true); tag(8, 'WAVE'); tag(12, 'fmt '); v.setUint32(16, 16, true); v.setUint16(20, 1, true); v.setUint16(22, 1, true); v.setUint32(24, rate, true); v.setUint32(28, rate * 2, true); v.setUint16(32, 2, true); v.setUint16(34, 16, true); tag(36, 'data'); v.setUint32(40, rate * seconds * 2, true);
  // Integer pulse trains keep the fixture byte-identical across JS engines.
  for (let i = 0; i < rate * seconds; i++) {
    const active = (i >= rate && i < 2 * rate) || (i >= 4 * rate && i < 5 * rate);
    v.setInt16(44 + i * 2, active ? (i % 40 < 20 ? 4500 : -4500) : 0, true);
  }
  return buffer;
}

function text(value, name, max = 80) {
  if (typeof value !== 'string' || !value.trim() || value !== value.trim() || value.length > max) throw Error(`${name}: enter 1–${max} characters without surrounding spaces.`);
}
function numeric(value) { return typeof value === 'number' && Number.isFinite(value); }

export function validateDocument(doc, expected = null) {
  if (!doc || doc.schema !== 'talk2nature.annotation.v1' || doc.tool_version !== VERSION) throw Error('Unsupported annotation format/version.');
  if (doc.animal_context !== undefined) validateAnimal(doc.animal_context);
  const r = doc.recording;
  if (!r || !/^[a-f0-9]{64}$/.test(r.sha256) || !numeric(r.duration_seconds) || r.duration_seconds <= 0 || r.duration_seconds > MAX_SECONDS || !Number.isInteger(r.sample_rate) || r.sample_rate < 8000 || r.sample_rate > 192000 || ![1, 2].includes(r.channels) || !['synthetic', 'user-supplied'].includes(r.origin)) throw Error('Invalid recording metadata.');
  for (const key of ['recording_id', 'session_id', 'individual_id', 'annotator_id']) text(r[key], key);
  if (expected && ['sha256', 'duration_seconds', 'sample_rate', 'channels', 'origin'].some(key => r[key] !== expected[key])) throw Error('This label file does not match the open recording and its origin.');
  if (!Array.isArray(doc.events) || doc.events.length > 1000) throw Error('Use at most 1,000 events.');
  const seen = new Set();
  for (const e of doc.events) {
    if (!e || !Number.isSafeInteger(e.id) || e.id < 1 || seen.has(e.id)) throw Error('Event IDs must be distinct positive safe integers.');
    seen.add(e.id);
    if (!numeric(e.start_seconds) || !numeric(e.end_seconds) || e.start_seconds < 0 || e.end_seconds <= e.start_seconds || e.end_seconds > r.duration_seconds) throw Error('Each event needs a start before its end, within the recording.');
    if (!KINDS.includes(e.kind) || !CONTEXTS.includes(e.context) || !SOURCES.includes(e.context_source) || !CONFIDENCE.includes(e.confidence)) throw Error('Unknown event label.');
    if (e.context !== 'unknown' && e.context_source === 'not observed') throw Error('An observed context needs direct observation or synchronized video; otherwise choose unknown.');
    if (typeof e.notes !== 'string' || e.notes.length > 500) throw Error('Notes must be text of at most 500 characters.');
  }
  return doc;
}

export function eventCsv(doc) {
  validateDocument(doc);
  const quote = value => '"' + String(value).replace(/^[\s]*[=+@-]/, "'$&").replace(/"/g, '""') + '"';
  const keys = ['id', 'start_seconds', 'end_seconds', 'kind', 'context', 'context_source', 'confidence', 'notes'];
  return [['recording_id', 'source_sha256', 'animal_group', 'species_label', 'identity_basis', ...keys], ...doc.events.map(e => [doc.recording.recording_id, doc.recording.sha256, doc.animal_context?.group ?? 'unknown', doc.animal_context?.species ?? '', doc.animal_context?.basis ?? 'not recorded', ...keys.map(k => e[k])])].map(row => row.map(quote).join(',')).join('\r\n') + '\r\n';
}
