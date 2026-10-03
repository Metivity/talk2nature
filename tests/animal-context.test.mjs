import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {ANIMAL_GROUPS, unknownAnimal, validateAnimal} from '../web/assets/animal-model.mjs';
import {validateDocument, syntheticWav, eventCsv} from '../web/assets/listen-model.mjs';
import {makeNotebook, readNotebook} from '../web/assets/notebook.mjs';
import {StationSession} from '../web/assets/station-model.mjs';
import {sessionFiles} from '../web/assets/station-export.mjs';
const document = () => JSON.parse(readFileSync(new URL('../examples/annotations.synthetic.json',import.meta.url),'utf8'));

test('all supported animal groups and Unicode species round trip with audio and annotations',async()=>{
 for(const [group] of ANIMAL_GROUPS){
  const doc=document();doc.animal_context={group,species:'תוכי · 🦜',basis:'observer-declared'};
  const audio=syntheticWav();doc.recording.sha256=Buffer.from(await crypto.subtle.digest('SHA-256',audio)).toString('hex');
  const result=await readNotebook(await makeNotebook(audio,doc));
  assert.deepEqual(result.labels.animal_context,doc.animal_context);assert.deepEqual(result.audio,audio);
  assert.equal(result.labels.recording.origin,'synthetic');
 }
});
test('animal metadata is optional for old files, and untrusted fields and false authority are rejected',()=>{
 assert.ok(validateDocument(document()));
 for(const value of [null,[],{}, {...unknownAnimal(),group:'dragon'}, {...unknownAnimal(),basis:'AI-verified'}, {...unknownAnimal(),species:'x'.repeat(81)}, {...unknownAnimal(),species:'a\nb'}, {...unknownAnimal(),species:' leading'}, {...unknownAnimal(),confidence:1}]){
  const doc=document();doc.animal_context=value;assert.throws(()=>validateDocument(doc));
 }
 assert.doesNotThrow(()=>validateAnimal({...unknownAnimal(),species:'🦜'.repeat(40)}));
 assert.throws(()=>validateAnimal({...unknownAnimal(),species:'🦜'.repeat(41)}));
});
test('station freezes animal declaration at start and exports copies, not mutable references',async()=>{
 const animal={group:'parrot',species:'budgerigar',basis:'observer-declared'};
 const session=new StationSession(16000,{animalContext:animal});animal.species='cockatiel';
 session.stop();const first=session.exportRecord();assert.equal(first.animal_context.species,'budgerigar');
 first.animal_context.species='changed';assert.equal(session.exportRecord().animal_context.species,'budgerigar');
 const files=await sessionFiles(session,'fixture',{});
 const json=JSON.parse(new TextDecoder().decode(files[0].bytes));assert.equal(json.animal_context.species,'budgerigar');
 assert.throws(()=>new StationSession(16000,{animalContext:{...animal,group:'invalid'}}));
});
test('CSV includes declared animal context and neutralizes spreadsheet formulas',()=>{
 const doc=document();doc.animal_context={group:'other_animal',species:'=1+1',basis:'observer-declared'};
 const csv=eventCsv(doc);assert.match(csv,/animal_group/);assert.match(csv,/"'=1\+1"/);assert.match(csv,/observer-declared/);
});
