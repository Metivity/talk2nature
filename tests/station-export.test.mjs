import test from 'node:test';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {StationSession} from '../web/assets/station-model.mjs';
import {sessionFiles, zipFiles} from '../web/assets/station-export.mjs';

test('one archive preserves journal, Unicode notes, exact WAV hashes and discarded provenance', async () => {
  const s = new StationSession(8000);
  for (let i=0;i<100;i++) s.push(new Float32Array(800).fill(i>=40&&i<45||i>=70&&i<75 ? .2 : .00001));
  s.mark('observation','ציפור · synthetic example'); s.stop();
  assert.equal(s.events.length,2); s.discard(s.events[1].id);
  s.review(s.events[0].id,'other','Invented tone');
  const files=await sessionFiles(s,'rehearsal',{}), archive=zipFiles(files);
  const result=spawnSync('python3',['-c',`
import sys,io,zipfile,json,hashlib,wave
z=zipfile.ZipFile(io.BytesIO(sys.stdin.buffer.read()))
assert z.testzip() is None
assert len(z.namelist())==3
r=json.loads(z.read(next(n for n in z.namelist() if n.endswith('.json'))))
assert r['origin']=='synthetic' and r['status']=='stopped'
assert r['markers'][0]['note']=='ציפור · synthetic example'
assert len(r['discarded_events'])==1
e=r['events'][0]; audio=z.read(e['audio_filename'])
assert hashlib.sha256(audio).hexdigest()==e['audio_sha256']
with wave.open(io.BytesIO(audio)) as w:
 assert w.getframerate()==8000 and w.getnframes()==e['samples']
assert b'not encrypted' in z.read('READ-ME.txt')
`],{input:Buffer.from(await archive.arrayBuffer())});
  assert.equal(result.status,0,result.stderr.toString());
});

test('export requires stopped session and alias; empty sessions still save a journal', async () => {
  const s=new StationSession(8000);
  await assert.rejects(sessionFiles(s,'place',{}),/Stop/); s.stop();
  await assert.rejects(sessionFiles(s,'  ',{}),/alias/);
  const files=await sessionFiles(s,'place',{});
  assert.equal(files.length,2); assert.equal(JSON.parse(new TextDecoder().decode(files[0].bytes)).events.length,0);
});

test('ZIP rejects path traversal, duplicate names and unbounded input', () => {
  const file=name=>({name,bytes:new Uint8Array(2)});
  for(const name of ['../clip.wav','/clip.wav','dir/clip.wav','x\\clip.wav']) assert.throws(()=>zipFiles([file(name)]),/Invalid/);
  assert.throws(()=>zipFiles([file('a'),file('a')]),/Invalid/);
  assert.throws(()=>zipFiles(Array.from({length:27},(_,i)=>file(String(i)))),/count/);
  assert.throws(()=>zipFiles([{name:'large',bytes:new Uint8Array(26*1048576+1)}]),/size/);
});

test('export snapshots review and audio before awaiting hashes', async () => {
  const s=new StationSession(8000);
  for(let i=0;i<60;i++) s.push(new Float32Array(800).fill(i>=40&&i<45?.2:.00001));
  s.stop(); let release;
  const pending=sessionFiles(s,'place',{},()=>new Promise(resolve=>{release=resolve;}));
  s.discard(s.events[0].id); release(new Uint8Array(32).buffer);
  const files=await pending, record=JSON.parse(new TextDecoder().decode(files[0].bytes));
  assert.equal(record.events.length,1); assert.equal(record.discarded_events.length,0); assert.equal(files.length,3);
});
