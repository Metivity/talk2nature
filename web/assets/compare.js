import {MAX_BUNDLE_BYTES,openSessionBundle,sessionSummary,comparisonWarnings,SessionSlot} from './session-import.mjs';
import {ANIMAL_GROUPS} from './animal-model.mjs';
import {WindowSession} from './window-model.mjs';
import {sessionFiles,zipFiles} from './station-export.mjs';

const $=id=>document.getElementById(id), slots={a:new SessionSlot(),b:new SessionSlot()};
const seconds=n=>`${n.toFixed(1)} s`;
const animal=r=>r.animal_context ? `${new Map(ANIMAL_GROUPS.map(([id,label])=>[id,label])).get(r.animal_context.group)}${r.animal_context.species?' · '+r.animal_context.species:''}`:'Not provided in this older session';
const node=(tag,text,className)=>{const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(className)e.className=className;return e;};
let audioUrl=null, audioSlot=null, exampleRun=0;
function stopPlayer(){const player=$('compare-player');player.pause();player.removeAttribute('src');player.load();if(audioUrl)URL.revokeObjectURL(audioUrl);audioUrl=null;audioSlot=null;$('compare-player-panel').hidden=true;}
function prepareClip(key,clip,index){stopPlayer();audioUrl=URL.createObjectURL(new Blob([clip.bytes],{type:'audio/wav'}));audioSlot=key;$('compare-player').src=audioUrl;$('compare-player-label').textContent=`Moment ${key.toUpperCase()} · Recording ${index+1} · ${slots[key].value.record.origin==='synthetic'?'invented tones':'declared microphone capture'}`;$('compare-player-panel').hidden=false;$('compare-player-panel').scrollIntoView({behavior:'auto',block:'center'});$('compare-player').focus();}
function renderSlot(key){
  const s=slots[key].value, target=$('summary-'+key), content=$('content-'+key); target.replaceChildren();content.replaceChildren();
  $('clear-'+key).hidden=!s;$('details-'+key).hidden=!s;
  $('title-'+key).textContent=s?s.record.station_alias:key==='a'?'Open a saved session':'Another day, perhaps?';
  if(!s){$('details-'+key).open=false;return;}
  const r=s.record, summary=sessionSummary(s);
  target.append(node('span',r.origin==='synthetic'?'INVENTED EXAMPLE':'MICROPHONE · DECLARED','compare-badge'),node('p',summary.kind,'compare-summary-kind'),node('p',`${seconds(r.duration_seconds)} observed · ${s.clips.length} retained recording${s.clips.length===1?'':'s'} · ${r.markers.length} observation${r.markers.length===1?'':'s'}`,'compare-summary-text'),node('p',`${animal(r)} · observer-declared`,'compare-summary-text'));
  content.append(node('h3','Saved recordings'));
  const clips=node('ol',undefined,'compare-entries');
  s.clips.forEach((clip,i)=>{const li=node('li'),e=clip.event;li.append(node('strong',`Recording ${i+1} · ${seconds(e.samples/r.sample_rate)}`),node('p',`${seconds(e.clip_start_seconds)}–${seconds(e.clip_end_seconds)} into the session · Source label: ${e.source_label} (saved review)`));if(e.notes)li.append(node('p',e.notes));const b=node('button','Review this sound');b.type='button';b.addEventListener('click',()=>prepareClip(key,clip,i));li.append(b);clips.append(li);});
  content.append(s.clips.length?clips:node('p','No audio was retained. That does not establish silence.','compare-summary-text'));
  if(summary.discarded)content.append(node('p',`${summary.discarded} discarded recording${summary.discarded===1?'':'s'}; audio is absent.`,'compare-summary-text'));
  content.append(node('h3','Observer notes'));
  const notes=node('ol',undefined,'compare-entries');
  r.markers.forEach(m=>{const li=node('li');li.append(node('strong',`${seconds(m.at_seconds)} · ${m.kind==='person_voice'?'Person’s voice marked':'Observation'}`),node('p',m.note||'No written note.'));notes.append(li);});
  content.append(r.markers.length?notes:node('p','No observer notes were saved.','compare-summary-text'));
}
function renderComparison(){
  const a=slots.a.value,b=slots.b.value;$('compare-results').hidden=!(a&&b);$('compare-table').replaceChildren();$('compare-warnings').replaceChildren();if(!a||!b)return;
  const rows=[['Recording mode',s=>sessionSummary(s).kind],['Observed time',s=>seconds(s.record.duration_seconds)],['Retained audio¹',s=>seconds(sessionSummary(s).retainedSeconds)],['Recordings kept',s=>String(s.clips.length)],['Discarded recordings',s=>String(sessionSummary(s).discarded)],['Observer notes',s=>String(s.record.markers.length)],['Who was there?',s=>animal(s.record)],['Declared start · UTC²',s=>s.record.started_at_utc.replace('T',' ').replace('Z',' UTC')],['Sample rate',s=>`${s.record.sample_rate.toLocaleString('en')} Hz`],['Declared origin',s=>s.record.origin==='synthetic'?'Invented example':'Microphone'],['Stop reason',s=>s.record.stop_reason.replaceAll('_',' ')]];
  const makeTable=entries=>{
    const table=node('table',undefined,'compare-table'),head=node('thead'),tr=node('tr');
    ['Saved detail','A · First moment','B · Second moment'].forEach(t=>{const th=node('th',t);th.scope='col';tr.append(th);});head.append(tr);table.append(head);const body=node('tbody');
    entries.forEach(([label,get])=>{const row=node('tr'),th=node('th',label);th.scope='row';row.append(th,node('td',get(a)),node('td',get(b)));body.append(row);});table.append(body);return table;
  };
  $('compare-table').append(makeTable(rows.slice(0,7)),node('p','¹ Sum of saved audio lengths. Overlapping highlights count twice; this is not session coverage.','compare-status'));
  const advanced=node('details',undefined,'compare-about');advanced.append(node('summary','Recording details · optional'));
  const setting=(s,key)=>typeof s.record.audio_settings[key]==='boolean'?(s.record.audio_settings[key]?'On':'Off'):'Not reported';
  advanced.append(makeTable([...rows.slice(7),['Noise reduction',s=>setting(s,'noiseSuppression')],['Automatic gain',s=>setting(s,'autoGainControl')],['Echo cancellation',s=>setting(s,'echoCancellation')],['Detector margin',s=>s.record.detector?`${s.record.detector.margin_db} dB`:'Not used'],['Detector threshold',s=>s.record.detector?.threshold_dbfs!=null?`${s.record.detector.threshold_dbfs.toFixed(1)} dBFS`:'Not available']]),node('p','² Device clock, unverified and not synchronized. Settings describe the saved declaration; they do not calibrate the microphone.','compare-status'));$('compare-table').append(advanced);
  comparisonWarnings(a,b).forEach(w=>$('compare-warnings').append(node('li',w)));
}
async function loadSlot(key,load){
  $('status-'+key).textContent='Checking the journal and recordings…';
  try{if(!await slots[key].open(load))return;if(audioSlot===key)stopPlayer();renderSlot(key);renderComparison();$('status-'+key).textContent='Opened locally. Recordings play only when you press Play.';}
  catch(error){$('status-'+key).textContent=`Could not open this session. ${error.message} ${slots[key].value?'Your previous session is still open.':''}`;}
}
for(const key of ['a','b']){
  $('file-'+key).addEventListener('change',()=>{const file=$('file-'+key).files[0];if(!file)return;exampleRun++;$('compare-example').disabled=false;$('compare-status').textContent='Your files stay on this device. Nothing is uploaded or saved in the browser.';loadSlot(key,async()=>{if(file.size>MAX_BUNDLE_BYTES)throw Error('Choose a session ZIP smaller than 27 MB.');return openSessionBundle(await file.arrayBuffer());});$('file-'+key).value='';});
  $('clear-'+key).addEventListener('click',()=>{exampleRun++;$('compare-example').disabled=false;$('compare-status').textContent='Your files stay on this device. Nothing is uploaded or saved in the browser.';slots[key].clear();if(audioSlot===key)stopPlayer();$('status-'+key).textContent='Closed. Your original saved file is unchanged.';renderSlot(key);renderComparison();$('file-'+key).focus();});
}
async function example(index){
  const s=new WindowSession(8000,{origin:'synthetic',animalContext:{group:'parrot',species:'Budgerigar',basis:'observer-declared'}});
  s.startedAt=`2026-01-0${index+1}T09:00:00.000Z`;
  const frames=index===0?300:180;
  for(let n=0;n<frames;n++){
    if(n===50)s.mark('observation',index===0?'Invented scene: a bird moves along a perch.':'Invented scene: a second bird enters the frame.');
    s.push(Float32Array.from({length:800},(_,i)=>n>=80&&n<86?.025*Math.sin(2*Math.PI*(index?480:360)*i/8000):0));
  }
  if(!s.stopped)s.stop('user_stop');
  const files=await sessionFiles(s,index===0?'Example · a whole moment':'Example · an early stop',{});
  return openSessionBundle(await zipFiles(files).arrayBuffer());
}
$('compare-example').addEventListener('click',async()=>{
  // Reserve both slots immediately so a later file choice always wins.
  const run=++exampleRun;$('compare-example').disabled=true;$('compare-status').textContent='Making two tiny invented recordings on your device…';
  await Promise.all(['a','b'].map((key,i)=>loadSlot(key,()=>example(i))));
  if(run!==exampleRun)return;$('compare-example').disabled=false;$('compare-status').textContent='Two invented scenes are open: one complete 30-second moment and one stopped at 18 seconds. Scroll down to compare.';
});
window.addEventListener('pagehide',()=>{exampleRun++;stopPlayer();for(const key of ['a','b']){slots[key].clear();$('status-'+key).textContent='';renderSlot(key);}renderComparison();$('compare-example').disabled=false;$('compare-status').textContent='Open your saved sessions again. Nothing was saved in the browser.';});
document.addEventListener('visibilitychange',()=>{if(document.hidden)$('compare-player').pause();});
