// A bounded, uncompressed local notebook: a versioned header, labels, then WAV.
// No paths, executable content, server access or automatic research admission.
import {MAX_BYTES, readWav, validateDocument} from './listen-model.mjs';

const MAGIC = 'T2NBOOK1';
const MAX_LABELS = 2 * 1024 * 1024;
export const MAX_NOTEBOOK_BYTES = 12 + MAX_LABELS + MAX_BYTES;
const encoder = new TextEncoder();
const decoder = new TextDecoder('utf-8', {fatal: true});
async function checked(audio, labels) {
  const info = readWav(audio);
  const hash = [...new Uint8Array(await crypto.subtle.digest('SHA-256', audio))].map(b => b.toString(16).padStart(2, '0')).join('');
  validateDocument(labels, {sha256: hash, duration_seconds: info.duration, sample_rate: info.sample_rate, channels: info.channels, origin: labels?.recording?.origin});
  // An imported origin remains a declaration, not verified provenance.
  return {audio, labels, info};
}
export async function makeNotebook(audio, labels) {
  // Snapshot before awaiting hashing so a later UI edit cannot change this save.
  audio = audio.slice(0); labels = structuredClone(labels);
  await checked(audio, labels);
  const meta = encoder.encode(JSON.stringify(labels));
  if (meta.length > MAX_LABELS) throw Error('This notebook has too many notes.');
  const output = new Uint8Array(12 + meta.length + audio.byteLength);
  output.set(encoder.encode(MAGIC));
  new DataView(output.buffer).setUint32(8, meta.length, true);
  output.set(meta, 12); output.set(new Uint8Array(audio), 12 + meta.length);
  return output.buffer;
}
export async function readNotebook(buffer) {
  if (!(buffer instanceof ArrayBuffer) || buffer.byteLength < 56 || buffer.byteLength > MAX_NOTEBOOK_BYTES) throw Error('Choose a complete Talk2Nature notebook under 28 MB.');
  if (decoder.decode(new Uint8Array(buffer, 0, 8)) !== MAGIC) throw Error('This is not a supported Talk2Nature notebook.');
  const length = new DataView(buffer).getUint32(8, true);
  if (!length || length > MAX_LABELS || 12 + length + 44 > buffer.byteLength) throw Error('The notebook is incomplete or its notes are too large.');
  const labels = JSON.parse(decoder.decode(new Uint8Array(buffer, 12, length)));
  return checked(buffer.slice(12 + length), labels);
}
