import {animalPicker} from './animal-picker.mjs';
import {VERSION, MAX_BYTES, readWav, syntheticWav, validateDocument, eventCsv} from './listen-model.mjs';
import {MAX_NOTEBOOK_BYTES, makeNotebook, readNotebook} from './notebook.mjs';
import {audacityPackage} from './audacity-export.mjs';
import {aoefPackage} from './aoef-export.mjs';
import {MAX_BUNDLE_BYTES, openSessionBundle, sessionSummary} from './session-import.mjs';
import {createReviewAudioControls} from './review-audio.mjs';

const $ = id => document.getElementById(id);
const reviewAudio = createReviewAudioControls({audio:$('recording-audio'),button:$('listen-playback-toggle'),seek:$('listen-playback-seek'),time:$('listen-playback-time'),status:$('listen-playback-status'),confirm:message=>window.confirm(message)});
let audioBytes = null, recording = null, audioInfo = null, events = [], editing = null, mediaUrl = null, dirty = false, draftDirty = false, generation = 0, sessionBundle = null, sessionImportRevision = 0;
const animal = animalPicker(document, 'listen', () => { if (recording) dirty = true; });
const ids = ['recording-id', 'session-id', 'individual-id', 'annotator-id'];
const status = message => { $('listen-status').textContent = message; };
const rounded = n => Math.round(n * 1000) / 1000;
function documentValue() {
  const r = {...recording};
  ['recording_id', 'session_id', 'individual_id', 'annotator_id'].forEach((key, i) => { r[key] = $(ids[i]).value.trim(); });
  return validateDocument({schema: 'talk2nature.annotation.v1', tool_version: VERSION, recording: r, animal_context: animal.value(), events: structuredClone(events)});
}
function allowReplace() { return !(dirty || draftDirty) || window.confirm('Discard this session and any unfinished observation? Check that your notebook is in Downloads first.'); }
function allowDraftReplace() { return !draftDirty || window.confirm('Discard the unfinished observation?'); }
function markDraft() { draftDirty = true; $('draft-status').textContent = 'Unfinished observation — add it to the log before exporting.'; $('cancel-edit').hidden = false; }
function readyToExport() {
  if (!draftDirty) return true;
  const message = 'Add the unfinished observation to the log, or discard the draft, before exporting.';
  $('export-status').textContent = message; $('event-error').textContent = message; $('save-event').focus(); return false;
}
function exportError(error) {
  $('export-status').textContent = error.message; status(error.message);
  const invalid = ids.find(id => !$(id).value.trim());
  if (invalid) { $('recording-identifiers').open = true; $(invalid).focus(); }
}
function releaseAudio() {
  $('recording-audio').pause(); $('recording-audio').removeAttribute('src'); $('recording-audio').load();
  if (mediaUrl) URL.revokeObjectURL(mediaUrl);
  mediaUrl = null;
  reviewAudio.reset();
}
function resetEditor() {
  editing = null; draftDirty = false; $('export-status').textContent = ''; $('draft-status').textContent = ''; $('event-form').reset(); $('edit-heading').textContent = 'Mark a sound event.';
  $('save-event').textContent = 'Add event +'; $('cancel-edit').hidden = true; $('event-error').textContent = '';
  $('event-end').value = Math.min(1, recording?.duration_seconds || 1); draw();
}
function stationSourceMessage(source) {
  const {journal,event_id:eventId}=source, event=journal.events.find(item=>item.id===eventId);
  const whole=journal.schema==='talk2nature.observation-window.v1';
  const description=whole?'Continuous observation window; it is not a detected vocalization.':'Selected sound highlight; it is not confirmation of an animal sound.';
  return `${whole?'Whole moment':'Station clip'} · ${event.clip_start_seconds.toFixed(3)}–${event.clip_end_seconds.toFixed(3)} s within ${journal.duration_seconds.toFixed(3)} s. ${description}\nThe full session journal, including notes and declarations, is copied into this notebook as source context, not as annotation labels. The notebook is unencrypted; review before sharing.`;
}
function renderStationBundle(bundle) {
  const {record,clips}=bundle, summary=sessionSummary(bundle), list=$('session-clip-list');
  list.replaceChildren(); $('session-clip-picker').hidden=false;
  $('session-import-summary').textContent=`${summary.kind} · ${record.duration_seconds.toFixed(1)} seconds observed · ${clips.length} retained clip${clips.length===1?'':'s'} · ${summary.discarded} discarded.`;
  if(!clips.length) {
    $('session-import-status').textContent='No clips were retained in this session. An empty session is not evidence of silence; open it in Compare to inspect its journal.';
    return;
  }
  $('session-import-status').textContent='Session checked on this device. Choose a clip to annotate.';
  for(const clip of clips) {
    const {event}=clip, item=document.createElement('li'), detail=document.createElement('p'), button=document.createElement('button');
    const window=record.schema==='talk2nature.observation-window.v1';
    detail.textContent=window
      ? `Whole moment · ${event.clip_start_seconds.toFixed(3)}–${event.clip_end_seconds.toFixed(3)} s · continuous audio, not a detected sound.`
      : `Sound highlight ${event.id} · ${event.clip_start_seconds.toFixed(3)}–${event.clip_end_seconds.toFixed(3)} s in the session.`;
    button.type='button'; button.className='listen-secondary'; button.textContent='Review this clip';
    button.setAttribute('aria-label',`Review ${window?'whole moment':`sound highlight ${event.id}`} from ${event.clip_start_seconds.toFixed(3)} to ${event.clip_end_seconds.toFixed(3)} seconds`);
    button.addEventListener('click',()=>openStationClip(bundle,clip)); item.append(detail,button); list.append(item);
  }
}
function openStationClip(bundle,clip) {
  const source={journal:structuredClone(bundle.record),event_id:clip.event.id};
  const bytes=clip.bytes.slice().buffer;
  return openRecording(Promise.resolve(bytes),bundle.record.origin==='synthetic'?'synthetic':'user-supplied',source);
}
function draw() {
  if (!audioInfo) return;
  const canvas = $('waveform'), width = Math.max(1, canvas.clientWidth), height = 180, scale = window.devicePixelRatio || 1;
  canvas.width = Math.round(width * scale); canvas.height = height * scale;
  const ctx = canvas.getContext('2d'); ctx.scale(scale, scale);
  const start = Number($('event-start').value), end = Number($('event-end').value);
  ctx.fillStyle = '#d6bb6b77'; ctx.fillRect(start / audioInfo.duration * width, 0, (end - start) / audioInfo.duration * width, height);
  ctx.strokeStyle = '#366a50'; ctx.lineWidth = 1; ctx.beginPath();
  audioInfo.bins.forEach(([low, high], i) => { const x = i / audioInfo.bins.length * width; ctx.moveTo(x, height / 2 - Math.max(-1, Math.min(1, high)) * 78); ctx.lineTo(x, height / 2 - Math.max(-1, Math.min(1, low)) * 78); });
  ctx.stroke(); ctx.strokeStyle = '#778d6d'; ctx.beginPath(); ctx.moveTo(0, 90); ctx.lineTo(width, 90); ctx.stroke();
}
function renderEvents() {
  $('event-list').replaceChildren();
  $('event-count').textContent = events.length ? `${events.length} event${events.length === 1 ? '' : 's'} · ${events.filter(e => e.context === 'unknown').length} with unknown context` : 'No events yet. Mark an interval and add an observation.';
  for (const e of [...events].sort((a, b) => a.start_seconds - b.start_seconds || a.id - b.id)) {
    const li = document.createElement('li'), heading = document.createElement('h3'), description = document.createElement('p'), notes = document.createElement('p'), actions = document.createElement('div');
    heading.textContent = `${e.start_seconds.toFixed(3)}–${e.end_seconds.toFixed(3)} s · ${e.kind}`;
    description.textContent = `${e.context} · ${e.context_source} · ${e.confidence}`; notes.textContent = e.notes; actions.className = 'actions';
    for (const [label, action] of [['Edit', () => editEvent(e)], ['Remove', () => { if (editing === e.id && !allowDraftReplace()) return; events = events.filter(x => x.id !== e.id); dirty = true; if (editing === e.id) resetEditor(); renderEvents(); }]]) {
      const b = document.createElement('button'); b.type = 'button'; b.className = 'listen-secondary'; b.textContent = label; b.setAttribute('aria-label', `${label} event ${e.id}`); b.addEventListener('click', action); actions.append(b);
    }
    li.append(heading, description, notes, actions); $('event-list').append(li);
  }
}
function editEvent(e) {
  if (!allowDraftReplace()) return;
  draftDirty = false; $('draft-status').textContent = '';
  editing = e.id;
  for (const [id, key] of [['event-start','start_seconds'], ['event-end','end_seconds'], ['event-kind','kind'], ['event-context','context'], ['event-source','context_source'], ['event-confidence','confidence'], ['event-notes','notes']]) $(id).value = e[key];
  $('edit-heading').textContent = `Edit event ${e.id}.`; $('save-event').textContent = 'Save changes'; $('cancel-edit').hidden = false; $('event-error').textContent = '';
  draw(); $('event-start').focus();
}
async function openRecording(bufferPromise, origin, stationSource = null) {
  if (!allowReplace()) return;
  const current = ++generation;
  $('example').disabled = true; $('wav-file').disabled = true; $('session-zip-file').disabled = true; status('Inspecting the WAV file locally…');
  try {
    let buffer = await bufferPromise;
    let restored = null;
    if (origin === 'notebook') { const book = await readNotebook(buffer); buffer = book.audio; restored = book.labels; origin = restored.recording.origin; }
    const sourceSession=stationSource??restored?.recording?.source_session??null;
    const info = readWav(buffer);
    const hash = [...new Uint8Array(await crypto.subtle.digest('SHA-256', buffer))].map(b => b.toString(16).padStart(2, '0')).join('');
    if (current !== generation) return;
    releaseAudio(); audioInfo = info; audioBytes = buffer;
    recording = {sha256: hash, duration_seconds: info.duration, sample_rate: info.sample_rate, channels: info.channels, origin,...(sourceSession?{source_session:structuredClone(sourceSession)}:{})};
    events = []; dirty = false; animal.set(restored?.animal_context??sourceSession?.journal?.animal_context);
    ['recording-001', sourceSession?.journal?.session_id??'unknown', 'unknown', 'reviewer-001'].forEach((value, i) => { $(ids[i]).value = value; });
    if(sourceSession) $('recording-id').value=`station-clip-${sourceSession.event_id}`;
    else if (origin === 'synthetic') { $('recording-id').value = 'synthetic-tones-001'; $('session-id').value='unknown'; }
    $('recording-title').textContent = sourceSession ? 'A clip from your saved session.' : origin === 'synthetic' ? 'Two invented sound events.' : 'Your local recording.';
    $('origin-badge').textContent = sourceSession ? (origin==='synthetic'?'Synthetic session clip':'Station session clip') : origin === 'synthetic' ? 'Synthetic tones' : 'User-selected WAV';
    $('source-session-note').hidden=!sourceSession; $('source-session-note').textContent=sourceSession?stationSourceMessage(sourceSession):'';
    $('audio-summary').textContent = `${info.duration.toFixed(3)} seconds · ${info.sample_rate.toLocaleString()} Hz · ${info.channels} channel${info.channels === 1 ? '' : 's'} · ${info.bits}-bit`;
    $('quality-note').textContent = info.peak === 0 ? 'Digital silence: every sample is zero.' : `${(info.near_full_scale_fraction * 100).toFixed(3)}% of samples are near full scale (≥ 0.999). This is a basic level check; it does not establish recording quality or detect an animal.`;
    $('wave-end').textContent = `${info.duration.toFixed(3)} s`; $('hash-label').textContent = `SHA-256 · ${hash}`;
    $('event-start').max = info.duration; $('event-end').max = info.duration;
    reviewAudio.reset(info.duration);
    mediaUrl = URL.createObjectURL(new Blob([buffer], {type: 'audio/wav'})); $('recording-audio').src = mediaUrl;
    if (restored) { events = restored.events.map(e => Object.fromEntries(['id','start_seconds','end_seconds','kind','context','context_source','confidence','notes'].map(k => [k,e[k]]))); ['recording_id','session_id','individual_id','annotator_id'].forEach((key,i) => { $(ids[i]).value = restored.recording[key]; }); }
    $('listen-loaded').hidden = false; $('export-status').textContent = ''; resetEditor(); renderEvents(); $('recording-title').focus();
    status(restored ? `Notebook reopened with ${events.length} observation${events.length === 1 ? '' : 's'}. Audio and notes stayed on this device. Origin is an unverified declaration.` : sourceSession ? 'Station clip ready. Its journal is preserved as source context; no observation label or animal meaning was inferred.' : origin === 'synthetic' ? 'Example ready. Tones occur at 1–2 and 4–5 seconds. Label them as other sound; there is no animal context.' : 'Recording ready. No audio or labels have been uploaded.');
  } catch (error) { status(`Could not open recording: ${error.message}`); }
  finally { if (current === generation) { $('example').disabled = false; $('wav-file').disabled = false; $('session-zip-file').disabled = false; } }
}
$('example').addEventListener('click', () => openRecording(Promise.resolve(syntheticWav()), 'synthetic'));
$('wav-file').addEventListener('change', event => {
  const file = event.target.files[0]; event.target.value = '';
  if (!file) return;
  const notebook = file.name.toLowerCase().endsWith('.t2n');
  if (file.size > (notebook ? MAX_NOTEBOOK_BYTES : MAX_BYTES)) { status('Choose a sound under 25 MB or a notebook under 28 MB.'); return; }
  return openRecording(file.arrayBuffer(), notebook ? 'notebook' : 'user-supplied');
});
$('session-zip-file').addEventListener('change', async event => {
  const file=event.target.files[0]; event.target.value='';
  if(!file) return;
  if(file.size>MAX_BUNDLE_BYTES) { $('session-import-status').textContent='Choose an original session ZIP smaller than 27 MB.'; return; }
  const current=++sessionImportRevision; $('session-zip-file').disabled=true;
  $('session-import-status').textContent='Checking the session journal and saved sound hashes on this device…';
  try {
    const bundle=await openSessionBundle(await file.arrayBuffer());
    if(current!==sessionImportRevision) return;
    sessionBundle=bundle; renderStationBundle(bundle);
  } catch(error) {
    if(current===sessionImportRevision) $('session-import-status').textContent=`Could not open this session: ${error.message}${sessionBundle?' The previous checked session remains available.':''}`;
  } finally { if(current===sessionImportRevision) $('session-zip-file').disabled=false; }
});
$('event-form').addEventListener('submit', event => {
  event.preventDefault();
  try {
    const item = {id: editing ?? (Math.max(0, ...events.map(e => e.id)) + 1), start_seconds: Number($('event-start').value), end_seconds: Number($('event-end').value), kind: $('event-kind').value, context: $('event-context').value, context_source: $('event-source').value, confidence: $('event-confidence').value, notes: $('event-notes').value.trim()};
    const next = editing === null ? [...events, item] : events.map(e => e.id === editing ? item : e);
    validateDocument({...documentValue(), events: next}); events = next; dirty = true;
    resetEditor(); renderEvents(); status(`Event ${item.id} saved in this tab. Choose Save notebook to keep the sound and your observations together.`);
  } catch (error) { $('event-error').textContent = error.message; }
});
$('cancel-edit').addEventListener('click', () => { if (allowDraftReplace()) resetEditor(); });
$('event-form').addEventListener('input', markDraft);
$('event-form').addEventListener('change', markDraft);
ids.forEach(id => $(id).addEventListener('input', () => { dirty = true; }));
['event-start', 'event-end'].forEach(id => $(id).addEventListener('input', draw));
function download(content, name, type) {
  const objectUrl = URL.createObjectURL(new Blob([content], {type})), a = document.createElement('a');
  a.href = objectUrl; a.download = name; document.body.append(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(objectUrl), 30000);
}
$('save-notebook').addEventListener('click', async () => {
  if (!recording || !readyToExport()) return;
  const current = generation;
  try {
    $('save-notebook').disabled = true;
    const book = await makeNotebook(audioBytes, documentValue());
    if (current !== generation) return;
    download(book, 'talk2nature-notebook.t2n', 'application/octet-stream');
    $('export-status').textContent = 'Notebook download requested. It contains your sound and observations. Check Downloads before leaving; reopen it with Open a sound or notebook.'; status($('export-status').textContent);
  } catch (error) { exportError(error); }
  finally { $('save-notebook').disabled = false; }
});
$('export-json').addEventListener('click', () => {
  if (!readyToExport()) return;
  try { download(JSON.stringify(documentValue(), null, 2) + '\n', 'talk2nature-labels.json', 'application/json'); $('export-status').textContent = 'JSON download requested. Check your downloads before leaving; audio is saved separately.'; status($('export-status').textContent); }
  catch (error) { exportError(error); }
});
$('export-csv').addEventListener('click', () => {
  if (!readyToExport()) return;
  try { download(eventCsv(documentValue()), 'talk2nature-events.csv', 'text/csv'); $('export-status').textContent = 'CSV download requested. Save JSON too to reopen your work.'; status($('export-status').textContent); }
  catch (error) { exportError(error); }
});
$('export-audacity').addEventListener('click', async () => {
  if (!recording || !readyToExport() || $('export-audacity').disabled) return;
  const current = generation;
  try {
    $('export-audacity').disabled = true;
    const bundle = await audacityPackage(audioBytes, documentValue());
    if (current !== generation) return;
    download(bundle, 'talk2nature-audacity.zip', 'application/zip');
    $('export-status').textContent = 'Audacity package download requested. Check Downloads, unzip it, then open recording.wav and import labels.txt in Audacity. Full notes and conversion limits are included. Save your notebook for reopening here.';
    status($('export-status').textContent);
  } catch (error) { if (current === generation) exportError(error); }
  finally { $('export-audacity').disabled = false; }
});
$('export-aoef').addEventListener('click', async () => {
  if (!recording || !readyToExport() || $('export-aoef').disabled) return;
  const current = generation;
  try {
    $('export-aoef').disabled = true;
    const bundle = await aoefPackage(audioBytes, documentValue());
    if (current !== generation) return;
    download(bundle, 'talk2nature-aoef.zip', 'application/zip');
    $('export-status').textContent = 'AOEF package download requested. The current format passed a synthetic Whombat 0.9.0 UI check; follow the import steps below. This export is unencrypted and experimental. Keep the original notebook.';
    status($('export-status').textContent);
  } catch (error) { if (current === generation) exportError(error); }
  finally { $('export-aoef').disabled = false; }
});
$('labels-file').addEventListener('change', async event => {
  const file = event.target.files[0]; event.target.value = '';
  if (!file || !recording) return;
  if (file.size > 2 * 1024 * 1024) { status('Label files must be smaller than 2 MB.'); return; }
  const current = generation;
  try {
    const doc = validateDocument(JSON.parse(await file.text()), recording);
    if (current !== generation || !allowReplace()) return;
    // Copy only known fields; no imported markup or scripts enter the DOM.
    events = doc.events.map(e => Object.fromEntries(['id', 'start_seconds', 'end_seconds', 'kind', 'context', 'context_source', 'confidence', 'notes'].map(k => [k, e[k]])));
    ['recording_id', 'session_id', 'individual_id', 'annotator_id'].forEach((key, i) => { $(ids[i]).value = doc.recording[key]; });
    animal.set(doc.animal_context);
    dirty = false; resetEditor(); renderEvents(); status(`Reopened ${events.length} event${events.length === 1 ? '' : 's'} matched to this recording. Origin labels are declarations, not verified provenance.`);
  } catch (error) { status(`Labels were not imported: ${error.message}`); }
});
$('clear-recording').addEventListener('click', () => {
  if (!allowReplace()) return;
  generation++; releaseAudio(); recording = null; audioBytes = null; audioInfo = null; draftDirty = false; events = []; dirty = false;
  animal.set();
  $('source-session-note').hidden=true; $('source-session-note').textContent=''; $('listen-loaded').hidden = true; $('event-list').replaceChildren(); status('Session cleared. Previously exported files remain on your device.');
});
let dragStart = null;
const timeAt = event => { const rect = $('waveform').getBoundingClientRect(); return Math.min(audioInfo.duration, rounded(Math.max(0, (event.clientX - rect.left) / rect.width * audioInfo.duration))); };
$('waveform').addEventListener('pointerdown', event => { if (audioInfo) { dragStart = timeAt(event); $('waveform').setPointerCapture(event.pointerId); } });
$('waveform').addEventListener('pointermove', event => {
  if (dragStart === null) return;
  const end = timeAt(event); $('event-start').value = Math.min(dragStart, end); $('event-end').value = Math.max(dragStart, end); markDraft(); draw();
});
for (const name of ['pointerup', 'pointercancel']) $('waveform').addEventListener(name, () => { dragStart = null; });
window.addEventListener('resize', draw);
document.addEventListener('visibilitychange', () => { if (document.hidden) reviewAudio.pause('Playback paused because Listen left the foreground.'); });
window.addEventListener('pagehide', () => reviewAudio.pause('Playback paused because Listen closed.'));
window.addEventListener('beforeunload', event => { if (dirty || draftDirty) { event.preventDefault(); event.returnValue = ''; } });
