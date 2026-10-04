import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {webcrypto} from 'node:crypto';
import {syntheticWav} from '../web/assets/listen-model.mjs';
import {audacityFiles, audacityLabels, audacityPackage} from '../web/assets/audacity-export.mjs';

globalThis.crypto ??= webcrypto;
const fixture = () => JSON.parse(fs.readFileSync(new URL('../examples/annotations.synthetic.json', import.meta.url), 'utf8'));
const decode = file => new TextDecoder('utf-8', {fatal:true}).decode(file.bytes);

test('Audacity receives timed UTF-8 rows while the sidecar keeps exact original observations', async () => {
  const doc = fixture();
  doc.animal_context = {group:'parrot', species:'budgerigar', basis:'observer-declared'};
  doc.events[0].notes = 'שלום 🌿\tfirst\nsecond\rthird\u0000\u0085\u2028\\ literal | =formula';
  doc.events[0].start_seconds = 1.12345678;
  doc.events[1].start_seconds = 1.5; // Retain overlapping observations.
  doc.events.reverse();
  const wav = syntheticWav();
  const files = await audacityFiles(wav, doc);
  assert.deepEqual(files.map(f => f.name), ['recording.wav','labels.txt','annotations.json','export-report.json','READ-ME.txt']);
  assert.deepEqual(files[0].bytes, new Uint8Array(wav));
  assert.deepEqual(JSON.parse(decode(files[2])), doc);
  const rows = decode(files[1]).trimEnd().split('\n').map(line => line.split('\t'));
  assert.equal(rows.length, 2); assert.ok(rows.every(row => row.length === 3));
  assert.deepEqual(rows.map(row => row.slice(0,2)), [['1.123457','2.000000'],['1.500000','5.000000']]);
  assert.match(rows[0][2], /declared synthetic/); assert.match(rows[0][2], /context=unknown/);
  assert.match(rows[0][2], /source=not observed/); assert.match(rows[0][2], /confidence=clear/);
  assert.equal(JSON.parse(rows[0][2].split(' | notes=')[1]), doc.events[1].notes);
  const report=JSON.parse(decode(files[3]));
  assert.deepEqual(report.label_row_event_ids,[1,2]);
  assert.ok(report.maximum_time_rounding_error_seconds <= .0000005);
  assert.match(report.limitations.join(' '), /do not update annotations.json/);
  assert.match(decode(files[4]), /unencrypted/);
  const zip=await audacityPackage(wav,doc);
  assert.equal(new DataView(await zip.arrayBuffer()).getUint32(0,true),0x04034b50);
});

test('mismatched audio, invalid context and collapsed timing are rejected without changing inputs', async () => {
  const audio=syntheticWav(), doc=fixture(), before=JSON.stringify(doc);
  const mismatch=audio.slice(0); new Uint8Array(mismatch)[100]=7;
  await assert.rejects(audacityFiles(mismatch,doc),/does not match/);
  assert.equal(JSON.stringify(doc),before);
  const context=fixture();context.events[0].context='feeding';
  await assert.rejects(audacityFiles(audio,context),/observed context/);
  const empty=fixture();empty.events=[];assert.throws(()=>audacityLabels(empty),/at least one/);
  const short=fixture();short.events[0].end_seconds=1.0000001;
  assert.throws(()=>audacityLabels(short),/too short/);
});

test('an asynchronous save snapshots both audio and notes before the first await', async () => {
  const audio=syntheticWav(), doc=fixture(), expected=structuredClone(doc), expectedAudio=audio.slice(0);
  let finish;
  const waiting=new Promise(resolve=>{finish=resolve;});
  const pending=audacityFiles(audio,doc,async bytes=>{await waiting;return webcrypto.subtle.digest('SHA-256',bytes);});
  doc.events[0].notes='later edit';new Uint8Array(audio)[100]=7;finish();
  const files=await pending;
  assert.deepEqual(JSON.parse(decode(files[2])),expected);
  assert.deepEqual(files[0].bytes,new Uint8Array(expectedAudio));
});

test('oversized metadata and malformed WAV never produce an export', async()=>{
  const large=fixture();large.extra='x'.repeat(2*1024*1024);
  await assert.rejects(audacityFiles(syntheticWav(),large),/too many notes/);
  await assert.rejects(audacityFiles(new ArrayBuffer(44),fixture()),/RIFF/);
});
