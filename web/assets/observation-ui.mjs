// Human-entered timeline notes; never inferred animal behavior or call meaning.
export const QUICK_NOTES = Object.freeze({
  movement: 'I noticed movement.',
  another_animal: 'I noticed another animal.',
  surroundings: 'I noticed a change in the surroundings.',
  uncertain: 'I am not sure what happened.'
});

export function addQuickObservation(session, key) {
  if (!Object.hasOwn(QUICK_NOTES, key) || !session || session.stopped) throw Error('Start a session before adding an observation.');
  return session.mark('observation', QUICK_NOTES[key]);
}

export function sessionRecap(session) {
  if (!session?.stopped) return null;
  const record = session.exportRecord();
  const count = record.events.length;
  const notes = record.markers.length;
  const origin = record.origin === 'synthetic' ? 'Invented practice audio' : 'Microphone audio';
  const title = !count ? 'No audio retained.' : record.sampling
    ? record.sampling.complete ? 'A whole 30-second moment.' : 'A partial moment. Still worth noting.'
    : `${count} sound ${count === 1 ? 'highlight' : 'highlights'} to review.`;
  const detail = `${origin} · ${record.duration_seconds.toFixed(1)} seconds observed · ${notes} ${notes === 1 ? 'note' : 'notes'}. ${count ? 'Audio is still temporary. Save the session before leaving.' : 'You can save the journal, including notes and any discard records.'}`;
  return {title, detail};
}

export function sessionProvenance(record) {
  if (!record || !Number.isInteger(record.sample_rate) || !record.audio_settings) {
    return [{label: 'Recording details', value: 'Not available for this session.'}];
  }
  const settings = record.audio_settings;
  const synthetic = record.origin === 'synthetic';
  const capture = record.capture_metadata || {};
  const reported = (value, unit = '') => Number.isFinite(value) && value > 0 ? `${value.toLocaleString()}${unit} · browser-reported` : 'Not reported';
  const enabled = value => typeof value === 'boolean' ? value ? 'On' : 'Off' : 'Not reported';
  return [
    {label: 'Capture source', value: synthetic ? 'Invented practice audio · no microphone used' : 'Microphone input · device identifier not saved'},
    {label: 'Recorder or microphone', value: synthetic ? 'Not applicable · synthetic practice' : capture.recorder_description ? `${capture.recorder_description} · ${capture.recorder_description_provenance || 'provenance not reported'}` : 'Not provided · hardware is not detected'},
    {label: 'Input sample rate', value: synthetic ? 'Not applicable · no microphone input' : reported(settings.input_sample_rate, ' Hz')},
    {label: 'Input channels', value: synthetic ? 'Not applicable · no microphone input' : reported(settings.input_channels)},
    {label: 'Processing sample rate', value: `${record.sample_rate.toLocaleString()} Hz · ${synthetic ? 'synthetic audio' : capture.sample_rate_role || 'browser audio processing'}`},
    {label: 'Saved audio', value: 'Mono 16-bit PCM WAV · uncompressed'},
    {label: 'Microphone processing', value: synthetic ? 'Not applicable' : `Automatic gain ${enabled(settings.auto_gain_control)} · noise suppression ${enabled(settings.noise_suppression)} · echo cancellation ${enabled(settings.echo_cancellation)}`},
    {label: 'Microphone frequency response', value: synthetic ? 'Not applicable · synthetic practice' : capture.microphone_frequency_response || 'Not reported'},
    {label: 'Clock', value: record.clock || 'Not reported'}
  ];
}
