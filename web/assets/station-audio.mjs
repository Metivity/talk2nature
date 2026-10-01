// Own every capture resource so cancellation/permission races cannot leave a mic on.
export class AudioSession {
  constructor({createContext, getMicrophone, createNode, moduleUrl, onFrame, onEnded}) {
    Object.assign(this, {createContext, getMicrophone, createNode, moduleUrl, onFrame, onEnded});
    this.cancelled = false; this.stream = null; this.context = null; this.node = null; this.source = null; this.generator = null;
  }
  async start(synthetic) {
    try {
      if (!synthetic) {
        this.stream = await this.getMicrophone();
        if (this.cancelled) { this.stream.getTracks().forEach(t => t.stop()); return null; }
      }
      if (this.cancelled) return null;
      this.context = this.createContext();
      if (this.context.sampleRate < 8000 || this.context.sampleRate > 96000) throw Error('This audio sample rate is not supported.');
      await this.context.resume();
      if (this.cancelled) return null;
      await this.context.audioWorklet.addModule(this.moduleUrl);
      if (this.cancelled) return null;
      if (synthetic) {
        // Invented pulses flow through the same worklet, never to audible output.
        const rate = this.context.sampleRate, buffer = this.context.createBuffer(1, rate * 12, rate), values = buffer.getChannelData(0);
        for (let i = 0; i < values.length; i++) {
          const t = i / rate, active = (t >= 4 && t < 4.6) || (t >= 8 && t < 8.8);
          values[i] = active ? .09 * Math.sin(2 * Math.PI * (t < 6 ? 1400 : 2100) * t) : .0002 * Math.sin(2 * Math.PI * 170 * t);
        }
        this.generator = this.context.createBufferSource(); this.generator.buffer = buffer; this.generator.loop = true;
        this.source = this.generator;
      } else {
        this.source = this.context.createMediaStreamSource(this.stream);
        for (const track of this.stream.getTracks()) track.addEventListener('ended', () => { if (!this.cancelled) this.onEnded('microphone_ended'); });
      }
      this.node = this.createNode(this.context);
      this.node.port.onmessage = event => { if (!this.cancelled) this.onFrame(event.data); };
      this.source.connect(this.node); this.node.connect(this.context.destination); // Worklet explicitly zeros all output.
      this.context.addEventListener('statechange', () => { if (!this.cancelled && this.context.state !== 'running') this.onEnded('audio_interrupted'); });
      if (this.generator) this.generator.start();
      const settings = this.stream?.getAudioTracks()[0]?.getSettings() || {};
      return {sampleRate: this.context.sampleRate, settings: {input_sample_rate: settings.sampleRate ?? null, input_channels: settings.channelCount ?? null, processing_channel: 'first input channel', echo_cancellation: settings.echoCancellation ?? null, noise_suppression: settings.noiseSuppression ?? null, auto_gain_control: settings.autoGainControl ?? null}};
    } catch (error) { this.stop(); throw error; }
  }
  stop() {
    this.cancelled = true;
    if (this.node) { this.node.port.onmessage = null; this.node.disconnect(); }
    if (this.generator) { try { this.generator.stop(); } catch {} }
    if (this.source) this.source.disconnect();
    if (this.stream) this.stream.getTracks().forEach(t => t.stop());
    if (this.context && this.context.state !== 'closed') this.context.close().catch(() => {});
  }
}
