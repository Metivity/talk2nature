import {StationSession, wavBytes, SOURCE_LABELS} from './station-model.mjs';
import {AudioSession} from './station-audio.mjs';

const $ = id => document.getElementById(id);
let session = null, capture = null, active = false, pending = false, run = 0, settings = {}, levels = [], wake = null, deadline = null, watchdog = null, playerUrl = null, dirty = false, lastEventCount = 0, lastFrameAt = 0;
const formatTime = seconds => `${String(Math.floor(seconds / 60)).padStart(2, '0')}:${String(Math.floor(seconds % 60)).padStart(2, '0')}`;
const status = text => { $('station-status').textContent = text; };
const reasons = {user_stop: 'Stopped by you.', backgrounded: 'Stopped because this page left the foreground.', page_closed: 'Stopped on leaving the page.', time_limit: 'The five-minute session limit was reached.', storage_limit: 'Local event storage is full. Export or discard before a new session.', microphone_ended: 'The microphone disconnected or permission ended.', audio_interrupted: 'Audio was interrupted. Restart explicitly when ready.', no_audio: 'No audio frames arrived for five seconds. Capture stopped.', capture_error: 'An audio frame could not be processed.'};
function controls() {
  const busy = pending || active;
  for (const id of ['station-start', 'station-demo', 'station-margin', 'station-alias', 'station-permission']) $(id).disabled = busy;
  $('station-stop').disabled = !busy;
  $('station-voice').disabled = !active; $('station-observe').disabled = !active;
  $('station-export').disabled = !session || busy; $('station-clear').disabled = !session || busy;
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
  if (pending || active) return;
  if (!synthetic && !$('station-permission').checked) { status('Confirm that you have permission to record this setting before starting the microphone.'); return; }
  if (!$('station-alias').value.trim()) { status('Give this station a short alias. Avoid names or precise locations.'); return; }
  if (dirty && !window.confirm('Discard the current local session? Export its JSON and clips first if you want to keep them.')) return;
  if (!window.AudioContext || !window.AudioWorkletNode || (!synthetic && !navigator.mediaDevices?.getUserMedia)) { status('This browser does not support the required audio APIs. Try a current browser on HTTPS.'); return; }
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
        if (session.threshold === null) status('Checking the first three seconds of background level. Keep the setting undisturbed.');
        else if (result.elapsed < 3.3) status(synthetic ? 'Synthetic session running. Invented pulses recur; add a test marker and examine what follows.' : 'Listening locally. Short sound candidates will appear below. Mark only what you actually observed.');
      } catch { stop('capture_error'); }
    }
  });
  try {
    const result = await capture.start(synthetic);
    if (token !== run || !result) return;
    session = new StationSession(result.sampleRate, {origin: synthetic ? 'synthetic' : 'microphone', margin: Number($('station-margin').value)});
    settings = result.settings; active = true; pending = false; lastFrameAt = performance.now();
    $('station-headline').textContent = synthetic ? 'A rehearsal in listening.' : 'This place has a rhythm.';
    const setting = value => value === null ? 'unreported' : value ? 'on' : 'off';
    $('station-device').textContent = synthetic ? `Synthetic tones · ${result.sampleRate.toLocaleString()} Hz processing · no microphone, no speaker output.` : `${result.sampleRate.toLocaleString()} Hz processing · gain control ${setting(settings.auto_gain_control)} · noise suppression ${setting(settings.noise_suppression)} · echo cancellation ${setting(settings.echo_cancellation)}. Device settings are reported, not calibrated.`;
    controls();
    deadline = setTimeout(() => stop('time_limit'), 300000);
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
  $('station-time').textContent = formatTime(session?.elapsed || 0); $('station-event-total').textContent = session?.events.length || 0;
  $('station-memory').textContent = `${((session?.bytes || 0) / 1048576).toFixed(1)} MB`;
  $('station-level').textContent = session ? `${session.level.toFixed(1)} dBFS` : '— dBFS';
  $('station-threshold').textContent = session?.threshold != null ? `trigger ${session.threshold.toFixed(1)} dBFS · not dB SPL` : '3-second level check on start';
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
  $('station-window-summary').textContent = windows.length ? `${detected} voice markers followed by a detected sound · ${quiet} with none detected · ${incomplete} incomplete · ${discarded} with a clip not retained. Timing only; not verified replies.` : 'A shared timeline, before a shared vocabulary.';
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
  if (!session?.events.length) { const p = document.createElement('p'); p.className = 'station-empty'; p.textContent = 'Your first sound event will appear here.'; list.append(p); return; }
  for (const event of session.events) {
    const card = document.createElement('article'); card.className = 'station-event';
    const title = document.createElement('h3'), detail = document.createElement('p'), sourceLabel = document.createElement('label'), select = document.createElement('select');
    title.textContent = `Sound ${event.id} · ${formatTime(event.onset_seconds)}`;
    detail.textContent = `${(event.clip_end_seconds - event.clip_start_seconds).toFixed(1)} s clip · ${session.origin === 'synthetic' ? 'synthetic audio' : 'microphone audio'} · source ${event.source_label}`;
    sourceLabel.textContent = 'What made this sound?'; select.setAttribute('aria-label', `Source of sound ${event.id}`); select.disabled = active || pending;
    for (const source of SOURCE_LABELS) { const option = document.createElement('option'); option.value = source; option.textContent = source; select.append(option); } select.value = event.source_label;
    const details = document.createElement('details'), summary = document.createElement('summary'), notes = document.createElement('textarea'); summary.textContent = 'Review note'; notes.value = event.notes; notes.maxLength = 300; notes.disabled = active || pending; notes.setAttribute('aria-label', `Review note for sound ${event.id}`); details.append(summary, notes);
    const saveReview = () => { session.review(event.id, select.value, notes.value); dirty = true; detail.textContent = `${(event.clip_end_seconds - event.clip_start_seconds).toFixed(1)} s clip · source ${event.source_label} (your review)`; renderMarkers(); };
    select.addEventListener('change', saveReview); notes.addEventListener('change', saveReview); sourceLabel.append(select);
    const buttons = document.createElement('div'); buttons.className = 'station-controls';
    for (const [label, action] of [
      ['Review audio', () => { silencePlayer(); playerUrl = URL.createObjectURL(new Blob([wavBytes(event.pcm, session.sampleRate)], {type: 'audio/wav'})); $('station-player').src = playerUrl; $('station-player').hidden = false; $('station-player').focus(); status(`Sound ${event.id} ready in the audio player. Use headphones away from animals; press Play to review.`); }],
      ['Save WAV', () => { download(wavBytes(event.pcm, session.sampleRate), session.audioFilename(event.id), 'audio/wav'); status(`Sound ${event.id} download requested. Review it before sharing.`); }],
      ['Discard clip', () => { silencePlayer(); session.discard(event.id); dirty = true; renderEvents(); renderMarkers(); metrics(); }]
    ]) { const button = document.createElement('button'); button.type = 'button'; button.textContent = label; button.setAttribute('aria-label', `${label} ${event.id}`); button.disabled = active || pending; button.addEventListener('click', action); buttons.append(button); }
    card.append(title, detail, sourceLabel, details, buttons); list.append(card);
  }
}
$('station-start').addEventListener('click', () => start(false)); $('station-demo').addEventListener('click', () => start(true)); $('station-stop').addEventListener('click', () => stop());
for (const [id, kind] of [['station-voice', 'person_voice'], ['station-observe', 'observation']]) $(id).addEventListener('click', () => {
  try { session.mark(kind, $('station-note').value); $('station-note').value = ''; dirty = true; renderMarkers(); } catch (error) { status(error.message); }
});
$('station-export').addEventListener('click', async () => {
  const snapshot = session;
  if (!snapshot || active || pending) return;
  $('station-export').disabled = true;
  try {
    const record = snapshot.exportRecord($('station-alias').value, settings);
    const clips = snapshot.events.map(event => ({id: event.id, pcm: event.pcm}));
    for (const clip of clips) {
      const digest = await crypto.subtle.digest('SHA-256', wavBytes(clip.pcm, snapshot.sampleRate));
      record.events.find(event => event.id === clip.id).audio_sha256 = [...new Uint8Array(digest)].map(b => b.toString(16).padStart(2, '0')).join('');
    }
    download(JSON.stringify(record, null, 2) + '\n', `talk2nature-${snapshot.id}.json`, 'application/json');
    status('Session JSON download requested, with clip checksums. Save each WAV separately; JSON contains no audio.');
  } catch { status('Export failed. Your local clips remain in this tab; try again before leaving.'); }
  finally { controls(); }
});
$('station-clear').addEventListener('click', () => {
  if (dirty && !window.confirm('Discard this session and all local clips? Previously downloaded files will remain on your device.')) return;
  silencePlayer(); session = null; dirty = false; levels = []; metrics(); renderEvents(); renderMarkers(); draw(); controls(); status('Session discarded. No audio is recording.');
});
$('station-display').addEventListener('click', () => { const large = $('station-console').classList.toggle('station-large'); $('station-display').setAttribute('aria-pressed', String(large)); $('station-display').textContent = large ? 'Standard view' : 'Large-screen view'; draw(); });
document.addEventListener('visibilitychange', () => { if (document.hidden && (active || pending)) stop('backgrounded'); });
window.addEventListener('pagehide', () => { if (active || pending) stop('page_closed'); });
window.addEventListener('beforeunload', event => { if (active || pending) stop('page_closed'); if (dirty) { event.preventDefault(); event.returnValue = ''; } });
window.addEventListener('resize', draw); draw(); controls();
