// A convenience for observer-selected studies; never an automatic animal ID.
export function stationPreset(mode) {
  if (mode !== 'parrot') return null;
  return {
    captureMode: 'window',
    animalContext: {group: 'parrot', species: '', basis: 'observer-declared'}
  };
}
