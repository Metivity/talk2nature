// Observer declarations for a local notebook, never an automatic identification.
export const ANIMAL_GROUPS = [
  ['unknown', 'Not sure yet', 'Describe what you saw. A sound alone does not establish which animal made it.'],
  ['parrot', 'Parrot', 'Add the species if you know it. Keep natural calls, mimicked words and human speech distinct in your notes.'],
  ['dog', 'Dog', 'Describe visible movement and who was nearby. Do not label a bark as an emotion or a translated sentence.'],
  ['cat', 'Cat', 'Note the ordinary activity around a sound. Let the animal continue its routine; do not provoke a meow.'],
  ['other_bird', 'Other bird', 'Observe from a distance. If several birds are present, leave the caller unknown unless you actually saw it.'],
  ['other_mammal', 'Other mammal', 'Record what you can observe safely. This phone tool is not an ultrasonic bat detector or an underwater recorder.'],
  ['amphibian', 'Amphibian', 'A chorus may contain several callers. Note overlap and uncertainty; do not approach or handle animals for a recording.'],
  ['reptile', 'Reptile', 'Movement and setting may be more informative than audible sound. No detected sound does not mean no communication.'],
  ['fish', 'Fish', 'You can record observations, but a phone microphone does not establish underwater sound or fish communication.'],
  ['invertebrate', 'Insect or other invertebrate', 'Note the setting and visible movement. This tool does not measure substrate vibrations or identify the caller.'],
  ['other_animal', 'Another animal', 'Any animal can be part of an observation. Describe its visible behavior and leave unsupported meaning open.'],
  ['multiple', 'Several animals / mixed scene', 'Keep each caller uncertain unless independently observed. A group label does not assign every sound to an animal.']
];
export const unknownAnimal = () => ({group:'unknown', species:'', basis:'observer-declared'});
export function validateAnimal(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value) || Object.keys(value).sort().join(',') !== 'basis,group,species' || !ANIMAL_GROUPS.some(([id]) => id === value.group) || value.basis !== 'observer-declared' || typeof value.species !== 'string' || value.species.length > 80 || value.species !== value.species.trim() || /[\u0000-\u001f\u007f]/.test(value.species)) throw Error('Choose an animal group and use a species label of at most 80 characters.');
  return {group:value.group, species:value.species, basis:value.basis};
}
