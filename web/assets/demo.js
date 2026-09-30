import {initialState, scenes, canAccept, transition} from './demo-model.mjs';

const $ = selector => document.querySelector(selector);
const all = selector => document.querySelectorAll(selector);
let state = initialState();
const titleCase = value => value[0].toUpperCase() + value.slice(1);
function permissions(observation) {
  return `Private review: allowed · Research training: ${observation.training ? 'allowed' : 'not allowed'} · Publication: not allowed`;
}
function render(moveFocus = false) {
  const step = ['observe', 'review'].includes(state.stage) ? state.stage : 'outcome';
  all('[data-stage]').forEach(item => {
    if (item.dataset.stage === step) item.setAttribute('aria-current', 'step');
    else item.removeAttribute('aria-current');
  });
  ['observe', 'review', 'outcome'].forEach(name => { $(`#${name}-panel`).hidden = name !== step; });
  $('#scene-description').textContent = scenes[state.scene].description;
  $('#scene-art').classList.toggle('obstructed', state.scene === 'hidden');
  all('[data-scene]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.scene === state.scene)));
  const observation = state.observation;
  $('#record-observation').textContent = {
    observe: 'Waiting for your label', review: 'In the demo review queue', accepted: 'Accepted for permitted use',
    rejected: 'Rejected — excluded from training', withdrawn: 'Withdrawn — example cleared',
  }[state.stage];
  $('#record-permissions').textContent = observation ? `${titleCase(observation.behavior)}. ${permissions(observation)}.`
    : state.stage === 'withdrawn' ? 'The demo observation and its permissions have been removed.' : 'Permissions have not been selected.';
  $('#record-release').textContent = {none: 'Not created', available: 'Available in this demo', revoked: 'Revoked after withdrawal'}[state.release];
  $('#record-release-detail').textContent = state.release === 'revoked'
    ? 'The demo release is no longer available for reuse.'
    : state.release === 'available' ? 'One invented observation. No export or model training took place.'
    : observation && !observation.training ? 'The observer did not allow research training.' : 'Requires an accepted label and separate training permission.';
  if (step === 'review') {
    $('#review-scene').textContent = scenes[observation.scene].description;
    $('#review-label').textContent = titleCase(observation.behavior);
    $('#review-permissions').textContent = permissions(observation);
    $('#review-guidance').textContent = canAccept(state)
      ? 'The description supports this label. Check the permissions and each review item before accepting.'
      : observation.behavior === 'unknown' ? 'Unknown is a useful answer when evidence is missing. It can stay in the review queue, but cannot enter this demo’s labeled training release. You can reject or withdraw the example.'
      : 'The description does not support this label. Do not infer a behavior you cannot observe. Reject or withdraw this example, then try again.';
    $('#accept-button').disabled = !canAccept(state);
  }
  if (step === 'outcome') {
    const released = state.release === 'available';
    const outcomes = {
      accepted: [released ? 'Ready for permitted reuse.' : 'Reviewed. Still your choice.',
        released ? 'The demo release contains one invented observation with training permission.' : 'The example passed review. Its permissions still determine what can happen next.',
        observation?.training ? 'A training release must preserve the study, session, review and permissions. This demonstration does not establish scientific suitability.' : 'Training was not allowed, so this example cannot enter a training release. Private review does not override that choice.'],
      rejected: ['A useful boundary.', 'This example was rejected and cannot enter a training release.', 'A rejected observation is still a record of a decision. In this demo you can withdraw it, or reset and try another scene.'],
      withdrawn: ['The example is withdrawn.', 'Its observation and permissions have been cleared from the walkthrough.', state.release === 'revoked' ? 'The dependent demo release has also been revoked. In a real service, withdrawal needs a deletion process for stored media and backups; it cannot guarantee recall of downloaded copies or reverse completed model training.' : 'No training release remains. A real service must also handle stored media, backups and any already distributed copies.'],
    };
    const [heading, description, detail] = outcomes[state.stage];
    $('#outcome-heading').textContent = heading;
    $('#outcome-description').textContent = description;
    $('#outcome-detail').textContent = detail;
    $('#release-button').hidden = state.stage !== 'accepted' || released;
    $('#release-button').disabled = !observation?.training;
    $('#release-note').hidden = state.stage !== 'accepted';
  }
  all('[data-withdraw]').forEach(button => { button.hidden = state.stage === 'withdrawn'; });
  if (moveFocus) $(`#${step}-heading`).focus();
}
function dispatch(action, message) {
  try {
    const previous = state;
    state = transition(state, action);
    if (action.type === 'reset' || action.type === 'withdraw') {
      $('#observation-form').reset();
      $('#review-form').reset();
      $('#review-scene').textContent = '';
      $('#review-label').textContent = '';
      $('#review-permissions').textContent = '';
    }
    render(previous.stage !== state.stage || action.type === 'release');
    $('#demo-message').textContent = message;
  } catch (error) {
    $('#demo-message').textContent = error.message;
  }
}
all('[data-scene]').forEach(button => button.addEventListener('click', () => {
  all('input[name="behavior"]').forEach(input => { input.checked = false; });
  dispatch({type: 'scene', scene: button.dataset.scene}, 'Scene changed. Choose a label based on the new description.');
}));
$('#observation-form').addEventListener('submit', event => {
  event.preventDefault();
  dispatch({type: 'submit', behavior: new FormData(event.currentTarget).get('behavior'), review: $('#allow-review').checked, training: $('#allow-training').checked}, 'Invented observation added to the demo review queue.');
});
$('#review-form').addEventListener('submit', event => {
  event.preventDefault();
  const data = new FormData(event.currentTarget);
  dispatch({type: 'accept', checks: Object.fromEntries(['rights', 'consent', 'privacy', 'label'].map(key => [key, data.has(key)]))}, 'Demo observation accepted with its original permissions.');
});
$('#reject-button').addEventListener('click', () => dispatch({type: 'reject'}, 'Demo observation rejected.'));
$('#release-button').addEventListener('click', () => dispatch({type: 'release'}, 'Demo release created. No data was exported and no model was trained.'));
all('[data-withdraw]').forEach(button => button.addEventListener('click', () => dispatch({type: 'withdraw'}, 'Example withdrawn. Any dependent demo release has been revoked.')));
$('#reset-button').addEventListener('click', () => dispatch({type: 'reset'}, 'Demo reset. No choices have been saved.'));
$('#observation-form').reset();
$('#review-form').reset();
render();
$('#demo-app').hidden = false;
