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
    id: 'parrot-and-phrase',
    title: 'A parrot and a phrase',
    setup: 'A person says “hello.” Later in the same clip, a parrot makes a similar-sounding phrase. No response-choice test is shown.',
    claims: [
      { text: 'The person spoke, then the parrot made a similar sound.', category: 'observed', explanation: 'That sequence is directly described. Similar sound does not alone establish what the parrot understood.' },
      { text: 'The parrot understood the word “hello.”', category: 'unknown', explanation: 'The clip does not show whether the parrot understands the word. A suitable test would be needed.' },
      { text: 'The parrot was trying to make the person laugh.', category: 'possible', explanation: 'That is a playful interpretation, but the scene does not establish the parrot’s intention.' }
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
