import {AudioSession} from './station-audio.mjs';
import {DEVICE_CHECK_SECONDS, DeviceCheckMeter} from './device-check-model.mjs';

const $ = id => document.getElementById(id);
const card = $('device-check');
let capture = null, meter = null, pending = false, active = false, run = 0, watchdog = null, hardLimit = null, lastFrameAt = 0;
const stateText = {
  complete: 'The browser processed microphone samples for the full check. This does not confirm that an audible signal was present.',
  user_stop: 'You stopped the check. This partial reading is temporary.',
  backgrounded: 'The check stopped when this page left the foreground.',
  page_closed: 'The check ended as this page closed.',
  microphone_ended: 'The microphone stopped sending audio.',
  audio_interrupted: 'The browser audio session was interrupted.',
  no_audio: 'No microphone audio arrived. Check browser permission and the selected input.',
  capture_error: 'The audio check could not continue.',
  cancelled: 'Microphone request cancelled. No audio was measured.'
};

function setPhase(phase) {
  card.dataset.phase = phase;
  $('check-setup').hidden = phase !== 'setup';
  $('check-running').hidden = phase !== 'running' && phase !== 'starting';
  $('check-result').hidden = phase !== 'result';
  $('check-start').disabled = phase === 'starting' || phase === 'running';
  $('check-stop').disabled = phase !== 'starting' && phase !== 'running';
  if (phase === 'running' || phase === 'starting') document.body.dataset.deviceChecking = 'true';
  else delete document.body.dataset.deviceChecking;
}

function clearTimers() {
  if (watchdog) clearInterval(watchdog);
  if (hardLimit) clearTimeout(hardLimit);
  watchdog = hardLimit = null;
}

function showResult(reason) {
  const result = meter?.finish() || null;
  const duration = result?.duration_seconds || 0;
  $('check-result-title').textContent = reason === 'complete' ? 'Processed samples arrived.' : reason === 'no_audio' ? 'No processed samples arrived.' : reason === 'capture_error' ? 'The check could not finish.' : duration ? 'The check stopped early.' : 'No audio was measured.';
  $('check-result-detail').textContent = `${stateText[reason] || stateText.capture_error} Digital silence can still produce samples. No sound or check result was saved or uploaded.`;
  $('check-duration').textContent = `${duration.toFixed(1)} seconds`;
  $('check-rate').textContent = result ? `${result.processing_sample_rate_hz.toLocaleString()} Hz (browser processing)` : 'Not available';
  $('check-peak').textContent = result?.peak_level_dbfs === null || !result ? 'Not available' : `${result.peak_level_dbfs.toFixed(1)} dBFS`;
  $('check-ceiling').textContent = !result || result.near_full_scale_fraction === null ? 'Not available' : `${(result.near_full_scale_fraction * 100).toFixed(3)}% of samples`;
  if (result?.near_full_scale_fraction > 0) {
    $('check-ceiling').textContent += ' met the near-maximum threshold';
  }
  $('check-title').textContent = reason === 'complete' ? 'That’s one useful check.' : 'Nothing was saved.';
  $('check-status').textContent = reason === 'complete' ? 'The app processed samples while the screen stayed visible. This does not certify the microphone.' : stateText[reason] || stateText.capture_error;
  setPhase('result');
  $('check-result-title').focus({preventScroll: true});
}

function stop(reason = 'user_stop') {
  if (!pending && !active) return;
  const wasPending = pending;
  run++;
  pending = active = false;
  clearTimers();
  capture?.stop(); capture = null;
  showResult(wasPending && !meter ? 'cancelled' : reason);
}

function fail(error) {
  run++;
  pending = active = false;
  clearTimers();
  capture?.stop(); capture = null;
  meter = null;
  setPhase('setup');
  $('check-status').textContent = error?.name === 'NotAllowedError'
    ? 'Microphone permission was denied or dismissed. Nothing was measured. You can use the synthetic practice instead.'
    : `The check could not start: ${error?.message || 'audio access is unavailable'}. Nothing was measured.`;
}

async function start() {
  if (pending || active) return;
  if (!$('check-permission').checked) {
    $('check-status').textContent = 'Confirm permission to use the microphone in this room before starting.';
    $('check-permission').focus();
    return;
  }
  if (!window.isSecureContext || !window.AudioContext || !window.AudioWorkletNode || !navigator.mediaDevices?.getUserMedia) {
    $('check-status').textContent = 'This browser cannot run the microphone check here. Use a current browser on HTTPS, or try the synthetic practice.';
    return;
  }
  const token = ++run;
  pending = true; meter = null; lastFrameAt = 0;
  setPhase('starting');
  $('check-status').textContent = 'Waiting for the browser microphone permission. Use Stop check to cancel.';
  capture = new AudioSession({
    createContext: () => new AudioContext(),
    getMicrophone: () => navigator.mediaDevices.getUserMedia({audio: {channelCount: {ideal: 1}, echoCancellation: {ideal: false}, noiseSuppression: {ideal: false}, autoGainControl: {ideal: false}}, video: false}),
    createNode: context => new AudioWorkletNode(context, 'station-capture', {numberOfInputs: 1, numberOfOutputs: 1, outputChannelCount: [1]}),
    moduleUrl: new URL('./station-capture.mjs', import.meta.url).href,
    onFrame: samples => {
      if (token !== run || !active || !meter) return;
      try {
        lastFrameAt = performance.now();
        const result = meter.push(samples);
        $('check-elapsed').textContent = result.duration_seconds.toFixed(1);
        $('check-level-bar').style.width = `${Math.min(100, result.duration_seconds / DEVICE_CHECK_SECONDS * 100)}%`;
        if (meter.finished) stop('complete');
      } catch { stop('capture_error'); }
    },
    onEnded: reason => { if (token === run) stop(reason); }
  });
  try {
    const info = await capture.start(false);
    if (token !== run || !info) return;
    meter = new DeviceCheckMeter(info.sampleRate);
    active = true; pending = false; lastFrameAt = performance.now();
    $('check-status').textContent = 'Processing microphone samples locally. Keep the phone still and this page visible.';
    setPhase('running');
    hardLimit = setTimeout(() => stop('no_audio'), (DEVICE_CHECK_SECONDS + 4) * 1000);
    watchdog = setInterval(() => { if (active && performance.now() - lastFrameAt > 5000) stop('no_audio'); }, 1000);
  } catch (error) {
    if (token === run) fail(error);
  }
}

$('check-start').addEventListener('click', start);
$('check-stop').addEventListener('click', () => stop());
$('check-again').addEventListener('click', () => {
  meter = null; $('check-elapsed').textContent = '0.0'; $('check-level-bar').style.width = '0%';
  $('check-title').textContent = 'Keep the room ordinary.';
  $('check-status').textContent = 'The app reads incoming sound levels while this page stays open. It does not save or play the sound.';
  setPhase('setup'); $('check-permission').focus();
});
document.addEventListener('visibilitychange', () => { if (document.hidden && (pending || active)) stop('backgrounded'); });
window.addEventListener('pagehide', () => { if (pending || active) stop('page_closed'); });
window.addEventListener('beforeunload', () => { if (pending || active) stop('page_closed'); });
setPhase('setup');
