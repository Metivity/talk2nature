import { CATEGORIES, SCENES, reviewClaim } from './practice-model.mjs';

const $ = id => document.getElementById(id);
const stage = $('practice-stage');
if (stage) {
  const title = $('practice-title');
  const number = $('practice-number');
  const setup = $('practice-setup');
  const progress = $('practice-progress');
  const claims = $('practice-claims');
  const feedback = $('practice-feedback');
  const next = $('practice-next');
  const finish = $('practice-finish');
  const answers = new Map();
  let sceneIndex = 0;

  function updateNext() {
    const complete = answers.size === SCENES[sceneIndex].claims.length;
    next.disabled = !complete;
    next.textContent = complete
      ? (sceneIndex === SCENES.length - 1 ? 'Finish the practice' : 'Continue to the next scene')
      : 'Review this scene first';
    feedback.textContent = complete
      ? 'Scene reviewed. These are invented examples, not labels for real animals.'
      : 'Choose one label for each statement. You can change your choices.';
  }

  function renderScene() {
    const scene = SCENES[sceneIndex];
    answers.clear();
    title.textContent = scene.title;
    number.textContent = `SCENE ${String(sceneIndex + 1).padStart(2, '0')}`;
    setup.textContent = scene.setup;
    progress.textContent = `Scene ${sceneIndex + 1} of ${SCENES.length}`;
    claims.replaceChildren();

    scene.claims.forEach((claim, claimIndex) => {
      const card = document.createElement('article');
      card.className = 'practice-claim';
      const statement = document.createElement('p');
      statement.className = 'practice-statement';
      statement.textContent = claim.text;
      const choices = document.createElement('div');
      choices.className = 'practice-choices';
      choices.setAttribute('role', 'group');
      choices.setAttribute('aria-label', `Review statement: ${claim.text}`);
      const note = document.createElement('p');
      note.className = 'practice-claim-note';
      note.setAttribute('aria-live', 'polite');

      for (const category of CATEGORIES) {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'practice-choice';
        button.textContent = category.label;
        button.setAttribute('aria-pressed', 'false');
        button.addEventListener('click', () => {
          answers.set(claimIndex, category.id);
          for (const option of choices.querySelectorAll('button')) option.setAttribute('aria-pressed', String(option === button));
          const review = reviewClaim(sceneIndex, claimIndex, category.id);
          note.textContent = `${review.matchesThisScene ? 'This fits the scene.' : 'Compare with the scene.'} ${review.explanation}`;
          updateNext();
        });
        choices.append(button);
      }
      card.append(statement, choices, note);
      claims.append(card);
    });
    updateNext();
  }

  next.addEventListener('click', () => {
    if (next.disabled) return;
    if (sceneIndex < SCENES.length - 1) {
      sceneIndex += 1;
      renderScene();
      title.focus({ preventScroll: true });
      stage.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth', block: 'start' });
    } else {
      stage.hidden = true;
      finish.hidden = false;
      $('practice-finish-title').focus({ preventScroll: true });
      finish.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth', block: 'start' });
    }
  });

  $('practice-again').addEventListener('click', () => {
    sceneIndex = 0;
    finish.hidden = true;
    stage.hidden = false;
    renderScene();
    title.focus({ preventScroll: true });
    stage.scrollIntoView({ behavior: 'instant', block: 'start' });
  });

  renderScene();
}
