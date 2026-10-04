// Audacity's standard UTF-8 start/end/text label format; no spectral claims.
import {readWav, validateDocument} from './listen-model.mjs';
import {zipFiles} from './station-export.mjs';

const encode = text => new TextEncoder().encode(text);
const json = value => encode(JSON.stringify(value, null, 2) + '\n');
const quoted = value => JSON.stringify(value).replace(/[\u007f-\u009f\u2028\u2029]/g, c => `\\u${c.charCodeAt(0).toString(16).padStart(4, '0')}`);
export function audacityLabels(doc) {
  validateDocument(doc);
  if (!doc.events.length) throw Error('Add at least one sound event before exporting to Audacity.');
  const rows = [...doc.events].sort((a, b) => a.start_seconds - b.start_seconds || a.id - b.id).map(event => {
    const start = event.start_seconds.toFixed(6), end = event.end_seconds.toFixed(6);
    if (Number(end) <= Number(start)) throw Error(`Event ${event.id} is too short for this six-decimal label format. Keep the original notebook.`);
    const text = `[declared ${doc.recording.origin}] #${event.id} | ${event.kind} | context=${event.context} | source=${event.context_source} | confidence=${event.confidence} | notes=${quoted(event.notes)}`;
    return {event_id: event.id, start, end, text, max_error: Math.max(Math.abs(Number(start) - event.start_seconds), Math.abs(Number(end) - event.end_seconds))};
  });
  return {text: rows.map(r => `${r.start}\t${r.end}\t${r.text}`).join('\n') + '\n', rows};
}

export async function audacityFiles(audio, labels, digest = bytes => crypto.subtle.digest('SHA-256', bytes)) {
  // Freeze the save before hashing, so edits or replacement cannot mix files.
  audio = audio.slice(0); labels = structuredClone(labels);
  const info = readWav(audio);
  validateDocument(labels);
  const metadata = json(labels);
  if (metadata.length > 2 * 1024 * 1024) throw Error('This export has too many notes. Keep the original notebook.');
  const hash = [...new Uint8Array(await digest(audio))].map(b => b.toString(16).padStart(2, '0')).join('');
  validateDocument(labels, {sha256: hash, duration_seconds: info.duration, sample_rate: info.sample_rate, channels: info.channels, origin: labels.recording.origin});
  const exported = audacityLabels(labels);
  const report = {
    schema: 'talk2nature.audacity-export.v1', source_sha256: hash,
    declared_origin: labels.recording.origin, event_count: exported.rows.length,
    format: 'Audacity standard UTF-8 tab-separated start/end/text labels',
    time_unit: 'seconds from start of the bundled unedited WAV', decimal_places: 6,
    maximum_time_rounding_error_seconds: Math.max(...exported.rows.map(r => r.max_error)),
    label_row_event_ids: exported.rows.map(r => r.event_id),
    limitations: [
      'Label times are rounded to six decimals; this is formatting, not measured timing accuracy.',
      'Labels flatten kind, context, source, confidence and notes into display text. Notes use JSON string escaping; annotations.json preserves original fields and exact times.',
      'The text label track does not establish species, caller, channel, frequency range, permissions or biological meaning.',
      'Origin and animal context remain unverified declarations. The WAV checksum establishes equality, not authenticity or consent.',
      'Edits made in Audacity do not update annotations.json and cannot be imported back into Talk2Nature. Keep the original notebook and Station journal, if any.'
    ]
  };
  const instructions = `Talk2Nature → Audacity\n\n1. Unzip this package on your device.\n2. In Audacity, open recording.wav.\n3. Use File > Import > Labels (or the label editor's Import command) to open labels.txt. Menu names can vary by version.\n4. Inspect the timed labels. Playback is manual; use headphones away from animals.\n\nThe WAV is unchanged. Labels use seconds relative to its beginning, rounded to six decimals. Do not trim or shift the audio before importing. The labels are display text, not a validated biological codebook. Notes use visible escapes for tabs, newlines and control characters.\n\nKeep annotations.json for the complete original metadata and export-report.json for conversion limits and label-to-event mapping. Audacity edits do not update those files. There is no return import of Audacity labels into Talk2Nature. Save your original Talk2Nature notebook for reopening; this ZIP is not a Station session or notebook.\n\nDeclared origin: ${labels.recording.origin}. This declaration is not verified. No upload or automatic playback occurred. No consent, research admission, identity or meaning is established. The package is unencrypted and may contain private speech or notes; review it before sharing. Keep any original Station session journal separately.\n`;
  const files = [
    {name: 'recording.wav', bytes: new Uint8Array(audio)},
    {name: 'labels.txt', bytes: encode(exported.text)},
    {name: 'annotations.json', bytes: metadata},
    {name: 'export-report.json', bytes: json(report)},
    {name: 'READ-ME.txt', bytes: encode(instructions)}
  ];
  if (files.reduce((n, f) => n + f.bytes.length, 0) > 26 * 1048576) throw Error('The Audacity package exceeds 26 MB. Use a shorter WAV; keep the original notebook.');
  return files;
}

export async function audacityPackage(audio, labels) { return zipFiles(await audacityFiles(audio, labels)); }
