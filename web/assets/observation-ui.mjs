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
