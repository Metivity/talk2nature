import {StationSession, dbfs} from './station-model.mjs';

export const WINDOW_SECONDS = 30;
// A user-started continuous window, separate from energy-triggered sound events.
export class WindowSession extends StationSession {
  constructor(sampleRate, options = {}) {
    super(sampleRate, options);
    this.mode = 'window';
    this.capacity = Math.min(sampleRate * WINDOW_SECONDS, Math.floor(this.maxBytes / 2));
    if (!this.capacity) throw Error('Insufficient recording storage.');
    this.buffer = new Int16Array(this.capacity);
  }
  audioFilename() { return `talk2nature-${this.id}-window.wav`; }
  push(samples) {
    if (this.stopped) return null;
    if (!(samples instanceof Float32Array) || !samples.length || samples.length > this.sampleRate / 5 || samples.some(x => !Number.isFinite(x))) throw Error('Expected finite audio frames of at most 200 ms.');
    const count = Math.min(samples.length, this.capacity - this.samplesSeen);
    let squares = 0, peak = 0;
    for (let i = 0; i < count; i++) {
      const value = Math.max(-1, Math.min(1, samples[i]));
      squares += value * value; peak = Math.max(peak, Math.abs(value));
      if (Math.abs(value) >= .999) this.clippedSamples++;
      this.buffer[this.samplesSeen + i] = Math.round(value * (value < 0 ? 32768 : 32767));
    }
    this.samplesSeen += count; this.totalSamples += count; this.bytes = this.samplesSeen * 2;
    this.level = dbfs(Math.sqrt(squares / count)); this.peak = Math.max(this.peak, peak);
    if (this.samplesSeen === this.capacity) this.stop(this.capacity === this.sampleRate * WINDOW_SECONDS ? 'window_complete' : 'storage_limit');
    return {elapsed: this.elapsed, level: this.level, threshold: null, active: !this.stopped};
  }
  stop(reason = 'user_stop') {
    if (this.stopped) return;
    this.stopped = true;
    // A wall-clock deadline or interruption never certifies a full sample window.
    this.stopReason = reason === 'window_complete' && this.samplesSeen !== this.sampleRate * WINDOW_SECONDS ? 'capture_error' : reason;
    if (this.samplesSeen) this.events.push({id: 1, kind: 'observation_window', onset_seconds: null,
      clip_start_seconds: 0, clip_end_seconds: this.elapsed, peak: this.peak,
      ended_by: this.stopReason, source_label: 'unreviewed', notes: '', pcm: this.buffer.slice(0, this.samplesSeen)});
    this.buffer = null;
  }
  markerWindows() { return []; } // No detector, quiet-window or reply inference.
  exportRecord(alias = 'station-001', settings = {}) {
    const base = super.exportRecord(alias, settings);
    const {detector, marker_windows, limitations, ...record} = base;
    const retained = this.stopped && this.events.length === 1;
    return {...record, schema: 'talk2nature.observation-window.v1', tool_version: '0.1.0',
      sampling: {method: 'user_started_fixed_window', requested_seconds: WINDOW_SECONDS,
        processed_samples: this.samplesSeen, retained_samples: retained ? this.events[0].pcm.length : 0,
        complete: retained && this.stopReason === 'window_complete' && this.samplesSeen === this.sampleRate * WINDOW_SECONDS,
        selection: 'Observer-selected start; not randomized. Quiet samples are retained.'},
      limitations: ['This window contains processed audio samples, not a calibrated or synchronized physical measurement.',
        'Events here are retained observation windows, not detected vocalizations. No level detector or species model runs in this mode.',
        'A complete window does not prove an animal was audible, all sounds were captured, independent sampling or biological meaning.',
        'An interruption, early stop or discarded window must not be treated as a complete observation.',
        'Human speech and background sounds can be present. Review locally before sharing.',
        'No verified consent, identity, research admission or training permission is established.']};
  }
}
