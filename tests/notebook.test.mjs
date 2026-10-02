import test from 'node:test';
import assert from 'node:assert/strict';
import {webcrypto} from 'node:crypto';
import {syntheticWav, VERSION} from '../web/assets/listen-model.mjs';
import {makeNotebook, readNotebook, MAX_NOTEBOOK_BYTES} from '../web/assets/notebook.mjs';
if (!globalThis.crypto) globalThis.crypto = webcrypto;
async function fixture() {
  const audio=syntheticWav();
  const sha256=Buffer.from(await crypto.subtle.digest('SHA-256',audio)).toString('hex');
  return {audio,labels:{schema:'talk2nature.annotation.v1',tool_version:VERSION,recording:{sha256,duration_seconds:8,sample_rate:16000,channels:1,origin:'synthetic',recording_id:'demo',session_id:'unknown',individual_id:'unknown',annotator_id:'reviewer'},events:[{id:1,start_seconds:1,end_seconds:2,kind:'other sound',context:'unknown',context_source:'not observed',confidence:'clear',notes:'רגע · A tone, not an animal.'}]}};
}
test('one notebook restores exact WAV bytes, Unicode notes and labels',async()=>{
 const {audio,labels}=await fixture();const book=await makeNotebook(audio,labels);const restored=await readNotebook(book);
 assert.deepEqual(restored.audio,audio);assert.deepEqual(restored.labels,labels);assert.equal(restored.info.duration,8);
});
test('damaged, mismatched, truncated and excessive notebooks fail before import',async()=>{
 const {audio,labels}=await fixture();const book=await makeNotebook(audio,labels);
 const changed=book.slice(0);new Uint8Array(changed)[changed.byteLength-1]^=1;
 await assert.rejects(readNotebook(changed),/does not match/);
 await assert.rejects(readNotebook(book.slice(0,-1)),/complete RIFF/);
 const invalid=book.slice(0);new DataView(invalid).setUint32(8,0xffffffff,true);
 await assert.rejects(readNotebook(invalid),/incomplete/);
 await assert.rejects(readNotebook(new ArrayBuffer(MAX_NOTEBOOK_BYTES+1)),/under 28/);
 await assert.rejects(makeNotebook(audio,{...labels,recording:{...labels.recording,sample_rate:48000}}),/does not match/);
});
test('save snapshots labels before hashing and rejects invalid context',async()=>{
 const {audio,labels}=await fixture();const promise=makeNotebook(audio,labels);labels.events[0].notes='Later edit';
 assert.notEqual((await readNotebook(await promise)).labels.events[0].notes,'Later edit');
 labels.events[0].context='feeding';await assert.rejects(makeNotebook(audio,labels),/observed context/);
});
