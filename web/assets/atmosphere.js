/* A little life around the evidence. No audio, storage, network or animation loop. */
(() => {
  'use strict';
  const root = document.documentElement;
  const preference = window.matchMedia('(prefers-reduced-motion: reduce)');
  const control = document.querySelector('#motion-control');
  let enabled = true;
  function updateMotion() {
    const active = enabled && !preference.matches;
    root.classList.toggle('motion-enabled', active);
    if (control) {
      control.hidden = false;
      control.disabled = preference.matches;
      control.setAttribute('aria-pressed', String(active));
      control.textContent = preference.matches ? 'Motion reduced by your device' : `Motion ${active ? 'on' : 'off'}`;
    }
  }
  control?.addEventListener('click', () => { enabled = !enabled; updateMotion(); });
  preference.addEventListener('change', updateMotion);
  updateMotion();

  // Animate only editorial surfaces, once. Content is visible without this code;
  // recording forms, live meters and workbench controls never enter this observer.
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        if (enabled && !preference.matches) entry.target.classList.add('field-arrival');
        observer.unobserve(entry.target);
      }
    }, {threshold: 0.08});
    document.querySelectorAll('.science-invitation > div, .section-heading, .research-card, .frontier-cards > article, .curiosity-garden, .app-hero-copy').forEach(element => observer.observe(element));
    window.addEventListener('pagehide', () => observer.disconnect(), {once: true});
  }

  const choices = [...document.querySelectorAll('[data-curiosity]')];
  const panels = [...document.querySelectorAll('[data-curiosity-panel]')];
  const switcher = document.querySelector('.curiosity-switch');
  if (choices.length && panels.length && switcher) {
    switcher.hidden = false;
    for (const choice of choices) choice.addEventListener('click', () => {
      const selected = choice.dataset.curiosity;
      if (!panels.some(panel => panel.dataset.curiosityPanel === selected)) return;
      choices.forEach(button => button.setAttribute('aria-pressed', String(button === choice)));
      panels.forEach(panel => { panel.hidden = panel.dataset.curiosityPanel !== selected; });
      document.querySelector('#curiosity-status').textContent = `${choice.textContent} selected.`;
    });
  }
})();
