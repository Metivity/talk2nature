// A bounded, local energy detector. No species/meaning model or upload path.
export const STATION_VERSION = '0.2.0';
export const SESSION_SECONDS = 300;
export const MAX_AUDIO_BYTES = 24 * 1024 * 1024;
export const MAX_EVENTS = 24;
export const MARKER_KINDS = ['person_voice', 'observation'];
export const SOURCE_LABELS = ['unreviewed', 'person', 'animal', 'other', 'uncertain'];
const rounded = value => Math.round(value * 10000) / 10000;
export const dbfs = rms => Math.max(-100, 20 * Math.log10(Math.max(rms, 0.00001)));

export function wavBytes(samples, sampleRate) {
  if (!(samples instanceof Int16Array) || !Number.isInteger(sampleRate) || sampleRate < 8000 || sampleRate > 96000) throw Error('Invalid PCM recording.');
  const buffer = new ArrayBuffer(44 + samples.length * 2), view = new DataView(buffer);
  const tag = (at, value) => [...value].forEach((char, i) => view.setUint8(at + i, char.charCodeAt(0)));
  tag(0, 'RIFF'); view.setUint32(4, buffer.byteLength - 8, true); tag(8, 'WAVE'); tag(12, 'fmt '); view.setUint32(16, 16, true);
  view.setUint16(20, 1, true); view.setUint16(22, 1, true); view.setUint32(24, sampleRate, true); view.setUint32(28, sampleRate * 2, true);
  view.setUint16(32, 2, true); view.setUint16(34, 16, true); tag(36, 'data'); view.setUint32(40, samples.length * 2, true);
  for (let i = 0; i < samples.length; i++) view.setInt16(44 + i * 2, samples[i], true);
  return buffer;
}

export class StationSession {
  constructor(sampleRate, {origin = 'synthetic', margin = 12, maxBytes = MAX_AUDIO_BYTES} = {}) {
    if (!Number.isInteger(sampleRate) || sampleRate < 8000 || sampleRate > 96000 || !['synthetic', 'microphone'].includes(origin) || !Number.isFinite(margin) || margin < 6 || margin > 24 || !Number.isInteger(maxBytes) || maxBytes < 1 || maxBytes > MAX_AUDIO_BYTES) throw Error('Unsupported station settings.');
    this.sampleRate = sampleRate; this.origin = origin; this.margin = margin; this.maxBytes = maxBytes;
    this.id = crypto.randomUUID(); this.startedAt = new Date().toISOString();
    this.samplesSeen = 0; this.events = []; this.discarded = []; this.markers = []; this.ring = []; this.active = null; this.calibration = [];
    this.threshold = null; this.level = -100; this.peak = 0; this.bytes = 0; this.stopped = false; this.stopReason = null; this.nextId = 1;
    this.totalSamples = 0; this.clippedSamples = 0;
  }
  get elapsed() { return this.samplesSeen / this.sampleRate; }
  audioFilename(id) { return `talk2nature-${this.id}-event-${id}.wav`; }
  push(samples) {
    if (this.stopped) return null;
    if (!(samples instanceof Float32Array) || !samples.length || samples.length > this.sampleRate / 5 || [...samples].some(x => !Number.isFinite(x))) throw Error('Expected finite audio frames of at most 200 ms.');
    const start = this.elapsed, pcm = new Int16Array(samples.length);
    let squares = 0, peak = 0, clipped = 0;
    for (let i = 0; i < samples.length; i++) {
      const value = Math.max(-1, Math.min(1, samples[i]));
      squares += value * value; peak = Math.max(peak, Math.abs(value)); if (Math.abs(value) >= .999) clipped++;
      pcm[i] = Math.round(value * (value < 0 ? 32768 : 32767));
    }
    this.samplesSeen += samples.length; this.totalSamples += samples.length; this.clippedSamples += clipped;
    this.level = dbfs(Math.sqrt(squares / samples.length)); this.peak = peak;
    const frame = {start, end: this.elapsed, pcm};
    if (this.threshold === null) {
      this.calibration.push(this.level);
      if (this.elapsed >= 3) {
        const levels = [...this.calibration].sort((a, b) => a - b);
        this.threshold = Math.min(-3, Math.max(-50, levels[Math.floor(levels.length / 2)] + this.margin));
      }
    } else {
      const loud = this.level >= (this.active ? this.threshold - 4 : this.threshold);
      if (!this.active && loud) this.active = {frames: [...this.ring], onset: start, lastLoudEnd: frame.end, quiet: 0, peak: 0};
      if (this.active) {
        this.active.frames.push(frame); this.active.peak = Math.max(this.active.peak, peak);
        this.active.quiet = loud ? 0 : this.active.quiet + samples.length / this.sampleRate;
        if (loud) this.active.lastLoudEnd = frame.end;
        if (this.active.quiet >= .5 || frame.end - this.active.frames[0].start >= 6) this.finishEvent(this.active.quiet >= .5 ? 'quiet' : 'clip_limit');
      }
    }
    this.ring.push(frame);
    while (this.ring.length && frame.end - this.ring[0].start > 1.05) this.ring.shift();
    if (this.elapsed >= SESSION_SECONDS) this.stop('time_limit');
    return {elapsed: this.elapsed, level: this.level, threshold: this.threshold, active: Boolean(this.active)};
  }
  finishEvent(reason) {
    const active = this.active; if (!active) return;
    this.active = null;
    const length = active.frames.reduce((n, f) => n + f.pcm.length, 0);
    if (this.events.length >= MAX_EVENTS || this.bytes + length * 2 > this.maxBytes) {
      this.discarded.push({id: this.nextId++, onset_seconds: rounded(active.onset), discarded: true, reason: 'storage_limit'});
      this.stopped = true; this.stopReason = 'storage_limit'; this.ring = []; return;
    }
    const pcm = new Int16Array(length); let offset = 0;
    for (const frame of active.frames) { pcm.set(frame.pcm, offset); offset += frame.pcm.length; }
    const event = {id: this.nextId++, onset_seconds: rounded(active.onset), last_loud_seconds: rounded(active.lastLoudEnd), clip_start_seconds: rounded(active.frames[0].start), clip_end_seconds: rounded(active.frames.at(-1).end), threshold_dbfs: rounded(this.threshold), peak: rounded(active.peak), ended_by: reason, source_label: 'unreviewed', notes: '', pcm};
    this.events.push(event); this.bytes += pcm.byteLength;
    if (this.events.length >= MAX_EVENTS || this.bytes >= this.maxBytes) { this.stopped = true; this.stopReason = 'storage_limit'; this.ring = []; }
    return event;
  }
  mark(kind, note = '') {
    if (this.stopped || !MARKER_KINDS.includes(kind) || typeof note !== 'string' || note.length > 300 || this.markers.length >= 100) throw Error('Start a session; use up to 100 markers with short notes.');
    const marker = {id: this.markers.length + 1, at_seconds: rounded(this.elapsed), kind, note: note.trim(), provenance: 'user-entered'};
    this.markers.push(marker); return marker;
  }
  review(id, source, notes) {
    const event = this.events.find(e => e.id === id);
    if (!event || !SOURCE_LABELS.includes(source) || typeof notes !== 'string' || notes.length > 300) throw Error('Invalid review.');
    event.source_label = source; event.notes = notes.trim();
  }
  discard(id) {
    const index = this.events.findIndex(e => e.id === id); if (index < 0) return;
    const event = this.events[index]; this.discarded.push({id: event.id, onset_seconds: event.onset_seconds, discarded: true});
    this.bytes -= event.pcm.byteLength; this.events.splice(index, 1);
  }
  stop(reason = 'user_stop') {
    if (!this.stopped) { this.finishEvent(reason); this.stopped = true; this.stopReason ||= reason; }
    this.ring = []; this.active = null;
  }
  markerWindows() {
    return this.markers.filter(m => m.kind === 'person_voice').map(m => {
      const next = [...this.events, ...this.discarded].sort((a, b) => a.onset_seconds - b.onset_seconds).find(e => e.onset_seconds >= m.at_seconds && e.onset_seconds <= m.at_seconds + 10);
      return {marker_id: m.id, window_seconds: 10, outcome: next ? next.discarded ? 'discarded_sound' : 'sound_detected' : m.at_seconds >= 3 && this.elapsed >= m.at_seconds + 10 ? 'no_detected_sound' : 'incomplete', event_id: next?.id ?? null, lag_seconds: next ? rounded(next.onset_seconds - m.at_seconds) : null, source_label: next?.source_label ?? null};
    });
  }
  exportRecord(alias = 'station-001', settings = {}) {
    if (typeof alias !== 'string' || !alias.trim() || alias.trim().length > 80) throw Error('Use a station alias of 1–80 characters.');
    return {schema: 'talk2nature.station.v1', session_id: this.id, started_at_utc: this.startedAt, clock: 'device wall clock; event offsets use processed audio samples; not synchronized', tool_version: STATION_VERSION, station_alias: alias.trim(), origin: this.origin, sample_rate: this.sampleRate, duration_seconds: rounded(this.elapsed), status: this.stopped ? 'stopped' : 'running', stop_reason: this.stopReason, detector: {type: 'energy_threshold', calibration_seconds: 3, margin_db: this.margin, threshold_dbfs: this.threshold, pre_roll_seconds: 1, max_clip_seconds_approx: 6, max_session_seconds: SESSION_SECONDS}, audio_settings: settings, near_full_scale_fraction: this.totalSamples ? this.clippedSamples / this.totalSamples : 0, markers: this.markers.map(m => ({...m})), events: this.events.map(({pcm, ...event}) => ({...event, samples: pcm.length, audio_filename: this.audioFilename(event.id)})), discarded_events: this.discarded.map(e => ({...e})), marker_windows: this.markerWindows(), limitations: ['No animal, human speech or meaning classifier is running.', 'A sound following a marker is not evidence of a reply or causation.', 'Undetected sounds and discarded audio are absent; this is not unbiased continuous audio.', 'Discarded clips retain only event ID/onset so deletion is not misreported as silence.', 'No verified consent, identity, research admission or training permission is established.', 'Audio is separate from this JSON. Files remain local until you share them.']};
  }
}
