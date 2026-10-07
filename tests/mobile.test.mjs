import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import vm from 'node:vm';

async function worker({failInstall=false}={}) {
  const scope='/talk2nature/app/', origin='https://fixture.test';
  const paths=[scope,scope+'station/',scope+'review/',scope+'compare/','/talk2nature/assets/station.js?v=fixture'];
  const handlers={}, stores=new Map(), fetches=[], adds=[];
  const old='talk2nature-shell:'+scope+':old', unrelated='another-project-cache';
  stores.set(old,new Map()); stores.set(unrelated,new Map());
  const caches={
    async open(key) { if(!stores.has(key))stores.set(key,new Map()); const items=stores.get(key); return {
      async addAll(requests) { for(const request of requests){adds.push(request);if(failInstall)throw Error('network');items.set(request.url,new Response('cached '+request.url));} },
      async match(url) {return items.get(String(url))?.clone();}
    }; },
    async keys(){return [...stores.keys()];}, async delete(key){return stores.delete(key);}
  };
  const self={location:{origin},clients:{claim:async()=>{}},addEventListener:(name,fn)=>handlers[name]=fn};
  const source=(await readFile(new URL('../web/templates/app-sw.js',import.meta.url),'utf8')).replace('__REVISION__','new').replace('__ASSETS__',JSON.stringify(paths)).replace('__SCOPE__',JSON.stringify(scope));
  vm.runInNewContext(source,{self,caches,URL,Request,Set,Promise,fetch:async request=>{fetches.push(request.url);return new Response('network');}});
  const dispatch=async(name,extra={})=>{let completion,response;handlers[name]({...extra,waitUntil:p=>completion=p,respondWith:p=>response=p});await completion;return response;};
  return {dispatch,stores,fetches,adds,paths,scope,origin,old,unrelated,key:'talk2nature-shell:'+scope+':new'};
}
test('offline shell install omits credentials and activation preserves unrelated caches',async()=>{
  const w=await worker();await w.dispatch('install');await w.dispatch('activate');
  assert.equal(w.adds.length,w.paths.length);assert.ok(w.adds.every(r=>r.credentials==='omit'));
  assert.equal(w.stores.has(w.old),false);assert.equal(w.stores.has(w.unrelated),true);
  const result=await w.dispatch('fetch',{request:new Request(w.origin+w.scope+'station/?mode=companion')});
  assert.match(await result.text(),/^cached/);assert.equal(w.fetches.length,0);
  const parrot=await w.dispatch('fetch',{request:new Request(w.origin+w.scope+'station/?mode=parrot')});
  assert.match(await parrot.text(),/^cached/);assert.equal(w.fetches.length,0);
});
test('private, unknown, authenticated, query-bearing and mutation requests bypass the offline cache',async()=>{
  const w=await worker();await w.dispatch('install');
  for(const request of [
    new Request(w.origin+'/admin/observations'),new Request(w.origin+w.scope+'private/'),
    new Request(w.origin+w.scope,{method:'POST',body:'private'}),
    new Request(w.origin+w.scope,{headers:{authorization:'Bearer test-only'}}),
    new Request(w.origin+w.scope+'?token=private'),new Request(w.origin+w.scope+'compare/?file=private'),new Request(w.origin+w.scope+'station/?mode=companion&note=private'),
    new Request('https://other.test'+w.scope)
  ]) assert.equal(await w.dispatch('fetch',{request}),undefined);
  assert.equal(w.fetches.length,0);
});
test('missing cached asset falls back to network without persisting runtime response',async()=>{
  const w=await worker();await w.dispatch('install');const url=w.origin+w.scope;
  w.stores.get(w.key).delete(url);
  const response=await w.dispatch('fetch',{request:new Request(url)});
  assert.equal(await response.text(),'network');assert.deepEqual(w.fetches,[url]);assert.equal(w.stores.get(w.key).has(url),false);
});
test('readiness checks every file and failed installation removes only the incomplete new cache',async()=>{
  const w=await worker();await w.dispatch('install');let result;
  const extra={data:{type:'SHELL_STATUS'},ports:[{postMessage:value=>result=value}]};
  await w.dispatch('message',extra);assert.equal(result.ready,true);
  w.stores.get(w.key).delete(w.origin+w.paths[0]);await w.dispatch('message',extra);assert.equal(result.ready,false);
  const broken=await worker({failInstall:true});await assert.rejects(broken.dispatch('install'),/network/);
  assert.equal(broken.stores.has(broken.key),false);assert.equal(broken.stores.has(broken.old),true);assert.equal(broken.stores.has(broken.unrelated),true);
});


test('only the exact release asset query is served from the public offline cache',async()=>{
  const w=await worker();await w.dispatch('install');
  const path='/talk2nature/assets/station.js';
  const good=await w.dispatch('fetch',{request:new Request(w.origin+path+'?v=fixture')});
  assert.match(await good.text(),/^cached/);
  for(const suffix of ['', '?v=old', '?v=fixture&token=private', '?v=fixture&v=fixture'])
    assert.equal(await w.dispatch('fetch',{request:new Request(w.origin+path+suffix)}),undefined);
  assert.equal(await w.dispatch('fetch',{request:new Request(w.origin+w.scope+'station/?mode=demo&mode=companion')}),undefined);
});

test('comparison page is part of the exact public offline shell',async()=>{const w=await worker();await w.dispatch('install');const r=await w.dispatch('fetch',{request:new Request(w.origin+w.scope+'compare/')});assert.match(await r.text(),/^cached/);assert.equal(w.fetches.length,0);});
