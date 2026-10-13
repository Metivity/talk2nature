import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {webcrypto} from 'node:crypto';
import {syntheticWav} from '../web/assets/listen-model.mjs';
import {aoefFiles, aoefPackage} from '../web/assets/aoef-export.mjs';

globalThis.crypto ??= webcrypto;
const fixture = () => JSON.parse(fs.readFileSync(new URL('../examples/annotations.synthetic.json', import.meta.url), 'utf8'));
const text = file => new TextDecoder('utf-8', {fatal:true}).decode(file.bytes);

test('AOEF keeps interval labels, unchanged audio and full Talk2Nature provenance sidecar', async () => {
  const doc=fixture();
  doc.animal_context={group:'parrot',species:'budgerigar',basis:'observer-declared'};
  doc.events[0].notes='Synthetic note';
  const audio=syntheticWav(), files=await aoefFiles(audio,doc);
  assert.deepEqual(files.map(file=>file.name),['recording.wav','dataset.aoef.json','annotation-project.aoef.json','talk2nature-annotations.json','export-report.json','READ-ME.txt']);
  assert.deepEqual(files[0].bytes,new Uint8Array(audio));
  const dataset=JSON.parse(text(files[1])), project=JSON.parse(text(files[2]));
  assert.equal(dataset.version,'1.1.0'); assert.equal(dataset.data.collection_type,'dataset');
  assert.equal(project.version,'1.1.0'); assert.equal(project.data.collection_type,'annotation_project');
  assert.deepEqual(project.data.project_tags,project.data.tags.map(tag=>tag.id));
  const recording=dataset.data.recordings[0];
  assert.equal(recording.path,'recording.wav'); assert.equal(recording.hash,doc.recording.sha256);
  assert.equal(project.data.recordings[0].uuid,recording.uuid);
  assert.equal(project.data.sound_events.length,2);
  assert.equal(project.data.sound_events[0].geometry.type,'TimeInterval');
  assert.deepEqual(project.data.sound_events.map(item=>item.geometry.coordinates),[[1,2],[4,5]]);
  const tags=Object.fromEntries(project.data.tags.map(tag=>[tag.id,[tag.key,tag.value]]));
  const first=project.data.sound_event_annotations[0];
  assert.deepEqual(first.tags.map(id=>tags[id]),[
    ['talk2nature.kind','other sound'],['talk2nature.context','unknown'],
    ['talk2nature.context_source','not observed'],['talk2nature.confidence','clear']
  ]);
  assert.equal(first.notes[0].message,'Synthetic note');
  assert.equal(project.data.clip_annotations[0].sound_events.length,2);
  assert.equal(project.data.tasks[0].clip,project.data.clips[0].uuid);
  const aoefText=text(files[1])+text(files[2]);
  for(const privateField of ['annotator_id','individual_id','session_id','email','username','created_by']) assert.ok(!aoefText.includes(privateField));
  const sidecar=JSON.parse(text(files[3]));
  assert.deepEqual(sidecar,doc);
  assert.equal(sidecar.animal_context.species,'budgerigar');
  const report=JSON.parse(text(files[4]));
  assert.equal(report.source_sha256,doc.recording.sha256); assert.equal(report.event_count,2);
  assert.match(report.tested_library,/Whombat 0\.9\.0 synthetic UI import verified/);
  assert.match(report.limitations.join(' '),/sidecar may contain aliases/);
  assert.match(text(files[5]),/Import dataset\.aoef\.json first/);
  assert.match(text(files[5]),/unencrypted/);
  const zip=await aoefPackage(audio,doc);
  assert.equal(new DataView(await zip.arrayBuffer()).getUint32(0,true),0x04034b50);
});

test('AOEF export rejects empty events, WAV mismatch, invalid labels and oversized sidecar', async()=>{
  const audio=syntheticWav();
  const empty=fixture();empty.events=[];
  await assert.rejects(aoefFiles(audio,empty),/at least one observation/);
  const mismatch=audio.slice(0);new Uint8Array(mismatch)[100]^=1;
  await assert.rejects(aoefFiles(mismatch,fixture()),/does not match/);
  const invalid=fixture();invalid.events[0].context='feeding';
  await assert.rejects(aoefFiles(audio,invalid),/observed context/);
  const large=fixture();large.extra='x'.repeat(2*1024*1024);
  await assert.rejects(aoefFiles(audio,large),/sidecar is too large/);
});

test('AOEF export snapshots inputs before hashing and cancels mutations', async()=>{
  const audio=syntheticWav(), doc=fixture(), expected=structuredClone(doc), expectedAudio=audio.slice(0);
  let finish;const waiting=new Promise(resolve=>{finish=resolve;});
  const pending=aoefFiles(audio,doc,async bytes=>{await waiting;return webcrypto.subtle.digest('SHA-256',bytes);});
  doc.events[0].notes='Later edit';new Uint8Array(audio)[100]^=1;finish();
  const files=await pending;
  assert.deepEqual(JSON.parse(text(files[3])),expected);
  assert.deepEqual(files[0].bytes,new Uint8Array(expectedAudio));
});
