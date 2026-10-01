import {wavBytes} from './station-model.mjs';

// Small, uncompressed ZIPs avoid a dependency and work with ordinary file managers.
// Only generated, flat filenames are accepted. No imports or filesystem paths.
export function zipFiles(files) {
  if (!files.length || files.length > 26) throw Error('Invalid session file count.');
  const names = new Set(), parts = [], directory = [];
  let offset = 0, total = 0;
  for (const {name, bytes} of files) {
    if (!/^[a-zA-Z0-9][a-zA-Z0-9_.-]{0,119}$/.test(name) || names.has(name) || !(bytes instanceof Uint8Array)) throw Error('Invalid session file.');
    names.add(name); total += bytes.length;
    if (total > 26 * 1048576) throw Error('Session export exceeds its size limit.');
    const filename = new TextEncoder().encode(name);
    let crc = 0xffffffff;
    for (const byte of bytes) {
      crc ^= byte;
      for (let bit = 0; bit < 8; bit++) crc = (crc >>> 1) ^ (crc & 1 ? 0xedb88320 : 0);
    }
    crc = (crc ^ 0xffffffff) >>> 0;
    const header = new Uint8Array(30 + filename.length), h = new DataView(header.buffer);
    h.setUint32(0, 0x04034b50, true); h.setUint16(4, 20, true);
    h.setUint16(12, 33, true); // ZIP's fixed 1980-01-01 date; actual time is in JSON.
    h.setUint32(14, crc, true); h.setUint32(18, bytes.length, true); h.setUint32(22, bytes.length, true);
    h.setUint16(26, filename.length, true); header.set(filename, 30);
    const central = new Uint8Array(46 + filename.length), c = new DataView(central.buffer);
    c.setUint32(0, 0x02014b50, true); c.setUint16(4, 20, true); c.setUint16(6, 20, true);
    c.setUint16(14, 33, true); c.setUint32(16, crc, true);
    c.setUint32(20, bytes.length, true); c.setUint32(24, bytes.length, true);
    c.setUint16(28, filename.length, true); c.setUint32(42, offset, true); central.set(filename, 46);
    parts.push(header, bytes); directory.push(central); offset += header.length + bytes.length;
  }
  const size = directory.reduce((n, b) => n + b.length, 0);
  const end = new Uint8Array(22), e = new DataView(end.buffer);
  e.setUint32(0, 0x06054b50, true); e.setUint16(8, files.length, true); e.setUint16(10, files.length, true);
  e.setUint32(12, size, true); e.setUint32(16, offset, true);
  return new Blob([...parts, ...directory, end], {type: 'application/zip'});
}

export async function sessionFiles(session, alias, settings, digest = bytes => crypto.subtle.digest('SHA-256', bytes)) {
  if (!session?.stopped) throw Error('Stop the session before saving it.');
  const record = session.exportRecord(alias, settings);
  // Snapshot both metadata and audio before the first asynchronous hash.
  const files = session.events.map(event => ({name: session.audioFilename(event.id), bytes: new Uint8Array(wavBytes(event.pcm, session.sampleRate))}));
  for (let i = 0; i < files.length; i++) {
    const hash = await digest(files[i].bytes);
    record.events[i].audio_sha256 = [...new Uint8Array(hash)].map(b => b.toString(16).padStart(2, '0')).join('');
  }
  const encode = text => new TextEncoder().encode(text);
  files.unshift({name: `talk2nature-${session.id}.json`, bytes: encode(JSON.stringify(record, null, 2) + '\n')});
  files.push({name: 'READ-ME.txt', bytes: encode('Talk2Nature session\n\nUnzip this folder to find your session journal (JSON) and retained sound clips (WAV).\nThe journal contains clip checksums, observations and declared origin. Discarded audio is not included.\n\nTo examine a clip, open Talk2Nature > Review a recording and choose one WAV.\nThis session journal cannot be imported as Listen labels; they are different formats.\nKeep the original journal alongside any new annotation export.\n\nReview recordings and notes before sharing. This ZIP is not encrypted.\nNo files have been uploaded. These are preliminary observations, not verified research data or animal translations.\n')});
  return files;
}
