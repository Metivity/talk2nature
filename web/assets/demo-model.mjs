// A browser-only rehearsal. No backend requests, authentication, storage or real data.
export const scenes = Object.freeze({
  visible: Object.freeze({
    description: 'Bird A moves from the left end of a perch to the right, then hops to a second perch. No food is visible.',
    supported: 'moving',
  }),
  hidden: Object.freeze({
    description: 'Bird A is behind an opaque screen for the entire interval. You cannot see its body, position or any food.',
    supported: 'unknown',
  }),
});
const behaviors = new Set(['moving', 'resting', 'feeding', 'unknown']);
export const initialState = () => ({stage: 'observe', scene: 'visible', observation: null, release: 'none'});
export function canAccept(state) {
  return state.observation !== null && state.observation.behavior !== 'unknown'
    && state.observation.behavior === scenes[state.observation.scene].supported;
}
export function transition(state, action) {
  if (action.type === 'reset') return initialState();
  if (action.type === 'scene' && state.stage === 'observe' && Object.hasOwn(scenes, action.scene)) {
    return {...state, scene: action.scene};
  }
  if (action.type === 'submit' && state.stage === 'observe') {
    if (!behaviors.has(action.behavior) || action.review !== true || typeof action.training !== 'boolean') {
      throw new Error('Choose a behavior and allow private review before adding an example.');
    }
    return {...state, stage: 'review', observation: {
      scene: state.scene, behavior: action.behavior, review: true, training: action.training, publication: false,
    }};
  }
  if (action.type === 'accept' && state.stage === 'review') {
    if (!canAccept(state) || !['rights', 'consent', 'privacy', 'label'].every(key => action.checks?.[key] === true)) {
      throw new Error('Acceptance needs all four checks and a label supported by the scene. Unknown stays unresolved.');
    }
    return {...state, stage: 'accepted'};
  }
  if (action.type === 'reject' && state.stage === 'review') return {...state, stage: 'rejected'};
  if (action.type === 'release' && state.stage === 'accepted' && state.release === 'none') {
    if (!state.observation.training) throw new Error('This example has no permission for research training.');
    return {...state, release: 'available'};
  }
  if (action.type === 'withdraw' && state.observation && state.stage !== 'withdrawn') {
    return {...state, stage: 'withdrawn', observation: null, release: state.release === 'available' ? 'revoked' : 'none'};
  }
  throw new Error('That action is not available at this step.');
}
