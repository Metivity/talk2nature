const legacyLabels = new Map([
  ['my-listening-place', 'Listening session'],
  ['outdoor-place', 'Outdoor moment'],
  ['companion-place', 'Shared moment'],
  ['parrot-visit', 'Parrot visit'],
  ['rehearsal', 'Practice session']
]);

export function sessionLabel(alias) {
  if (typeof alias !== 'string' || !alias.trim()) return 'Saved moment';
  const label = alias.trim();
  return legacyLabels.get(label) ?? label;
}
