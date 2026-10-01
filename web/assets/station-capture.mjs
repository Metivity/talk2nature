// Outputs remain zero: microphone audio is never routed to the speakers.
export class FrameAccumulator {
  constructor(rate, emit) { this.buffer = new Float32Array(Math.round(rate / 10)); this.offset = 0; this.emit = emit; }
  push(channel) {
    for (let i = 0; i < channel.length; i++) {
      this.buffer[this.offset++] = channel[i];
      if (this.offset === this.buffer.length) { const frame = this.buffer; this.buffer = new Float32Array(frame.length); this.offset = 0; this.emit(frame); }
    }
  }
}

if (typeof registerProcessor === 'function') {
  class StationCapture extends AudioWorkletProcessor {
    constructor() { super(); this.frames = new FrameAccumulator(sampleRate, frame => this.port.postMessage(frame, [frame.buffer])); }
    process(inputs, outputs) {
      for (const output of outputs) for (const channel of output) channel.fill(0);
      const channel = inputs[0]?.[0]; if (channel) this.frames.push(channel);
      return true;
    }
  }
  registerProcessor('station-capture', StationCapture);
}
