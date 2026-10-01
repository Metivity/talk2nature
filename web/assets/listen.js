import {VERSION, MAX_BYTES, readWav, syntheticWav, validateDocument, eventCsv} from './listen-model.mjs';

const $ = id => document.getElementById(id);
let recording = null, audioInfo = null, events = [], editing = null, mediaUrl = null, dirty = false, generation = 0;
const ids = ['recording-id', 'session-id', 'individual-id', 'annotator-id'];
const status = message => { $('listen-status').textContent = message; };
const rounded = n => Math.round(n * 1000) / 1000;
function documentValue() {
  const r = {...recording};
  ['recording_id', 'session_id', 'individual_id', 'annotator_id'].forEach((key, i) => { r[key] = $(ids[i]).value.trim(); });
  return validateDocument({schema: 'talk2nature.annotation.v1', tool_version: VERSION, recording: r, events: structuredClone(events)});
}
function allowReplace() { return !dirty || window.confirm('There are changes that have not been exported as JSON. Discard them?'); }
function releaseAudio() {
  $('recording-audio').pause(); $('recording-audio').removeAttribute('src'); $('recording-audio').load();
  if (mediaUrl) URL.revokeObjectURL(mediaUrl);
  mediaUrl = null;
}
function resetEditor() {
  editing = null; $('event-form').reset(); $('edit-heading').textContent = 'Mark a sound event.';
  $('save-event').textContent = 'Add event +'; $('cancel-edit').hidden = true; $('event-error').textContent = '';
  $('event-end').value = Math.min(1, recording?.duration_seconds || 1); draw();
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
    for (const [label, action] of [['Edit', () => editEvent(e)], ['Remove', () => { events = events.filter(x => x.id !== e.id); dirty = true; if (editing === e.id) resetEditor(); renderEvents(); }]]) {
      const b = document.createElement('button'); b.type = 'button'; b.className = 'listen-secondary'; b.textContent = label; b.setAttribute('aria-label', `${label} event ${e.id}`); b.addEventListener('click', action); actions.append(b);
    }
    li.append(heading, description, notes, actions); $('event-list').append(li);
  }
}
function editEvent(e) {
  editing = e.id;
  for (const [id, key] of [['event-start','start_seconds'], ['event-end','end_seconds'], ['event-kind','kind'], ['event-context','context'], ['event-source','context_source'], ['event-confidence','confidence'], ['event-notes','notes']]) $(id).value = e[key];
  $('edit-heading').textContent = `Edit event ${e.id}.`; $('save-event').textContent = 'Save changes'; $('cancel-edit').hidden = false; $('event-error').textContent = '';
  draw(); $('event-start').focus();
}
async function openRecording(bufferPromise, origin) {
  if (!allowReplace()) return;
  const current = ++generation;
  $('example').disabled = true; $('wav-file').disabled = true; status('Inspecting the WAV file locally…');
  try {
    const buffer = await bufferPromise;
    const info = readWav(buffer);
    const hash = [...new Uint8Array(await crypto.subtle.digest('SHA-256', buffer))].map(b => b.toString(16).padStart(2, '0')).join('');
    if (current !== generation) return;
    releaseAudio(); audioInfo = info;
    recording = {sha256: hash, duration_seconds: info.duration, sample_rate: info.sample_rate, channels: info.channels, origin};
    events = []; dirty = false;
    ['recording-001', 'unknown', 'unknown', 'reviewer-001'].forEach((value, i) => { $(ids[i]).value = value; });
    if (origin === 'synthetic') $('recording-id').value = 'synthetic-tones-001';
    $('recording-title').textContent = origin === 'synthetic' ? 'Two invented sound events.' : 'Your local recording.';
    $('origin-badge').textContent = origin === 'synthetic' ? 'Synthetic tones' : 'User-selected WAV';
    $('audio-summary').textContent = `${info.duration.toFixed(3)} seconds · ${info.sample_rate.toLocaleString()} Hz · ${info.channels} channel${info.channels === 1 ? '' : 's'} · ${info.bits}-bit`;
    $('quality-note').textContent = info.peak === 0 ? 'Digital silence: every sample is zero.' : `${(info.near_full_scale_fraction * 100).toFixed(3)}% of samples are near full scale (≥ 0.999). This is a basic level check; it does not establish recording quality or detect an animal.`;
    $('wave-end').textContent = `${info.duration.toFixed(3)} s`; $('hash-label').textContent = `SHA-256 · ${hash}`;
    $('event-start').max = info.duration; $('event-end').max = info.duration;
    mediaUrl = URL.createObjectURL(new Blob([buffer], {type: 'audio/wav'})); $('recording-audio').src = mediaUrl;
    $('listen-loaded').hidden = false; resetEditor(); renderEvents();
    status(origin === 'synthetic' ? 'Example ready. Tones occur at 1–2 and 4–5 seconds. Label them as other sound; there is no animal context.' : 'Recording ready. No audio or labels have been uploaded.');
  } catch (error) { status(`Could not open recording: ${error.message}`); }
  finally { if (current === generation) { $('example').disabled = false; $('wav-file').disabled = false; } }
}
$('example').addEventListener('click', () => openRecording(Promise.resolve(syntheticWav()), 'synthetic'));
$('wav-file').addEventListener('change', event => {
  const file = event.target.files[0]; event.target.value = '';
  if (!file) return;
  if (file.size > MAX_BYTES) { status('Choose a WAV file no larger than 25 MB.'); return; }
  openRecording(file.arrayBuffer(), 'user-supplied');
});
$('event-form').addEventListener('submit', event => {
  event.preventDefault();
  try {
    const item = {id: editing ?? (Math.max(0, ...events.map(e => e.id)) + 1), start_seconds: Number($('event-start').value), end_seconds: Number($('event-end').value), kind: $('event-kind').value, context: $('event-context').value, context_source: $('event-source').value, confidence: $('event-confidence').value, notes: $('event-notes').value.trim()};
    const next = editing === null ? [...events, item] : events.map(e => e.id === editing ? item : e);
    validateDocument({...documentValue(), events: next}); events = next; dirty = true;
    resetEditor(); renderEvents(); status(`Event ${item.id} saved in this tab. Export JSON to keep your work.`);
  } catch (error) { $('event-error').textContent = error.message; }
});
$('cancel-edit').addEventListener('click', resetEditor);
ids.forEach(id => $(id).addEventListener('input', () => { dirty = true; }));
['event-start', 'event-end'].forEach(id => $(id).addEventListener('input', draw));
function download(content, name, type) {
  const objectUrl = URL.createObjectURL(new Blob([content], {type})), a = document.createElement('a');
  a.href = objectUrl; a.download = name; document.body.append(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(objectUrl), 30000);
}
$('export-json').addEventListener('click', () => {
  try { download(JSON.stringify(documentValue(), null, 2) + '\n', 'talk2nature-labels.json', 'application/json'); dirty = false; status('JSON export requested. Check your downloads before closing this tab. The export contains labels and identifiers, not audio.'); }
  catch (error) { status(error.message); }
});
$('export-csv').addEventListener('click', () => {
  try { download(eventCsv(documentValue()), 'talk2nature-events.csv', 'text/csv'); status('CSV export requested. Keep a JSON export too if you want to reopen this work.'); }
  catch (error) { status(error.message); }
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
    dirty = false; resetEditor(); renderEvents(); status(`Reopened ${events.length} events matched to this recording. Origin labels are declarations, not verified provenance.`);
  } catch (error) { status(`Labels were not imported: ${error.message}`); }
});
$('clear-recording').addEventListener('click', () => {
  if (!allowReplace()) return;
  generation++; releaseAudio(); recording = null; audioInfo = null; events = []; dirty = false;
  $('listen-loaded').hidden = true; $('event-list').replaceChildren(); status('Session cleared. Previously exported files remain on your device.');
});
let dragStart = null;
const timeAt = event => { const rect = $('waveform').getBoundingClientRect(); return Math.min(audioInfo.duration, rounded(Math.max(0, (event.clientX - rect.left) / rect.width * audioInfo.duration))); };
$('waveform').addEventListener('pointerdown', event => { if (audioInfo) { dragStart = timeAt(event); $('waveform').setPointerCapture(event.pointerId); } });
$('waveform').addEventListener('pointermove', event => {
  if (dragStart === null) return;
  const end = timeAt(event); $('event-start').value = Math.min(dragStart, end); $('event-end').value = Math.max(dragStart, end); draw();
});
for (const name of ['pointerup', 'pointercancel']) $('waveform').addEventListener(name, () => { dragStart = null; });
window.addEventListener('resize', draw);
window.addEventListener('beforeunload', event => { if (dirty) { event.preventDefault(); event.returnValue = ''; } });
