import test from 'node:test';
import assert from 'node:assert/strict';
import {StationSession} from '../web/assets/station-model.mjs';
import {sessionFiles,zipFiles} from '../web/assets/station-export.mjs';
import {openSessionBundle,validateSessionJournal} from '../web/assets/session-import.mjs';

const feed=(session,seconds,value=0)=>{for(let i=0;i<seconds*10;i++)session.push(new Float32Array(session.sampleRate/10).fill(value));};
const encode=value=>new TextEncoder().encode(JSON.stringify(value,null,2)+'\n');

async function nativeBundle({duration=3600,max=3600}={}) {
  const session=new StationSession(8000,{origin:'microphone'});
  feed(session,4);feed(session,1,.1);feed(session,1);session.stop();
  const files=await sessionFiles(session,'Android field station',{});
  const record=JSON.parse(new TextDecoder().decode(files[0].bytes));
  record.schema='talk2nature.station.v2';
  record.duration_seconds=duration;
  record.detector.max_session_seconds=max;
  record.audio_settings={sampleRate:8000,channelCount:1,source:'device microphone',processing:'not reported'};
  files[0]={...files[0],bytes:encode(record)};
  return {files,record};
}

test('native v2 session imports through the existing review bundle path',async()=>{
  const {files}=await nativeBundle();
  const opened=await openSessionBundle(await zipFiles(files).arrayBuffer());
  assert.equal(opened.record.schema,'talk2nature.station.v2');
  assert.equal(opened.record.duration_seconds,3600);
  assert.equal(opened.record.events.length,1);
  assert.equal(opened.record.origin,'microphone');
});

test('native v2 stays inside its declared schedule and the eight-hour cap',async()=>{
  const valid=await nativeBundle({duration:14400,max:14400});
  assert.equal(validateSessionJournal(valid.record).duration_seconds,14400);

  const beyondSchedule=await nativeBundle({duration:3601,max:3600});
  assert.throws(()=>validateSessionJournal(beyondSchedule.record),/settings|supported/);

  const beyondCap=await nativeBundle({duration:28801,max:28801});
  assert.throws(()=>validateSessionJournal(beyondCap.record),/recording settings|supported/);
});
