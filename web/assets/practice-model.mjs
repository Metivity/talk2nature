export const CATEGORIES = Object.freeze([
  { id: 'observed', label: 'Directly observed' },
  { id: 'possible', label: 'Possible explanation' },
  { id: 'unknown', label: 'Not established' }
]);

export const SCENES = Object.freeze([
  {
    id: 'sound-no-video',
    title: 'A sound, no video',
    setup: 'A four-second recording contains three short calls at 08:14. There is no video and no second microphone.',
    claims: [
      { text: 'The recording contains three short calls.', category: 'observed', explanation: 'The scene states this directly. It does not identify a caller or explain the calls.' },
      { text: 'A second animal answered.', category: 'unknown', explanation: 'One recording with three calls does not tell us how many animals called.' },
      { text: 'The caller was warning a neighbor.', category: 'possible', explanation: 'That is a possible explanation, but this scene contains no evidence that establishes a warning.' }
    ]
  },
  {
    id: 'turn-after-call',
    title: 'A turn after a call',
    setup: 'A video shows a bird turn its head shortly after a call is heard. The camera and microphone clocks have not been synchronized.',
    claims: [
      { text: 'The video shows a bird turn its head.', category: 'observed', explanation: 'That movement is directly described in the scene.' },
      { text: 'The bird may have heard the call.', category: 'possible', explanation: 'It is a possible explanation. A movement near a sound does not by itself establish what the bird heard.' },
      { text: 'The call caused the bird to turn.', category: 'unknown', explanation: 'The clocks are not synchronized, and timing alone would not establish cause.' }
    ]
  },
  {
    id: 'parrot-reported-name',
    title: 'A reported name',
    setup: 'An invented note says a parrot used its dog’s name after the dog barked. A short audio clip includes a similar phrase, but the dog is off-camera and nothing was checked against other situations.',
    claims: [
      { text: 'The caregiver reports a phrase after the dog barks.', category: 'observed', explanation: 'The invented note says that. It records what the caregiver reported; it does not independently check the timing.' },
      { text: 'The phrase may be linked to the dog or its bark.', category: 'possible', explanation: 'That is one possible explanation. The scene does not compare other dogs, other sounds or other moments.' },
      { text: 'The parrot uses this name to identify this one dog.', category: 'unknown', explanation: 'The note and similar-sounding clip do not show whether the parrot identifies the dog or repeats a phrase around a familiar cue. A fair test would compare other dogs and situations.' }
    ]
  }
]);

export function reviewClaim(sceneIndex, claimIndex, selectedCategory) {
  const claim = SCENES[sceneIndex]?.claims[claimIndex];
  if (!claim || !CATEGORIES.some(category => category.id === selectedCategory)) {
    throw new RangeError('Choose a statement and one of the listed review labels.');
  }
  return {
    matchesThisScene: claim.category === selectedCategory,
    explanation: claim.explanation
  };
}
