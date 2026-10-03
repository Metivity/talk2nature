import {validateAnimal, unknownAnimal} from './animal-model.mjs';

export const MAX_BUNDLE_BYTES = 27 * 1048576;
const fail = message => { throw Error(message); };
const check = (condition, message) => { if (!condition) fail(message); };
const object = x => x !== null && typeof x === 'object' && !Array.isArray(x);
const finite = (x, min, max) => Number.isFinite(x) && x >= min && x <= max;
const integer = (x, min, max) => Number.isInteger(x) && finite(x, min, max);
const short = (x, max) => typeof x === 'string' && x.length <= max;
const decode = bytes => new TextDecoder('utf-8', {fatal:true}).decode(bytes);
const near = (a,b) => Math.abs(a-b) <= .00021;
const uuid = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/;
function crc32(bytes) {
  let crc=0xffffffff;
  for (const byte of bytes) {
    crc ^= byte;
    for(let n=0;n<8;n++) crc=(crc>>>1) ^ (crc&1 ? 0xedb88320 : 0);
  }
  return (crc^0xffffffff)>>>0;
}

// Read only our bounded, flat, uncompressed export format. Never extract paths.
export function readBundleFiles(buffer) {
  check(buffer instanceof ArrayBuffer && buffer.byteLength >= 22 && buffer.byteLength <= MAX_BUNDLE_BYTES, 'Choose a Talk2Nature session ZIP smaller than 27 MB.');
  const bytes=new Uint8Array(buffer), v=new DataView(buffer), end=bytes.length-22;
  const u16=p=>v.getUint16(p,true), u32=p=>v.getUint32(p,true);
  check(u32(end)===0x06054b50 && u16(end+4)===0 && u16(end+6)===0 && u16(end+20)===0, 'This is not an original Talk2Nature session ZIP.');
  const count=u16(end+10), central=u32(end+16);
  check(integer(count,2,26) && count===u16(end+8) && central+u32(end+12)===end, 'The session ZIP directory is incomplete.');
  const files=new Map(); let p=central, local=0, total=0;
  for(let i=0;i<count;i++) {
    check(p+46<=end && u32(p)===0x02014b50, 'The session ZIP directory is damaged.');
    const nameLength=u16(p+28), size=u32(p+24), crc=u32(p+16);
    check(u16(p+8)===0 && u16(p+10)===0 && u16(p+30)===0 && u16(p+32)===0 && u16(p+34)===0 && u32(p+20)===size && p+46+nameLength<=end, 'Use the original Save session ZIP, without recompressing it.');
    const name=decode(bytes.subarray(p+46,p+46+nameLength));
    check(/^[a-zA-Z0-9][a-zA-Z0-9_.-]{0,119}$/.test(name) && !files.has(name), 'The ZIP contains an unexpected or duplicate filename.');
    check(u32(p+42)===local && local+30+nameLength+size<=central && u32(local)===0x04034b50, 'The ZIP contains an invalid file layout.');
    check(u16(local+6)===0 && u16(local+8)===0 && u32(local+14)===crc && u32(local+18)===size && u32(local+22)===size && u16(local+26)===nameLength && u16(local+28)===0 && decode(bytes.subarray(local+30,local+30+nameLength))===name, 'The ZIP file headers disagree.');
    total+=size; check(total<=26*1048576,'This session exceeds the supported size.');
    const data=bytes.subarray(local+30+nameLength,local+30+nameLength+size);
    check(crc32(data)===crc,'A file in this session is damaged. Try the original saved copy.');
    files.set(name,data); local+=30+nameLength+size; p+=46+nameLength;
  }
  check(p===end && local===central,'The ZIP contains unexpected extra data.');
  return files;
}

function validateJournal(r) {
  check(object(r) && ['talk2nature.station.v1','talk2nature.observation-window.v1'].includes(r.schema),'Choose a Station Save session ZIP. Sound desk notebooks and loose recordings use Review.');
  const window=r.schema==='talk2nature.observation-window.v1';
  check(r.status==='stopped' && ['synthetic','microphone'].includes(r.origin) && uuid.test(r.session_id) && short(r.station_alias,80) && r.station_alias.trim() && short(r.started_at_utc,40) && /^\d{4}-\d\d-\d\dT/.test(r.started_at_utc) && Number.isFinite(Date.parse(r.started_at_utc)) && short(r.clock,200) && short(r.tool_version,40) && short(r.stop_reason,80),'The saved session details are incomplete or unsupported.');
  check(integer(r.sample_rate,8000,96000) && finite(r.duration_seconds,0,window?30:300.2) && finite(r.near_full_scale_fraction,0,1) && object(r.audio_settings),'The session recording settings are invalid.');
  if (r.animal_context!==undefined) validateAnimal(r.animal_context);
  check(Array.isArray(r.events) && r.events.length<=(window?1:24) && Array.isArray(r.discarded_events) && r.discarded_events.length<=(window?1:1000) && Array.isArray(r.markers) && r.markers.length<=100,'The session has too many or missing observations.');
  const ids=new Set(); let audioBytes=0;
  for(const e of r.events) {
    check(object(e) && integer(e.id,1,2000) && !ids.has(e.id) && finite(e.clip_start_seconds,0,r.duration_seconds) && finite(e.clip_end_seconds,e.clip_start_seconds,r.duration_seconds+.0001) && integer(e.samples,1,30*r.sample_rate) && near(e.samples/r.sample_rate,e.clip_end_seconds-e.clip_start_seconds) && finite(e.peak,0,1) && ['unreviewed','person','animal','other','uncertain'].includes(e.source_label) && short(e.notes,300) && short(e.ended_by,80),'A retained recording has inconsistent timing or details.');
    ids.add(e.id); audioBytes+=e.samples*2;
    const expected=`talk2nature-${r.session_id}-${window?'window':`event-${e.id}`}.wav`;
    check(e.audio_filename===expected && /^[0-9a-f]{64}$/.test(e.audio_sha256),'A recording is missing its filename or checksum.');
    if(window) check(e.id===1 && e.kind==='observation_window' && e.onset_seconds===null && e.clip_start_seconds===0 && near(e.clip_end_seconds,r.duration_seconds) && e.ended_by===r.stop_reason,'This observation window is inconsistent.');
    else check(finite(e.onset_seconds,e.clip_start_seconds,e.clip_end_seconds) && finite(e.last_loud_seconds,e.onset_seconds,e.clip_end_seconds) && finite(e.threshold_dbfs,-100,0) && e.samples/r.sample_rate<=6.21,'A sound highlight has invalid timing.');
  }
  check(audioBytes<=24*1048576,'The session audio exceeds its limit.');
  for(const e of r.discarded_events) {
    check(object(e) && integer(e.id,1,2000) && !ids.has(e.id) && e.discarded===true && (window? e.id===1 && e.onset_seconds===null : finite(e.onset_seconds,0,r.duration_seconds)),'The session discard history is inconsistent.'); ids.add(e.id);
  }
  r.markers.forEach((m,i)=>check(object(m) && m.id===i+1 && finite(m.at_seconds,0,r.duration_seconds) && (i===0 || m.at_seconds>=r.markers[i-1].at_seconds) && ['person_voice','observation'].includes(m.kind) && m.provenance==='user-entered' && short(m.note,300),'An observation note has invalid timing or provenance.'));
  if(window) {
    const s=r.sampling;
    check(object(s) && s.method==='user_started_fixed_window' && s.requested_seconds===30 && integer(s.processed_samples,0,30*r.sample_rate) && near(s.processed_samples/r.sample_rate,r.duration_seconds) && s.retained_samples===(r.events[0]?.samples||0) && (!r.events.length || s.retained_samples===s.processed_samples) && typeof s.complete==='boolean','The window sample counts are inconsistent.');
    const complete=r.events.length===1 && r.stop_reason==='window_complete' && s.processed_samples===30*r.sample_rate;
    check(s.complete===complete && (r.stop_reason!=='window_complete' || s.processed_samples===30*r.sample_rate),'This session incorrectly claims a complete window.');
    check(r.events.length+r.discarded_events.length===(s.processed_samples?1:0),'The window is missing its retained or discarded record.');
  } else {
    const d=r.detector;
    check(object(d) && d.type==='energy_threshold' && d.calibration_seconds===3 && finite(d.margin_db,6,24) && (d.threshold_dbfs===null||finite(d.threshold_dbfs,-50,-3)) && d.pre_roll_seconds===1 && d.max_clip_seconds_approx===6 && d.max_session_seconds===300,'The sound-highlights settings are unsupported.');
  }
  return r;
}
function checkWav(bytes, event, rate) {
  check(bytes?.length===44+event.samples*2,'A recording is missing or its length has changed.');
  const v=new DataView(bytes.buffer,bytes.byteOffset,bytes.byteLength), tag=(p,n)=>decode(bytes.subarray(p,p+n));
  check(tag(0,4)==='RIFF' && v.getUint32(4,true)===bytes.length-8 && tag(8,8)==='WAVEfmt ' && v.getUint32(16,true)===16 && v.getUint16(20,true)===1 && v.getUint16(22,true)===1 && v.getUint32(24,true)===rate && v.getUint32(28,true)===rate*2 && v.getUint16(32,true)===2 && v.getUint16(34,true)===16 && tag(36,4)==='data' && v.getUint32(40,true)===event.samples*2,'A recording does not match the saved mono audio format.');
}
export async function openSessionBundle(buffer, digest=bytes=>crypto.subtle.digest('SHA-256',bytes)) {
  const files=readBundleFiles(buffer), journals=[...files.keys()].filter(n=>n.endsWith('.json'));
  check(journals.length===1 && files.get(journals[0]).length<=262144,'The session needs one small original journal.');
  let parsed; try { parsed=JSON.parse(decode(files.get(journals[0]))); } catch { fail('The saved session journal could not be read.'); }
  const record=validateJournal(parsed);
  check(journals[0]===`talk2nature-${record.session_id}.json` && files.has('READ-ME.txt') && files.size===record.events.length+2,'The ZIP contains missing or unexpected files.');
  const clips=[];
  for(const event of record.events) {
    const bytes=files.get(event.audio_filename); checkWav(bytes,event,record.sample_rate);
    const actual=[...new Uint8Array(await digest(bytes))].map(b=>b.toString(16).padStart(2,'0')).join('');
    check(actual===event.audio_sha256,'A recording does not match its saved checksum. Try the original session.');
    clips.push({event,bytes});
  }
  return {record,clips};
}

export function sessionSummary({record:r}) {
  const window=r.schema==='talk2nature.observation-window.v1';
  return {window, animal:r.animal_context||unknownAnimal(),
    kind:window ? (r.sampling.complete?'Whole moment · complete':r.events.length?'Whole moment · partial':'Whole moment · no retained audio') : 'Sound highlights',
    retainedSeconds:r.events.reduce((n,e)=>n+e.samples/r.sample_rate,0),
    discarded:r.discarded_events.length};
}
export function comparisonWarnings(a,b) {
  const x=a.record,y=b.record,warnings=[];
  if(x.session_id===y.session_id) warnings.push('These are copies of the same session, not two independent observations.');
  if(x.origin!==y.origin) warnings.push('One session is an invented example and one declares microphone capture. Do not treat them as biological comparisons.');
  if(x.schema!==y.schema) warnings.push('Different recording modes: whole moments retain quiet samples; highlights select sounds above a threshold.');
  if(x.duration_seconds!==y.duration_seconds) warnings.push('Different observed durations. Clip and note counts are not comparable rates.');
  if([a,b].some(s=>s.record.schema==='talk2nature.observation-window.v1' && !s.record.sampling.complete)) warnings.push('A whole moment is incomplete or has discarded audio. Do not count the missing audio as silence.');
  if(x.discarded_events.length+y.discarded_events.length) warnings.push('Some audio was discarded. Retained recordings do not describe the whole session.');
  const ax=x.animal_context, ay=y.animal_context;
  if(!ax||!ay||ax.group==='unknown'||ay.group==='unknown'||ax.group!==ay.group||ax.species!==ay.species) warnings.push('Animal context is missing or differs. These are observer descriptions, not automatic identifications.');
  const settings=r=>JSON.stringify([r.sample_rate,...['sampleRate','channelCount','echoCancellation','noiseSuppression','autoGainControl'].map(k=>r.audio_settings[k]??null),r.detector?.margin_db??null,r.detector?.threshold_dbfs??null]);
  if(settings(x)!==settings(y)) warnings.push('Recording or detector settings differ. Apparent sound differences may come from the setup.');
  if([x,y].some(r=>r.origin==='microphone' && !['echoCancellation','noiseSuppression','autoGainControl'].every(k=>typeof r.audio_settings[k]==='boolean'))) warnings.push('Microphone processing settings are missing. Noise reduction or automatic gain may have changed the sound.');
  warnings.push('Microphone, distance, surroundings and start time are not controlled. Even matching settings do not establish a biological change.');
  return warnings;
}

// A slow or failed import must never replace a newer choice or an open session.
export class SessionSlot {
  constructor(){this.value=null;this.revision=0;}
  async open(load){const revision=++this.revision;try {const value=await load();if(revision!==this.revision)return false;this.value=value;return true;}catch(error){if(revision!==this.revision)return false;throw error;}}
  clear(){this.revision++;this.value=null;}
}
