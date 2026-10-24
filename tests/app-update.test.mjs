import test from 'node:test';
import assert from 'node:assert/strict';
import {announceWaitingUpdate,watchWaitingWorker} from '../web/assets/app-update.mjs';

test('a waiting update uses the global notice without replacing offline readiness',()=>{
  const notice={hidden:true,textContent:''};
  const offline={textContent:'Offline tools are ready on this browser.'};
  announceWaitingUpdate(notice,offline);
  assert.equal(notice.hidden,false);
  assert.match(notice.textContent,/Update ready/);
  assert.equal(offline.textContent,'Offline tools are ready on this browser.');
});

test('offline status is the fallback when no global update notice exists',()=>{
  const offline={textContent:'Checking offline availability…'};
  announceWaitingUpdate(null,offline);
  assert.match(offline.textContent,/Update ready/);
});

test('an already-waiting worker is announced once without mutating registration state',()=>{
  const waiting={state:'installed'}, registration=new EventTarget(), ready=[];
  registration.waiting=waiting; registration.installing=null;
  watchWaitingWorker(registration,worker=>ready.push(worker));
  assert.deepEqual(ready,[waiting]);
  assert.equal(registration.waiting,waiting);
  assert.equal(waiting.state,'installed');
});

test('a newly-installed worker is reported once after updatefound',()=>{
  const registration=new EventTarget(), ready=[];
  registration.waiting=null; registration.installing=null;
  watchWaitingWorker(registration,worker=>ready.push(worker));
  const installing=new EventTarget(); installing.state='installing';
  registration.installing=installing;
  registration.dispatchEvent(new Event('updatefound'));
  installing.state='installed'; registration.waiting=installing;
  installing.dispatchEvent(new Event('statechange'));
  installing.dispatchEvent(new Event('statechange'));
  assert.deepEqual(ready,[installing]);
  assert.equal(registration.waiting,installing);
});
