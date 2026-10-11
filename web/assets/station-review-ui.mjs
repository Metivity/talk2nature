export function emptyEventsMessage(session, active = false) {
  if (!session) return 'Your first sound event will appear here.';

  const discarded = Array.isArray(session.discarded) ? session.discarded : [];
  if (discarded.length && session.mode === 'window') {
    return 'The whole-moment audio was discarded. Its discard status remains in the session record; the audio itself is gone.';
  }
  if (discarded.length) {
    const manuallyDiscarded = discarded.filter(event => !event.reason).length;
    const storageOmitted = discarded.filter(event => event.reason === 'storage_limit').length;
    const otherOmitted = discarded.length - manuallyDiscarded - storageOmitted;
    const details = [];
    if (manuallyDiscarded) {
      details.push(`${manuallyDiscarded} ${manuallyDiscarded === 1 ? 'clip was' : 'clips were'} discarded; event IDs and timing remain in the journal.`);
    }
    if (storageOmitted) {
      details.push(`${storageOmitted} ${storageOmitted === 1 ? 'sound candidate could' : 'sound candidates could'} not be kept because the local storage limit was reached.`);
    }
    if (otherOmitted) details.push(`${otherOmitted} additional ${otherOmitted === 1 ? 'sound candidate was' : 'sound candidates were'} not retained.`);
    return `No clips are retained. ${details.join(' ')}`;
  }

  if (session.mode === 'window') {
    return active
      ? 'Your full 30-second moment will appear here when recording stops.'
      : 'No audio window was retained. An early stop or interruption is not a complete 30-second observation.';
  }
  return active
    ? 'No sound clips yet. A quiet detector reading does not prove silence.'
    : 'No sound clips were detected. This does not establish that the setting was silent.';
}

export function nextEventFocusId(events, removedIndex) {
  if (!Array.isArray(events) || events.length === 0 || !Number.isInteger(removedIndex) || removedIndex < 0) return null;
  return events[Math.min(removedIndex, events.length - 1)]?.id ?? null;
}
