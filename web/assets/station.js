import {WindowSession, WINDOW_SECONDS} from './window-model.mjs';
import {animalPicker} from './animal-picker.mjs';
import {StationSession, wavBytes, SOURCE_LABELS} from './station-model.mjs';
import {sessionFiles, zipFiles} from './station-export.mjs';
import {AudioSession} from './station-audio.mjs';

const $ = id => document.getElementById(id);
let session = null, capture = null, active = false, pending = false, exporting = false, run = 0, settings = {}, levels = [], wake = null, deadline = null, watchdog = null, playerUrl = null, dirty = false, lastEventCount = 0, lastFrameAt = 0;
const animal = animalPicker(document, 'station');
const formatTime = seconds => `${String(Math.floor(seconds / 60)).padStart(2, '0')}:${String(Math.floor(seconds % 60)).padStart(2, '0')}`;
const status = text => { $('station-status').textContent = text; };
const reasons = {window_complete: 'Your 30-second window is ready. Quiet moments are included.', window_timeout: 'Recording stopped at the time limit. This window is incomplete; check its recorded duration.', user_stop: 'Stopped by you.', backgrounded: 'Stopped because this page left the foreground.', page_closed: 'Stopped on leaving the page.', time_limit: 'The five-minute session limit was reached.', storage_limit: 'Local event storage is full. Export or discard before a new session.', microphone_ended: 'The microphone disconnected or permission ended.', audio_interrupted: 'Audio was interrupted. Restart explicitly when ready.', no_audio: 'No audio frames arrived for five seconds. Capture stopped.', capture_error: 'An audio frame could not be processed.'};
function controls() {
  const busy = pending || active || exporting;
  animal.lock(busy || Boolean(session));
  $('station-capture-mode').disabled = busy || Boolean(session);
  for (const id of ['station-start', 'station-demo', 'station-margin', 'station-alias', 'station-permission']) $(id).disabled = busy;
  $('station-stop').disabled = !(pending || active);
  $('station-voice').disabled = !active; $('station-observe').disabled = !active;
  $('station-bundle').disabled = !session || busy; $('station-export').disabled = !session || busy; $('station-clear').disabled = !session || busy;
  $('station-state').textContent = pending ? 'Starting…' : active ? session?.origin === 'synthetic' ? 'Synthetic session' : 'Microphone recording' : session ? 'Stopped · local only' : 'Ready';
  $('station-light').classList.toggle('recording', active && session?.origin === 'microphone');
  $('station-voice').textContent = session?.origin === 'synthetic' ? 'Add test voice marker' : 'Mark my voice';
}
function silencePlayer() {
  $('station-player').pause(); $('station-player').removeAttribute('src'); $('station-player').load(); $('station-player').hidden = true;
  if (playerUrl) URL.revokeObjectURL(playerUrl); playerUrl = null;
}
function stop(reason = 'user_stop') {
  run++; pending = false; active = false;
  capture?.stop(); capture = null;
  if (deadline) clearTimeout(deadline); if (watchdog) clearInterval(watchdog); deadline = null; watchdog = null;
  wake?.release().catch(() => {}); wake = null;
  if (session) { session.stop(reason); dirty = true; status(reasons[session.stopReason] || 'Session stopped.'); }
  else status(reasons[reason] || 'Start cancelled.');
  controls(); renderEvents(); renderMarkers(); metrics();
}
async function start(synthetic) {
  if (pending || active || exporting) return;
  if (!synthetic && !$('station-permission').checked) { status('Confirm that you have permission to record this setting before starting the microphone.'); return; }
  if (!checkAlias()) return;
  if (dirty && !window.confirm('Discard the current local session? Export its JSON and clips first if you want to keep them.')) return;
  if (!window.AudioContext || !window.AudioWorkletNode || (!synthetic && !navigator.mediaDevices?.getUserMedia)) { status('This browser does not support the required audio APIs. Try a current browser on HTTPS.'); return; }
  let animalContext;
  try { animalContext = animal.value(); } catch (error) { status(error.message); return; }
  const windowMode = $('station-capture-mode').value === 'window';
  const token = ++run; pending = true; session = null; dirty = false; levels = []; lastEventCount = 0; settings = {}; silencePlayer(); renderEvents(); renderMarkers(); controls(); metrics();
  status(synthetic ? 'Starting invented tones inside the audio engine. No microphone access or audible playback.' : 'Waiting for microphone permission. You can cancel with Stop recording.');
  capture = new AudioSession({
    createContext: () => new AudioContext(),
    getMicrophone: () => navigator.mediaDevices.getUserMedia({audio: {channelCount: {ideal: 1}, echoCancellation: {ideal: false}, noiseSuppression: {ideal: false}, autoGainControl: {ideal: false}}, video: false}),
    createNode: context => new AudioWorkletNode(context, 'station-capture', {numberOfInputs: 1, numberOfOutputs: 1, outputChannelCount: [1]}),
    moduleUrl: new URL('./station-capture.mjs', import.meta.url).href,
    onEnded: reason => { if (token === run) stop(reason); },
    onFrame: samples => {
      if (token !== run || !session || !active) return;
      try {
        lastFrameAt = performance.now(); const result = session.push(samples); if (!result) return;
        dirty = true; levels.push(result.level); if (levels.length > 120) levels.shift(); metrics(); draw();
        if (lastEventCount !== session.events.length) { lastEventCount = session.events.length; renderEvents(); }
        renderMarkers();
        if (session.stopped) { stop(session.stopReason); return; }
        if (windowMode) status(`Keeping the whole moment · ${Math.max(0, Math.ceil(WINDOW_SECONDS - result.elapsed))} seconds remaining. Observe the ordinary routine; quiet moments count too.`);
        else if (session.threshold === null) status('Checking the first three seconds of background level. Keep the setting undisturbed.');
        else if (result.elapsed < 3.3) status(synthetic ? 'Synthetic session running. Invented pulses recur; add a test marker and examine what follows.' : 'Listening locally. Short sound candidates will appear below. Mark only what you actually observed.');
      } catch { stop('capture_error'); }
    }
  });
  try {
    const result = await capture.start(synthetic);
    if (token !== run || !result) return;
    session = new (windowMode ? WindowSession : StationSession)(result.sampleRate, {origin: synthetic ? 'synthetic' : 'microphone', margin: Number($('station-margin').value), animalContext});
    settings = result.settings; active = true; pending = false; lastFrameAt = performance.now();
    $('station-headline').textContent = synthetic ? 'A rehearsal in listening.' : 'This place has a rhythm.';
    const setting = value => value === null ? 'unreported' : value ? 'on' : 'off';
    $('station-device').textContent = synthetic ? `Synthetic tones · ${result.sampleRate.toLocaleString()} Hz processing · no microphone, no speaker output.` : `${result.sampleRate.toLocaleString()} Hz processing · gain control ${setting(settings.auto_gain_control)} · noise suppression ${setting(settings.noise_suppression)} · echo cancellation ${setting(settings.echo_cancellation)}. Device settings are reported, not calibrated.`;
    controls(); renderEvents();
    deadline = setTimeout(() => stop(windowMode ? 'window_timeout' : 'time_limit'), windowMode ? WINDOW_SECONDS * 1000 + 1500 : 300000);
    watchdog = setInterval(() => { if (active && performance.now() - lastFrameAt > 5000) stop('no_audio'); }, 1000);
    if (navigator.wakeLock) {
      try { const lock = await navigator.wakeLock.request('screen'); if (token === run && active) wake = lock; else lock.release().catch(() => {}); } catch { /* A denied wake lock never implies background capture. */ }
    }
  } catch (error) {
    if (token !== run) return;
    stop('capture_error');
    status(error.name === 'NotAllowedError' ? 'Microphone permission was denied. Nothing is recording. You can try the synthetic station.' : `Could not start audio: ${error.message}. Nothing is recording.`);
  }
}
function metrics() {
  const whole = session ? session.mode === 'window' : $('station-capture-mode').value === 'window';
  $('station-time').textContent = formatTime(session?.elapsed || 0); $('station-event-total').textContent = session?.events.length || 0;
  $('station-event-caption').textContent = whole ? 'saved window' : 'sound candidates';
  $('station-memory').textContent = `${((session?.bytes || 0) / 1048576).toFixed(1)} MB`;
  $('station-level').textContent = session ? `${session.level.toFixed(1)} dBFS` : '— dBFS';
  $('station-threshold').textContent = whole ? 'Continuous audio · no sound trigger' : session?.threshold != null ? `trigger ${session.threshold.toFixed(1)} dBFS · not dB SPL` : '3-second level check on start';
}
function draw() {
  const canvas = $('station-scope'), width = Math.max(1, canvas.clientWidth), height = canvas.clientHeight, scale = window.devicePixelRatio || 1;
  canvas.width = width * scale; canvas.height = height * scale; const ctx = canvas.getContext('2d'); ctx.scale(scale, scale);
  const y = level => height - Math.max(0, Math.min(1, (level + 100) / 100)) * height;
  ctx.strokeStyle = '#43644c'; ctx.lineWidth = .7;
  for (const db of [-80, -60, -40, -20]) { ctx.beginPath(); ctx.moveTo(0, y(db)); ctx.lineTo(width, y(db)); ctx.stroke(); }
  if (session?.threshold != null) { ctx.strokeStyle = '#e5b66b'; ctx.setLineDash([4, 5]); ctx.beginPath(); ctx.moveTo(0, y(session.threshold)); ctx.lineTo(width, y(session.threshold)); ctx.stroke(); ctx.setLineDash([]); }
  ctx.strokeStyle = '#d6e9a4'; ctx.lineWidth = 2; ctx.beginPath(); levels.forEach((level, i) => { const x = i / 119 * width; i ? ctx.lineTo(x, y(level)) : ctx.moveTo(x, y(level)); }); ctx.stroke();
}
function renderMarkers() {
  const list = $('station-markers'); list.replaceChildren(); const windows = session?.markerWindows() || [];
  const detected = windows.filter(w => w.outcome === 'sound_detected').length, quiet = windows.filter(w => w.outcome === 'no_detected_sound').length, incomplete = windows.filter(w => w.outcome === 'incomplete').length, discarded = windows.filter(w => w.outcome === 'discarded_sound').length;
  $('station-window-summary').textContent = windows.length ? `${detected} voice markers followed by a detected sound · ${quiet} with none detected · ${incomplete} incomplete · ${discarded} with a clip not retained. Timing only; not verified replies.` : session?.mode === 'window' ? 'Your markers share this window’s timeline. They do not establish who made a sound or what it meant.' : 'A shared timeline, before a shared vocabulary.';
  for (const marker of [...(session?.markers || [])].reverse()) {
    const li = document.createElement('li'), title = document.createElement('strong'), note = document.createElement('p');
    title.textContent = `${formatTime(marker.at_seconds)} · ${marker.kind === 'person_voice' ? 'Voice marker' : 'Observation'}`; note.textContent = marker.note;
    const window = windows.find(w => w.marker_id === marker.id), detail = document.createElement('p');
    if (window) detail.textContent = window.outcome === 'sound_detected' ? `Next detected sound: +${window.lag_seconds.toFixed(1)} s, source ${window.source_label}.` : window.outcome === 'discarded_sound' ? 'A detected sound followed; its clip was not retained.' : window.outcome === 'no_detected_sound' ? 'No level-triggered sound in the next 10 seconds.' : 'Ten-second detection window incomplete (calibration or session boundary).';
    li.append(title, note, detail); list.append(li);
  }
}
function download(content, name, type) {
  const url = URL.createObjectURL(new Blob([content], {type})), link = document.createElement('a'); link.href = url; link.download = name; document.body.append(link); link.click(); link.remove(); setTimeout(() => URL.revokeObjectURL(url), 30000);
}
function renderEvents() {
  const list = $('station-events'); list.replaceChildren();
  if (!session?.events.length) { const p = document.createElement('p'); p.className = 'station-empty'; p.textContent = session?.mode === 'window' ? active ? 'Your full window will appear here when recording stops.' : 'No audio window retained.' : 'Your first sound event will appear here.'; list.append(p); return; }
  for (const event of session.events) {
    const card = document.createElement('article'); card.className = 'station-event';
    const title = document.createElement('h3'), detail = document.createElement('p'), sourceLabel = document.createElement('label'), select = document.createElement('select');
    title.textContent = session.mode === 'window' ? session.exportRecord().sampling.complete ? 'Your full 30-second moment' : 'Partial observation window' : `Sound ${event.id} · ${formatTime(event.onset_seconds)}`;
    detail.textContent = `${(event.clip_end_seconds - event.clip_start_seconds).toFixed(1)} s clip · ${session.origin === 'synthetic' ? 'synthetic audio' : 'microphone audio'} · source ${event.source_label}`;
    sourceLabel.textContent = session.mode === 'window' ? 'Main source, if known (mixed or quiet? Leave uncertain)' : 'What made this sound?'; select.setAttribute('aria-label', `Source of sound ${event.id}`); select.disabled = active || pending || exporting;
    for (const source of SOURCE_LABELS) { const option = document.createElement('option'); option.value = source; option.textContent = source; select.append(option); } select.value = event.source_label;
    const details = document.createElement('details'), summary = document.createElement('summary'), notes = document.createElement('textarea'); summary.textContent = 'Review note'; notes.value = event.notes; notes.maxLength = 300; notes.disabled = active || pending || exporting; notes.setAttribute('aria-label', `Review note for sound ${event.id}`); details.append(summary, notes);
    const saveReview = () => { session.review(event.id, select.value, notes.value); dirty = true; detail.textContent = `${(event.clip_end_seconds - event.clip_start_seconds).toFixed(1)} s clip · source ${event.source_label} (your review)`; renderMarkers(); };
    select.addEventListener('change', saveReview); notes.addEventListener('change', saveReview); sourceLabel.append(select);
    const buttons = document.createElement('div'); buttons.className = 'station-controls';
    for (const [label, action] of [
      ['Review audio', () => { silencePlayer(); playerUrl = URL.createObjectURL(new Blob([wavBytes(event.pcm, session.sampleRate)], {type: 'audio/wav'})); $('station-player').src = playerUrl; $('station-player').hidden = false; $('station-player').focus(); status(`${session.mode === 'window' ? 'Observation window' : `Sound ${event.id}`} ready in the audio player. Use headphones away from animals; press Play to review.`); }],
      ['Save WAV', () => { download(wavBytes(event.pcm, session.sampleRate), session.audioFilename(event.id), 'audio/wav'); status(`Sound ${event.id} download requested. Review it before sharing.`); }],
      ['Discard clip', () => { silencePlayer(); session.discard(event.id); dirty = true; renderEvents(); renderMarkers(); metrics(); }]
    ]) { const button = document.createElement('button'); button.type = 'button'; button.textContent = label; button.setAttribute('aria-label', `${label} ${event.id}`); button.disabled = active || pending || exporting; button.addEventListener('click', action); buttons.append(button); }
    card.append(title, detail, sourceLabel, details, buttons); list.append(card);
  }
}
function modeGuidance() {
  const whole = $('station-capture-mode').value === 'window';
  $('station-sensitivity').hidden = whole;
  $('station-mode-guidance').textContent = whole ? 'Keep 30 seconds together, including quiet moments and background sounds. Start during an ordinary routine, before waiting for an interesting call. Review people’s speech before sharing.' : 'Keep short clips when sound rises above the background. Quieter periods are not saved; this is a highlights collection.';
  metrics();
  if ($('scenario-guidance')) $('scenario-guidance').textContent = whole ? 'Keep this screen open. Recording ends after 30 seconds of audio; an early stop or interruption is marked incomplete.' : 'Keep this screen open. Start with three quiet seconds for the detector. Five-minute maximum.';
}
if (new URL(location.href).searchParams.get('mode') === 'companion') $('station-capture-mode').value = 'window';
$('station-capture-mode').addEventListener('change', modeGuidance); modeGuidance();
$('station-start').addEventListener('click', () => start(false)); $('station-demo').addEventListener('click', () => start(true)); $('station-stop').addEventListener('click', () => stop());
for (const [id, kind] of [['station-voice', 'person_voice'], ['station-observe', 'observation']]) $(id).addEventListener('click', () => {
  try { session.mark(kind, $('station-note').value); $('station-note').value = ''; dirty = true; renderMarkers(); } catch (error) { status(error.message); }
});
function checkAlias() {
  const input = $('station-alias');
  if (input.value.trim() && input.value.trim().length <= 80) { input.removeAttribute('aria-invalid'); return true; }
  $('station-settings').open = true; input.setAttribute('aria-invalid', 'true'); input.focus();
  status('Enter a station alias of 1–80 characters in Session settings, then try again. Avoid personal names or precise locations.');
  return false;
}
async function exportSession(bundle) {
  if (!session || active || pending || exporting || !checkAlias()) return;
  exporting = true; controls(); renderEvents(); status('Preparing your local download…');
  try {
    const files = await sessionFiles(session, $('station-alias').value, settings);
    if (bundle) download(zipFiles(files), `talk2nature-${session.id}.zip`, 'application/zip');
    else download(files[0].bytes, files[0].name, 'application/json');
    status(bundle ? 'Session download requested: one ZIP with your journal and all retained WAV clips. Check your Downloads folder before leaving. Unzip it to review a WAV.' : 'Journal JSON download requested. This file contains no audio; use Save session for journal and clips together.');
  } catch { status('Could not prepare the download. Your clips remain in this tab. Try again or save individual WAV files before leaving.'); }
  finally { exporting = false; controls(); renderEvents(); }
}
$('station-bundle').addEventListener('click', () => exportSession(true));
$('station-export').addEventListener('click', () => exportSession(false));
$('station-clear').addEventListener('click', () => {
  if (dirty && !window.confirm('Discard this session and all local clips? Previously downloaded files will remain on your device.')) return;
  silencePlayer(); session = null; dirty = false; levels = []; metrics(); renderEvents(); renderMarkers(); draw(); controls(); status('Session discarded. No audio is recording.');
});
$('station-display').addEventListener('click', () => { const large = $('station-console').classList.toggle('station-large'); $('station-display').setAttribute('aria-pressed', String(large)); $('station-display').textContent = large ? 'Standard view' : 'Large-screen view'; draw(); });
document.addEventListener('visibilitychange', () => { if (document.hidden && (active || pending)) stop('backgrounded'); });
window.addEventListener('pagehide', () => { if (active || pending) stop('page_closed'); });
window.addEventListener('beforeunload', event => { if (active || pending) stop('page_closed'); if (dirty) { event.preventDefault(); event.returnValue = ''; } });
window.addEventListener('resize', draw); draw(); controls();
