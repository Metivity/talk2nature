import test from 'node:test';
import assert from 'node:assert/strict';
import {announceWaitingUpdate,resolveRedundantWorker,watchWaitingWorker} from '../web/assets/app-update.mjs';

const updateMessage='A new version is ready. Save any moment you want to keep, close all Talk2Nature tabs or windows, then reopen the app.';

test('a waiting update uses the global notice without replacing offline readiness',()=>{
  const notice={hidden:true,textContent:''};
  const offline={textContent:'Offline tools are ready on this browser.'};
  announceWaitingUpdate(notice,offline);
  assert.equal(notice.hidden,false);
  assert.equal(notice.textContent,updateMessage);
  assert.equal(offline.textContent,'Offline tools are ready on this browser.');
});

test('offline status is the fallback when no global update notice exists',()=>{
  const offline={textContent:'Checking offline availability…'};
  announceWaitingUpdate(null,offline);
  assert.equal(offline.textContent,updateMessage);
});

test('a replaced worker keeps the verified active offline shell status',async()=>{
  const active={};
  assert.deepEqual(await resolveRedundantWorker({active},async worker=>worker===active),{
    message:'Offline tools are ready on this browser.',
    button:'Check for app updates'
  });
});

test('a missing active shell offers repair without claiming offline readiness',async()=>{
  assert.deepEqual(await resolveRedundantWorker({active:{}},async()=>false),{
    message:'Offline files are missing. Reconnect and use Enable offline tools to repair them.',
    button:'Enable offline tools'
  });
});

test('a failed first install explains that offline setup did not complete',async()=>{
  assert.deepEqual(await resolveRedundantWorker({active:null},()=>{throw Error('must not run');}),{
    message:'Offline setup did not complete. Check your connection and storage, then try again.',
    button:'Enable offline tools'
  });
});

test('a failed readiness probe degrades to repair guidance rather than an unhandled error',async()=>{
  assert.deepEqual(await resolveRedundantWorker({active:{}},async()=>{throw Error('probe failed');}),{
    message:'Offline files are missing. Reconnect and use Enable offline tools to repair them.',
    button:'Enable offline tools'
  });
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
