import test from 'node:test';
import assert from 'node:assert/strict';
import {WindowSession} from '../web/assets/window-model.mjs';
import {sessionFiles, zipFiles} from '../web/assets/station-export.mjs';
import {readWav} from '../web/assets/listen-model.mjs';
import {spawnSync} from 'node:child_process';

test('a full window retains quiet samples, starts at zero and trims exactly at 30 seconds', async () => {
  const s = new WindowSession(8000, {animalContext:{group:'parrot',species:'budgerigar',basis:'observer-declared'}});
  // Irregular frames intentionally cross the exact boundary; no duplicated or trailing samples.
  for (let n=0;n<240000;n+=777) s.push(Float32Array.from({length:777},(_,i)=>(n+i)%2 ? .25 : 0));
  assert.equal(s.elapsed,30); assert.equal(s.stopReason,'window_complete'); assert.equal(s.events.length,1);
  const r=s.exportRecord();assert.equal(r.schema,'talk2nature.observation-window.v1');
  assert.equal(r.sampling.complete,true);assert.equal(r.sampling.retained_samples,240000);
  assert.equal(r.events[0].onset_seconds,null);assert.equal(r.events[0].clip_start_seconds,0);
  assert.equal(r.animal_context.species,'budgerigar');assert.equal('detector' in r,false);
  assert.equal('marker_windows' in r,false);assert.deepEqual(s.markerWindows(),[]);
  assert.equal(s.events[0].pcm[0],0);assert.equal(s.events[0].pcm[1],8192);
  const files=await sessionFiles(s,'rehearsal',{}), archive=zipFiles(files);
  const result=spawnSync('python3',['-c',`
import sys,io,zipfile,json,hashlib,wave
z=zipfile.ZipFile(io.BytesIO(sys.stdin.buffer.read()));assert z.testzip() is None
r=json.loads(z.read(next(n for n in z.namelist() if n.endswith('.json'))))
e=r['events'][0];b=z.read(e['audio_filename'])
assert hashlib.sha256(b).hexdigest()==e['audio_sha256']
assert r['sampling']['complete'] and r['origin']=='synthetic'
with wave.open(io.BytesIO(b)) as w: assert w.getnframes()==240000 and w.getframerate()==8000
`],{input:Buffer.from(await archive.arrayBuffer())});assert.equal(result.status,0,result.stderr.toString());
  assert.equal(readWav(files[1].bytes.buffer).duration,30);
});

test('digital silence is retained and is not mislabeled as a detected animal', () => {
  const s=new WindowSession(8000);
  for(let i=0;i<300;i++)s.push(new Float32Array(800));
  assert.equal(s.exportRecord().sampling.complete,true);assert.equal(s.events[0].source_label,'unreviewed');
  assert.ok(s.events[0].pcm.every(x=>x===0));assert.equal(s.events[0].kind,'observation_window');
});

test('interruption, early stop, quota and discard cannot masquerade as complete windows', () => {
  for(const reason of ['backgrounded','user_stop','window_timeout','no_audio','capture_error']) {
    const s=new WindowSession(8000);s.push(new Float32Array(800).fill(.1));s.mark('observation','Moved');s.stop(reason);
    assert.equal(s.exportRecord().sampling.complete,false);assert.equal(s.elapsed,.1);
    assert.equal(s.exportRecord().markers[0].note,'Moved');assert.equal(s.stopReason,reason);
    assert.equal(s.push(new Float32Array(800)),null);assert.throws(()=>s.mark('observation'));
  }
  const quota=new WindowSession(8000,{maxBytes:101});quota.push(new Float32Array(800));
  assert.equal(quota.events[0].pcm.length,50);assert.equal(quota.stopReason,'storage_limit');assert.equal(quota.exportRecord().sampling.complete,false);
  const full=new WindowSession(8000);for(let i=0;i<300;i++)full.push(new Float32Array(800));
  full.review(1,'uncertain','quiet or distant');full.discard(1);
  const r=full.exportRecord();assert.equal(r.sampling.complete,false);assert.equal(r.sampling.retained_samples,0);
  assert.equal(r.discarded_events.length,1);assert.equal(full.bytes,0);assert.ok(!JSON.stringify(r).includes('quiet or distant'));
});

test('invalid frames fail before ingestion; empty and interrupted windows retain truthful metadata', async () => {
  const s=new WindowSession(8000);assert.throws(()=>s.push(new Float32Array([0,NaN])));
  assert.equal(s.samplesSeen,0);assert.throws(()=>s.push(new Float32Array(1601)));assert.throws(()=>new WindowSession(8000,{maxBytes:1}));
  s.stop('window_complete');assert.equal(s.stopReason,'capture_error');assert.equal(s.exportRecord().sampling.complete,false);
  assert.equal((await sessionFiles(s,'empty',{})).length,2);
});
