import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {webcrypto} from 'node:crypto';
import * as model from '../web/assets/listen-model.mjs';
import {animalPicker} from '../web/assets/animal-picker.mjs';
import * as notebook from '../web/assets/notebook.mjs';
import * as audacity from '../web/assets/audacity-export.mjs';
import * as aoef from '../web/assets/aoef-export.mjs';
import * as sessionImport from '../web/assets/session-import.mjs';
import {WindowSession} from '../web/assets/window-model.mjs';
import {sessionFiles,zipFiles} from '../web/assets/station-export.mjs';
if (!globalThis.crypto) globalThis.crypto=webcrypto;

// Execute the real event handlers with a small DOM facade. This checks whether
// user drafts are lost or omitted, separately from annotation-format tests.
function setup(overrides={}) {
  const elements=new Map(), windowEvents={}, downloads=[], files=[], objectUrls=new Map();
  const defaults={'event-start':'0','event-end':'1','event-kind':'uncertain','event-context':'unknown','event-source':'not observed','event-confidence':'uncertain','event-notes':''};
  const harness={confirm:false,confirmations:0,focus:null};
  function element(id='') {
    return {id,value:defaults[id]??'',textContent:'',hidden:false,open:false,disabled:false,paused:true,handlers:{},children:[],clientWidth:600,
      addEventListener(name,fn){this.handlers[name]=fn;},
      async fire(name,event={}){return await this.handlers[name]?.(event);},
      append(...nodes){this.children.push(...nodes);},replaceChildren(...nodes){this.children=nodes;},
      setAttribute(){},removeAttribute(){},pause(){this.paused=true;},play(){this.paused=false;},load(){},remove(){},
      focus(){harness.focus=id;},click(){if(this.download){downloads.push(this.download);files.push({name:this.download,blob:objectUrls.get(this.href)});}},
      reset(){for(const [id,value] of Object.entries(defaults)) get(id).value=value;},
      getContext(){return {scale(){},fillRect(){},beginPath(){},moveTo(){},lineTo(){},stroke(){}};}
    };
  }
  const get=id=>{if(!elements.has(id))elements.set(id,element(id));return elements.get(id);};
  const document={getElementById:get,createElement:()=>element(),body:element()};
  const window={devicePixelRatio:1,confirm(){harness.confirmations++;return harness.confirm;},addEventListener(name,fn){windowEvents[name]=fn;}};
  const source=fs.readFileSync(new URL('../web/assets/listen.js',import.meta.url),'utf8').replace(/^import .*;\n/gm,'');
  const urlApi={createObjectURL(blob){const key=`blob:synthetic-${objectUrls.size+1}`;objectUrls.set(key,blob);return key;},revokeObjectURL(){}};
  vm.runInNewContext(source,{...model,...notebook,...audacity,...aoef,...sessionImport,...overrides,animalPicker,document,window,crypto:webcrypto,Blob,structuredClone,URL:urlApi,setTimeout(){}});
  return {...harness,get,downloads,files,windowEvents,state:harness,async type(id,value){get(id).value=value;await get('event-form').fire('input');}};
}

async function savedSessionZip() {
  const session=new WindowSession(8000);
  for(let i=0;i<300;i++) { session.push(new Float32Array(800).fill(i<30?.01:0)); if(i===80) session.mark('observation','<img src=x onerror=alert(1)>'); }
  session.stop();
  const sourceFiles=await sessionFiles(session,'review rehearsal',{}), record=JSON.parse(new TextDecoder().decode(sourceFiles[0].bytes));
  return {record,archive:await zipFiles(sourceFiles).arrayBuffer()};
}

test('replacing or clearing a recording protects an unfinished observation',async()=>{
  const h=setup();await h.get('example').fire('click');
  await h.type('event-notes','Keep this draft');
  await h.get('example').fire('click');
  assert.equal(h.get('event-notes').value,'Keep this draft');
  await h.get('clear-recording').fire('click');
  assert.equal(h.get('event-notes').value,'Keep this draft');
  assert.equal(h.state.confirmations,2);
  let warned=false;h.windowEvents.beforeunload({preventDefault(){warned=true;}});assert.ok(warned);
  h.state.confirm=true;await h.get('example').fire('click');
  assert.equal(h.get('event-notes').value,'');
  warned=false;h.windowEvents.beforeunload({preventDefault(){warned=true;}});assert.equal(warned,false);
});

test('an unfinished draft cannot silently disappear from JSON or CSV export',async()=>{
  const h=setup();await h.get('example').fire('click');await h.type('event-notes','Pending');
  await h.get('export-json').fire('click');await h.get('export-csv').fire('click');await h.get('save-notebook').fire('click');await h.get('export-audacity').fire('click');await h.get('export-aoef').fire('click');
  assert.equal(h.downloads.length,0);assert.equal(h.state.focus,'save-event');
  assert.match(h.get('export-status').textContent,/unfinished/);
  await h.get('event-form').fire('submit',{preventDefault(){}});
  assert.match(h.get('event-count').textContent,/1 event/);
  await h.get('export-json').fire('click');assert.deepEqual(h.downloads,['talk2nature-labels.json']);
  // A requested download is not proof that the browser saved it.
  let warned=false;h.windowEvents.beforeunload({preventDefault(){warned=true;}});assert.ok(warned);
});

test('AOEF export requires an accepted observation and reports the untested app-import boundary',async()=>{
 const h=setup();await h.get('example').fire('click');
 await h.get('export-aoef').fire('click');assert.equal(h.downloads.length,0);
 assert.match(h.get('export-status').textContent,/at least one observation/);
 await h.get('event-form').fire('submit',{preventDefault(){}});
 await h.get('export-aoef').fire('click');assert.deepEqual(h.downloads,['talk2nature-aoef.zip']);
 assert.equal(h.get('export-aoef').disabled,false);
 assert.match(h.get('export-status').textContent,/Whombat UI import is untested/);
 const fail=setup({aoefPackage:async()=>{throw Error('Test AOEF failure');}});await fail.get('example').fire('click');
 await fail.get('event-form').fire('submit',{preventDefault(){}});await fail.get('export-aoef').fire('click');
 assert.equal(fail.downloads.length,0);assert.match(fail.get('export-status').textContent,/Test AOEF failure/);
 assert.equal(fail.get('export-aoef').disabled,false);
});

test('clearing a session cancels a pending AOEF download',async()=>{
 let release;const pending=new Promise(resolve=>{release=resolve;});
 const h=setup({aoefPackage:()=>pending});await h.get('example').fire('click');
 await h.get('event-form').fire('submit',{preventDefault(){}});
 const saving=h.get('export-aoef').fire('click');assert.equal(h.get('export-aoef').disabled,true);
 h.state.confirm=true;await h.get('clear-recording').fire('click');release(new Blob(['unused']));await saving;
 assert.equal(h.downloads.length,0);assert.match(h.get('listen-status').textContent,/Session cleared/);
});

test('Audacity export handles empty events and failed saves without discarding the notebook',async()=>{
 const h=setup();await h.get('example').fire('click');
 await h.get('export-audacity').fire('click');assert.equal(h.downloads.length,0);
 assert.match(h.get('export-status').textContent,/at least one/);
 await h.get('event-form').fire('submit',{preventDefault(){}});
 await h.get('export-audacity').fire('click');assert.deepEqual(h.downloads,['talk2nature-audacity.zip']);
 assert.equal(h.get('export-audacity').disabled,false);
 assert.match(h.get('export-status').textContent,/download requested/);
 let warned=false;h.windowEvents.beforeunload({preventDefault(){warned=true;}});assert.ok(warned);
 const fail=setup({audacityPackage:async()=>{throw Error('Test save failure');}});await fail.get('example').fire('click');
 await fail.get('event-form').fire('submit',{preventDefault(){}});await fail.get('export-audacity').fire('click');
 assert.equal(fail.downloads.length,0);assert.match(fail.get('event-count').textContent,/1 event/);
 assert.match(fail.get('export-status').textContent,/Test save failure/);assert.equal(fail.get('export-audacity').disabled,false);
});

test('a cleared session cancels a pending Audacity download',async()=>{
 let release;const pending=new Promise(resolve=>{release=resolve;});
 const h=setup({audacityPackage:()=>pending});await h.get('example').fire('click');
 await h.get('event-form').fire('submit',{preventDefault(){}});
 const saving=h.get('export-audacity').fire('click');assert.equal(h.get('export-audacity').disabled,true);
 h.state.confirm=true;await h.get('clear-recording').fire('click');release(new Blob(['unused']));await saving;
 assert.equal(h.downloads.length,0);assert.match(h.get('listen-status').textContent,/Session cleared/);
});

test('invalid hidden identifiers are revealed and focused on export',async()=>{
  const h=setup();await h.get('example').fire('click');h.get('session-id').value='';
  await h.get('export-json').fire('click');assert.equal(h.downloads.length,0);
  assert.equal(h.get('recording-identifiers').open,true);assert.equal(h.state.focus,'session-id');
  assert.ok(h.get('export-status').textContent);
});

test('cancelling a draft requires confirmation and preserves committed events',async()=>{
  const h=setup();await h.get('example').fire('click');
  await h.get('event-form').fire('submit',{preventDefault(){}});
  await h.type('event-notes','New draft');await h.get('cancel-edit').fire('click');
  assert.equal(h.get('event-notes').value,'New draft');
  h.state.confirm=true;await h.get('cancel-edit').fire('click');
  assert.equal(h.get('event-notes').value,'');assert.match(h.get('event-count').textContent,/1 event/);
});

test('animal choice survives label import, marks edits unsaved and resets for a fresh recording',async()=>{
 const h=setup();await h.get('example').fire('click');
 h.get('listen-animal-group').value='dog';await h.get('listen-animal-group').fire('change');
 let warned=false;h.windowEvents.beforeunload({preventDefault(){warned=true;}});assert.ok(warned);
 const doc=JSON.parse(fs.readFileSync(new URL('../examples/annotations.synthetic.json',import.meta.url),'utf8'));
 const audio=model.syntheticWav();doc.recording.sha256=Buffer.from(await webcrypto.subtle.digest('SHA-256',audio)).toString('hex');
 doc.animal_context={group:'parrot',species:'budgerigar',basis:'observer-declared'};
 h.state.confirm=true;
 await h.get('labels-file').fire('change',{target:{files:[{size:1000,text:async()=>JSON.stringify(doc)}],value:'selected'}});
 assert.equal(h.get('listen-animal-group').value,'parrot');assert.equal(h.get('listen-animal-species').value,'budgerigar');
 delete doc.animal_context;
 await h.get('labels-file').fire('change',{target:{files:[{size:1000,text:async()=>JSON.stringify(doc)}],value:'selected'}});
 assert.equal(h.get('listen-animal-group').value,'unknown');assert.equal(h.get('listen-animal-species').value,'');
 await h.get('example').fire('click');assert.equal(h.get('listen-animal-group').value,'unknown');
});

test('opening a notebook restores animal context through the real file-change handler',async()=>{
 const h=setup();
 const doc=JSON.parse(fs.readFileSync(new URL('../examples/annotations.synthetic.json',import.meta.url),'utf8'));
 doc.animal_context={group:'parrot',species:'budgerigar',basis:'observer-declared'};
 const buffer=await notebook.makeNotebook(model.syntheticWav(),doc);
 await h.get('wav-file').fire('change',{target:{files:[{name:'practice.t2n',size:buffer.byteLength,arrayBuffer:async()=>buffer}],value:'selected'}});
 assert.match(h.get('listen-status').textContent,/Notebook reopened with 2 observations/);
 assert.equal(h.get('listen-animal-group').value,'parrot');
 assert.equal(h.get('listen-animal-species').value,'budgerigar');
 assert.equal(h.get('origin-badge').textContent,'Synthetic tones');
});

test('Review imports one checked Station clip and keeps its full source journal in the notebook',async()=>{
 const {record,archive}=await savedSessionZip(),h=setup();
 const file={name:'station-session.zip',size:archive.byteLength,arrayBuffer:async()=>archive};
 await h.get('session-zip-file').fire('change',{target:{files:[file],value:'selected'}});
 assert.match(h.get('session-import-status').textContent,/Session checked/);
 assert.equal(h.get('session-clip-list').children.length,1);
 const button=h.get('session-clip-list').children[0].children.find(child=>child.textContent==='Review this clip');
 assert.ok(button); await button.fire('click');
 assert.equal(h.get('origin-badge').textContent,'Synthetic session clip');
 assert.match(h.get('source-session-note').textContent,/Continuous observation window; it is not a detected vocalization/);
 assert.match(h.get('source-session-note').textContent,/full session journal/);
 assert.equal(h.get('recording-audio').paused,true);
 assert.match(h.get('event-count').textContent,/No events yet/);
 assert.equal(h.get('session-id').value,record.session_id);
 await h.get('event-form').fire('submit',{preventDefault(){}});
 await h.get('save-notebook').fire('click');
 const saved=h.files.find(item=>item.name==='talk2nature-notebook.t2n');
 assert.ok(saved?.blob);
 const reopened=await notebook.readNotebook(await saved.blob.arrayBuffer());
 const source=reopened.labels.recording.source_session;
 assert.equal(source.journal.session_id,record.session_id);
 assert.equal(source.event_id,record.events[0].id);
 assert.equal(source.journal.events[0].audio_sha256,reopened.labels.recording.sha256);
 assert.equal(source.journal.markers[0].note,'<img src=x onerror=alert(1)>');
 assert.match(model.eventCsv(reopened.labels),/source_session_event_id/);
 assert.ok(model.eventCsv(reopened.labels).includes(record.session_id));
 const forged=structuredClone(reopened.labels);forged.recording.source_session.journal.events[0].audio_sha256='0'.repeat(64);
 assert.throws(()=>model.validateDocument(forged),/does not match/);
 const next=setup();
 await next.get('wav-file').fire('change',{target:{files:[{name:'review.t2n',size:saved.blob.size,arrayBuffer:()=>saved.blob.arrayBuffer()}],value:'selected'}});
 assert.equal(next.get('source-session-note').hidden,false);
 assert.match(next.get('listen-status').textContent,/Notebook reopened/);
});

test('a damaged replacement session does not erase a previously checked session list',async()=>{
 const {archive}=await savedSessionZip(),h=setup();
 await h.get('session-zip-file').fire('change',{target:{files:[{name:'valid.zip',size:archive.byteLength,arrayBuffer:async()=>archive}],value:'valid'}});
 assert.equal(h.get('session-clip-list').children.length,1);
 await h.get('session-zip-file').fire('change',{target:{files:[{name:'damaged.zip',size:8,arrayBuffer:async()=>new ArrayBuffer(8)}],value:'damaged'}});
 assert.match(h.get('session-import-status').textContent,/previous checked session remains available/);
 assert.equal(h.get('session-clip-list').children.length,1);
});
