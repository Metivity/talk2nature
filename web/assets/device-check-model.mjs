import {dbfs} from './station-model.mjs';

export const DEVICE_CHECK_SECONDS = 8;

// Keep only aggregate microphone diagnostics; never retain an input frame.
export class DeviceCheckMeter {
  constructor(sampleRate) {
    if (!Number.isInteger(sampleRate) || sampleRate < 8000 || sampleRate > 96000) throw Error('Unsupported processing sample rate.');
    this.sampleRate = sampleRate;
    this.limit = Math.floor(sampleRate * DEVICE_CHECK_SECONDS);
    this.samples = 0;
    this.squares = 0;
    this.peak = 0;
    this.nearFullScale = 0;
    this.finished = false;
  }

  push(frame) {
    if (this.finished) return this.snapshot();
    if (!(frame instanceof Float32Array) || !frame.length || frame.length > this.sampleRate / 5 || frame.some(value => !Number.isFinite(value))) throw Error('Expected a finite microphone frame no longer than 200 ms.');
    const count = Math.min(frame.length, this.limit - this.samples);
    for (let i = 0; i < count; i++) {
      const value = Math.max(-1, Math.min(1, frame[i]));
      this.squares += value * value;
      this.peak = Math.max(this.peak, Math.abs(value));
      if (Math.abs(value) >= .999) this.nearFullScale++;
    }
    this.samples += count;
    if (this.samples >= this.limit) this.finished = true;
    return this.snapshot();
  }

  finish() { this.finished = true; return this.snapshot(); }

  snapshot() {
    const rms = this.samples ? Math.sqrt(this.squares / this.samples) : null;
    return {
      processing_sample_rate_hz: this.sampleRate,
      processed_samples: this.samples,
      duration_seconds: Math.round(this.samples / this.sampleRate * 100) / 100,
      average_level_dbfs: rms === null ? null : dbfs(rms),
      peak_level_dbfs: this.samples ? dbfs(this.peak) : null,
      near_full_scale_fraction: this.samples ? this.nearFullScale / this.samples : null
    };
  }
}
