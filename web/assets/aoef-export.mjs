// Experimental, one-way local export to AOEF 1.1.0.
// The full Talk2Nature record is kept as a sidecar; no service or model is called.
import {readWav, validateDocument} from './listen-model.mjs';
import {zipFiles} from './station-export.mjs';

const encoder = new TextEncoder();
const encodeJSON = value => encoder.encode(JSON.stringify(value, null, 2) + '\n');
const isoNow = () => new Date().toISOString();

function uuid() {
  const source = globalThis.crypto;
  if (source?.randomUUID) return source.randomUUID();
  if (!source?.getRandomValues) throw Error('This browser cannot create secure export IDs.');
  const bytes = source.getRandomValues(new Uint8Array(16));
  bytes[6] = (bytes[6] & 0x0f) | 0x40;
  bytes[8] = (bytes[8] & 0x3f) | 0x80;
  const hex = [...bytes].map(n => n.toString(16).padStart(2, '0')).join('');
  return `${hex.slice(0,8)}-${hex.slice(8,12)}-${hex.slice(12,16)}-${hex.slice(16,20)}-${hex.slice(20)}`;
}

const tagFields = Object.freeze([
  ['talk2nature.kind', 'kind'],
  ['talk2nature.context', 'context'],
  ['talk2nature.context_source', 'context_source'],
  ['talk2nature.confidence', 'confidence']
]);

function aoefEnvelope(data, createdOn) {
  return {version: '1.1.0', created_on: createdOn, data};
}

export async function aoefFiles(audio, labels, digest = bytes => crypto.subtle.digest('SHA-256', bytes)) {
  // Freeze both inputs before hashing so edits cannot mix audio and annotations.
  audio = audio.slice(0);
  labels = structuredClone(labels);
  const audioInfo = readWav(audio);
  validateDocument(labels);
  if (!labels.events.length) throw Error('Add at least one observation before exporting an AOEF package.');
  const sourceJSON = encodeJSON(labels);
  if (sourceJSON.length > 2 * 1024 * 1024) throw Error('The provenance sidecar is too large for this export. Keep the original notebook.');
  const sha256 = [...new Uint8Array(await digest(audio))].map(b => b.toString(16).padStart(2, '0')).join('');
  validateDocument(labels, {sha256, duration_seconds: audioInfo.duration, sample_rate: audioInfo.sample_rate, channels: audioInfo.channels, origin: labels.recording.origin});

  const createdOn = isoNow();
  const recordingId = uuid();
  const recording = {
    uuid: recordingId,
    path: 'recording.wav',
    duration: audioInfo.duration,
    channels: audioInfo.channels,
    samplerate: audioInfo.sample_rate,
    hash: sha256,
    owners: []
  };
  const tagIndex = new Map();
  const tags = [];
  const indexedTag = (key, value) => {
    const identity = `${key}\u0000${value}`;
    if (!tagIndex.has(identity)) {
      const id = tags.length;
      tagIndex.set(identity, id);
      tags.push({id, key, value});
    }
    return tagIndex.get(identity);
  };

  const soundEvents = [];
  const soundEventAnnotations = [];
  const eventMapping = [];
  for (const event of labels.events) {
    const soundEventId = uuid();
    const annotationId = uuid();
    soundEvents.push({
      uuid: soundEventId,
      recording: recordingId,
      geometry: {type: 'TimeInterval', coordinates: [event.start_seconds, event.end_seconds]}
    });
    soundEventAnnotations.push({
      uuid: annotationId,
      sound_event: soundEventId,
      notes: event.notes ? [{uuid: uuid(), message: event.notes, is_issue: false, created_on: createdOn}] : [],
      tags: tagFields.map(([key, field]) => indexedTag(key, event[field])),
      created_on: createdOn
    });
    eventMapping.push({event_id: event.id, sound_event_uuid: soundEventId, annotation_uuid: annotationId, start_seconds: event.start_seconds, end_seconds: event.end_seconds});
  }

  const clipId = uuid();
  const clipAnnotationId = uuid();
  const dataset = aoefEnvelope({
    uuid: uuid(),
    collection_type: 'dataset',
    created_on: createdOn,
    recordings: [recording],
    tags: [],
    users: [],
    name: 'Talk2Nature recording',
    description: 'A user-selected recording with preliminary, observer-entered labels. Research admission is not established.'
  }, createdOn);
  const project = aoefEnvelope({
    uuid: uuid(),
    name: 'Talk2Nature preliminary observations',
    description: 'One-way experimental AOEF export. Read the Talk2Nature provenance sidecar before reuse.',
    collection_type: 'annotation_project',
    tags,
    project_tags: tags.map(tag => tag.id),
    recordings: [recording],
    sound_events: soundEvents,
    clips: [{uuid: clipId, recording: recordingId, start_time: 0, end_time: audioInfo.duration}],
    sound_event_annotations: soundEventAnnotations,
    clip_annotations: [{uuid: clipAnnotationId, clip: clipId, sound_events: soundEventAnnotations.map(item => item.uuid), sequences: [], tags: [], notes: [], created_on: createdOn}],
    created_on: createdOn,
    instructions: 'Tags are preliminary Talk2Nature observer entries, not decoded animal meaning. Unknown context is not silence. Do not treat these labels as verified research data or model predictions.',
    tasks: [{uuid: uuid(), clip: clipId, status_badges: [], created_on: createdOn}]
  }, createdOn);

  const report = {
    schema: 'talk2nature.aoef-export.v1',
    format: 'AOEF 1.1.0',
    tested_library: 'soundevent 2.10.0 synthetic save/load; Whombat 0.9.0 synthetic UI import verified',
    source_sha256: sha256,
    declared_origin: labels.recording.origin,
    event_count: labels.events.length,
    events: eventMapping,
    tag_keys: Object.fromEntries(tagFields.map(([key, field]) => [key, field])),
    included_files: ['recording.wav', 'dataset.aoef.json', 'annotation-project.aoef.json', 'talk2nature-annotations.json', 'export-report.json', 'READ-ME.txt'],
    limitations: [
      'This is a one-way exchange package. Keep the original .t2n notebook; edits in another tool do not update it.',
      'The AOEF files carry the WAV checksum, relative audio path, event intervals, kind, context, context source, confidence and observer notes.',
      'Recording/session/individual/annotator IDs, declared animal context and any checked Station source journal remain in the Talk2Nature JSON sidecar, not the AOEF records.',
      'No person, username or email is added to AOEF creator fields. The sidecar may contain aliases, notes, timestamps or location details; inspect every file before sharing.',
      'Whombat 0.9.0 UI import was verified with synthetic audio in one Python 3.12.5 desktop environment. Other dependency combinations, real recordings and scientific suitability have not been verified.',
      'Whombat requires imported audio directories to use the same canonical path as its configured audio root. On macOS, /tmp may resolve to /private/tmp; use a consistent canonical path.',
      'The package does not establish consent, rights, species identity, independent ground truth, research admission, animal meaning or model performance. No upload or model run occurred.'
    ]
  };
  const instructions = `Talk2Nature → AOEF 1.1.0\n\nThis experimental ZIP contains one unchanged WAV, a dataset description, an annotation project, the original Talk2Nature annotation JSON and a conversion report.\n\nTo try it in Whombat 0.9.0, unzip the package. Import dataset.aoef.json first and choose the extracted package folder as its audio directory. Then import annotation-project.aoef.json. The WAV reference is recording.wav relative to that folder. The synthetic dataset-then-project workflow was verified in the Whombat desktop UI.\n\nWhombat only imports audio directories inside its configured audio root. Use the same canonical absolute path for the configured root and the selected folder. On macOS, /tmp may resolve to /private/tmp, so inconsistent aliases can make Whombat skip the recording or reject the path.\n\nThe file structure was saved and reopened with soundevent 2.10.0 using synthetic audio. Keep the original .t2n notebook; this export is one-way.\n\nThe AOEF files omit person, username and email fields. In the synthetic Whombat 0.9.0 import, annotations remained without a creator identity. The Talk2Nature sidecar preserves recording/session/individual/annotator IDs, optional animal context, notes and any Station source journal. These can identify people, animals or places. This ZIP is unencrypted: inspect all files and remove details you do not want to share.\n\nTags are preliminary human-entered observations, not animal-language decoding or model predictions. Unknown context is not silence. Rights, consent, privacy, accuracy and admission for research are not established. Nothing was uploaded or played automatically.\n`;
  const files = [
    {name: 'recording.wav', bytes: new Uint8Array(audio)},
    {name: 'dataset.aoef.json', bytes: encodeJSON(dataset)},
    {name: 'annotation-project.aoef.json', bytes: encodeJSON(project)},
    {name: 'talk2nature-annotations.json', bytes: sourceJSON},
    {name: 'export-report.json', bytes: encodeJSON(report)},
    {name: 'READ-ME.txt', bytes: encoder.encode(instructions)}
  ];
  if (files.reduce((total, file) => total + file.bytes.length, 0) > 26 * 1048576) throw Error('The AOEF package exceeds 26 MB. Use a shorter WAV; keep the original notebook.');
  return files;
}

export async function aoefPackage(audio, labels) {
  return zipFiles(await aoefFiles(audio, labels));
}
