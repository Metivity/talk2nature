import test from 'node:test';
import assert from 'node:assert/strict';
import {WindowSession} from '../web/assets/window-model.mjs';
import {StationSession} from '../web/assets/station-model.mjs';
import {sessionFiles,zipFiles} from '../web/assets/station-export.mjs';
import {MAX_BUNDLE_BYTES,readBundleFiles,openSessionBundle,sessionSummary,comparisonWarnings,SessionSlot} from '../web/assets/session-import.mjs';
const feed=(s,seconds,value=0)=>{for(let i=0;i<seconds*10;i++)s.push(new Float32Array(s.sampleRate/10).fill(value));};
const encode=x=>new TextEncoder().encode(JSON.stringify(x));
async function fixture({window=true,seconds=30,discard=false,origin='synthetic'}={}){
  const s=new (window?WindowSession:StationSession)(8000,{origin});feed(s,4);s.mark('observation','<img src=x onerror=alert(1)>');feed(s,1,.1);feed(s,seconds-5);s.stop();if(discard)s.discard(1);return sessionFiles(s,'Saved moment',{});
}
async function open(files){return openSessionBundle(await zipFiles(files).arrayBuffer());}
const edit=(files,fn)=>{const r=JSON.parse(new TextDecoder().decode(files[0].bytes));fn(r);return [{...files[0],bytes:encode(r)},...files.slice(1)];};
test('reopen complete, interrupted, empty and discarded windows without upgrading completeness',async()=>{
  const complete=await open(await fixture());assert.equal(sessionSummary(complete).kind,'Whole moment · complete');assert.equal(complete.clips.length,1);assert.equal(sessionSummary(complete).retainedSeconds,30);assert.match(complete.record.markers[0].note,/<img/);
  const partial=await open(await fixture({seconds:9}));assert.match(sessionSummary(partial).kind,/partial/);assert.equal(partial.record.sampling.complete,false);
  const discarded=await open(await fixture({discard:true}));assert.match(sessionSummary(discarded).kind,/no retained/);assert.equal(sessionSummary(discarded).discarded,1);assert.equal(discarded.record.sampling.complete,false);
  const empty=new WindowSession(8000);empty.stop();const opened=await open(await sessionFiles(empty));assert.equal(opened.clips.length,0);assert.equal(opened.record.duration_seconds,0);
});
test('legacy highlights reopen without animal context and retain reviewed source, notes and origin declarations',async()=>{
  const files=await fixture({window:false,origin:'microphone'}), changed=edit(files,r=>{delete r.animal_context;r.events[0].source_label='uncertain';r.events[0].notes='Caller unknown.';});
  const opened=await open(changed);assert.equal(sessionSummary(opened).kind,'Sound highlights');assert.equal(sessionSummary(opened).animal.group,'unknown');assert.equal(opened.record.origin,'microphone');assert.equal(opened.record.events[0].notes,'Caller unknown.');
});
test('missing, unexpected and duplicate files, paths and recompressed ZIP flags are rejected',async()=>{
  const files=await fixture();await assert.rejects(open(files.filter(f=>!f.name.endsWith('.wav'))),/missing|unexpected/);
  await assert.rejects(open([...files,{name:'surprise.txt',bytes:encode('extra')}]),/unexpected/);
  const buffer=await zipFiles(files).arrayBuffer(), view=new DataView(buffer), end=buffer.byteLength-22,central=view.getUint32(end+16,true);
  const compressed=buffer.slice(0);new DataView(compressed).setUint16(central+10,8,true);assert.throws(()=>readBundleFiles(compressed),/original/);
  const encrypted=buffer.slice(0);new DataView(encrypted).setUint16(central+8,1,true);assert.throws(()=>readBundleFiles(encrypted),/original/);
  const path=buffer.slice(0);new Uint8Array(path)[central+46]=47;assert.throws(()=>readBundleFiles(path),/filename/);
  const duplicate=buffer.slice(0), dv=new DataView(duplicate), second=central+46+view.getUint16(central+28,true);dv.setUint16(second+28,view.getUint16(central+28,true),true);new Uint8Array(duplicate).set(new Uint8Array(buffer,central+46,view.getUint16(central+28,true)),second+46);assert.throws(()=>readBundleFiles(duplicate),/duplicate/);
});
test('ZIP truncation, oversized input, overlapping files, altered payload and trailing bytes are rejected',async()=>{
  const buffer=await zipFiles(await fixture()).arrayBuffer(),v=new DataView(buffer),central=v.getUint32(buffer.byteLength-6,true);
  for(const size of [0,21,100,buffer.byteLength-1])assert.throws(()=>readBundleFiles(buffer.slice(0,size)));
  assert.throws(()=>readBundleFiles(new ArrayBuffer(MAX_BUNDLE_BYTES+1)),/27 MB/);
  const overlap=buffer.slice(0);new DataView(overlap).setUint32(central+42,1,true);assert.throws(()=>readBundleFiles(overlap),/layout/);
  const altered=buffer.slice(0);new Uint8Array(altered)[30+v.getUint16(26,true)]^=1;assert.throws(()=>readBundleFiles(altered),/damaged/);
  const trailing=new Uint8Array(buffer.byteLength+1);trailing.set(new Uint8Array(buffer));assert.throws(()=>readBundleFiles(trailing.buffer));
});
test('valid ZIP CRC does not substitute for the journal audio checksum or WAV consistency',async()=>{
  const files=await fixture();const corrupt=files.map(f=>({name:f.name,bytes:f.bytes.slice()}));corrupt[1].bytes[44]^=1;await assert.rejects(open(corrupt),/checksum/);
  const wrongRate=files.map(f=>({name:f.name,bytes:f.bytes.slice()}));new DataView(wrongRate[1].bytes.buffer).setUint32(24,16000,true);await assert.rejects(open(wrongRate),/mono audio/);
  await assert.rejects(open(edit(files,r=>r.events[0].samples++)),/length|timing/);
  await assert.rejects(open(edit(files,r=>delete r.events[0].audio_sha256)),/checksum/);
});
test('forged complete status, sample totals and missing discard history are rejected',async()=>{
  const partial=await fixture({seconds:18});await assert.rejects(open(edit(partial,r=>r.sampling.complete=true)),/complete/);
  await assert.rejects(open(edit(partial,r=>r.sampling.processed_samples++)),/sample counts/);
  const discarded=await fixture({discard:true});await assert.rejects(open(edit(discarded,r=>r.discarded_events=[])),/discarded record/);
  await assert.rejects(open(edit(partial,r=>r.status='running')),/unsupported/);
});
test('out-of-session notes, invalid declarations and unbounded metadata are rejected',async()=>{
  const files=await fixture();
  for(const change of [r=>r.markers[0].at_seconds=31,r=>r.markers[0].provenance='ai-inferred',r=>r.markers[0].note='x'.repeat(301),r=>r.origin='translated',r=>r.animal_context.basis='identified'])await assert.rejects(open(edit(files,change)));
  await assert.rejects(open(edit(files,r=>r.extra='x'.repeat(262144))),/small original journal/);
});
test('comparison flags duplicate observations, partial audio, mode, origin, setup and context differences',async()=>{
  const a=await open(await fixture());assert.match(comparisonWarnings(a,a).join(' '),/copies of the same/);
  const b=await open(await fixture({window:false,seconds:18,origin:'microphone'}));const warnings=comparisonWarnings(a,b).join(' ');
  for(const text of ['invented example','Different recording modes','Different observed durations','context is missing','settings differ','not controlled'])assert.ok(warnings.includes(text),text);
  const discarded=await open(await fixture({discard:true}));assert.match(comparisonWarnings(a,discarded).join(' '),/discarded audio/);
});
test('failed replacement preserves the open session; stale and cancelled loads cannot replace it',async()=>{
  const slot=new SessionSlot();await slot.open(async()=>({name:'original'}));await assert.rejects(slot.open(async()=>{throw Error('bad file');}));assert.equal(slot.value.name,'original');
  let resolve;const slow=slot.open(()=>new Promise(r=>resolve=r));await slot.open(async()=>({name:'newer'}));resolve({name:'older'});assert.equal(await slow,false);assert.equal(slot.value.name,'newer');
  let finish;const pending=slot.open(()=>new Promise(r=>finish=r));slot.clear();finish({name:'cancelled'});assert.equal(await pending,false);assert.equal(slot.value,null);
  let reject;const stale=slot.open(()=>new Promise((_,r)=>reject=r));await slot.open(async()=>({name:'latest'}));reject(Error('stale failure'));assert.equal(await stale,false);assert.equal(slot.value.name,'latest');
});

test('real file-change UI keeps a valid session after a bad replacement and renders notes as text',async()=>{
  class Element {
    constructor(tag='div'){this.tag=tag;this.children=[];this.listeners={};this.textContent='';this.hidden=false;this.files=[];this.value='';this.paused=true;}
    append(...nodes){this.children.push(...nodes);} replaceChildren(...nodes){this.children=nodes;this.textContent='';}
    addEventListener(name,fn){this.listeners[name]=fn;} removeAttribute(name){delete this[name];}
    pause(){this.paused=true;} load(){} focus(){} scrollIntoView(){}
  }
  const elements=new Map(),get=id=>{if(!elements.has(id))elements.set(id,new Element());return elements.get(id);};
  const text=e=>[e.textContent,...e.children.map(text)].join(' ');
  globalThis.document={getElementById:get,createElement:tag=>new Element(tag),addEventListener(){}};
  const lifecycle={};globalThis.window={addEventListener:(name,fn)=>lifecycle[name]=fn};
  try{
    await import('../web/assets/compare.js?test-ui');
    const files=await fixture(),blob=zipFiles(files),buffer=await blob.arrayBuffer();
    get('file-a').files=[{size:blob.size,arrayBuffer:async()=>buffer}];get('file-a').listeners.change();
    for(let i=0;i<100 && get('status-a').textContent.startsWith('Checking');i++)await new Promise(r=>setTimeout(r,2));
    assert.match(get('status-a').textContent,/Opened locally/);assert.match(text(get('content-a')),/<img src=x onerror=alert\(1\)>/);assert.equal(get('title-a').textContent,'Saved moment');
    const button=get('content-a').children.find(e=>e.tag==='ol').children[0].children.find(e=>e.tag==='button');button.listeners.click();assert.equal(get('compare-player').paused,true);assert.ok(get('compare-player').src.startsWith('blob:'));
    get('file-a').files=[{size:7,arrayBuffer:async()=>new ArrayBuffer(7)}];get('file-a').listeners.change();
    for(let i=0;i<100 && get('status-a').textContent.startsWith('Checking');i++)await new Promise(r=>setTimeout(r,2));
    assert.match(get('status-a').textContent,/previous session is still open/);assert.equal(get('title-a').textContent,'Saved moment');assert.match(text(get('content-a')),/<img/);
    get('clear-a').listeners.click();assert.equal(get('compare-player').src,undefined);assert.equal(get('compare-player-panel').hidden,true);assert.equal(get('compare-results').hidden,true);
    await get('compare-example').listeners.click();assert.match(text(get('summary-a')),/complete/);assert.match(text(get('summary-b')),/partial/);assert.equal(get('compare-results').hidden,false);
    lifecycle.pagehide();assert.equal(get('compare-results').hidden,true);assert.equal(get('details-a').hidden,true);assert.equal(get('details-b').hidden,true);
  }finally{delete globalThis.document;delete globalThis.window;}
});
