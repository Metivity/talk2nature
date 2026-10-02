import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {webcrypto} from 'node:crypto';
import * as model from '../web/assets/listen-model.mjs';
import * as notebook from '../web/assets/notebook.mjs';

// Execute the real event handlers with a small DOM facade. This checks whether
// user drafts are lost or omitted, separately from annotation-format tests.
function setup() {
  const elements=new Map(), windowEvents={}, downloads=[];
  const defaults={'event-start':'0','event-end':'1','event-kind':'uncertain','event-context':'unknown','event-source':'not observed','event-confidence':'uncertain','event-notes':''};
  const harness={confirm:false,confirmations:0,focus:null};
  function element(id='') {
    return {id,value:defaults[id]??'',textContent:'',hidden:false,open:false,disabled:false,handlers:{},children:[],clientWidth:600,
      addEventListener(name,fn){this.handlers[name]=fn;},
      async fire(name,event={}){return await this.handlers[name]?.(event);},
      append(...nodes){this.children.push(...nodes);},replaceChildren(...nodes){this.children=nodes;},
      setAttribute(){},removeAttribute(){},pause(){},load(){},remove(){},
      focus(){harness.focus=id;},click(){downloads.push(this.download);},
      reset(){for(const [id,value] of Object.entries(defaults)) get(id).value=value;},
      getContext(){return {scale(){},fillRect(){},beginPath(){},moveTo(){},lineTo(){},stroke(){}};}
    };
  }
  const get=id=>{if(!elements.has(id))elements.set(id,element(id));return elements.get(id);};
  const document={getElementById:get,createElement:()=>element(),body:element()};
  const window={devicePixelRatio:1,confirm(){harness.confirmations++;return harness.confirm;},addEventListener(name,fn){windowEvents[name]=fn;}};
  const source=fs.readFileSync(new URL('../web/assets/listen.js',import.meta.url),'utf8').replace(/^import .*;\n/gm,'');
  vm.runInNewContext(source,{...model,...notebook,document,window,crypto:webcrypto,Blob,structuredClone,URL:{createObjectURL:()=> 'blob:synthetic',revokeObjectURL(){}},setTimeout(){}});
  return {...harness,get,downloads,windowEvents,state:harness,async type(id,value){get(id).value=value;await get('event-form').fire('input');}};
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
  await h.get('export-json').fire('click');await h.get('export-csv').fire('click');await h.get('save-notebook').fire('click');
  assert.equal(h.downloads.length,0);assert.equal(h.state.focus,'save-event');
  assert.match(h.get('export-status').textContent,/unfinished/);
  await h.get('event-form').fire('submit',{preventDefault(){}});
  assert.match(h.get('event-count').textContent,/1 event/);
  await h.get('export-json').fire('click');assert.deepEqual(h.downloads,['talk2nature-labels.json']);
  // A requested download is not proof that the browser saved it.
  let warned=false;h.windowEvents.beforeunload({preventDefault(){warned=true;}});assert.ok(warned);
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
