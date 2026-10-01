'use strict';
const toggle = document.querySelector('.menu-toggle');
const navigation = document.querySelector('#navigation');
if (toggle && navigation) {
  toggle.closest('header').classList.add('menu-ready');
  function closeMenu() { toggle.setAttribute('aria-expanded', 'false'); navigation.classList.remove('open'); }
  toggle.addEventListener('click', () => {
    const expanded = toggle.getAttribute('aria-expanded') !== 'true';
    toggle.setAttribute('aria-expanded', String(expanded));
    navigation.classList.toggle('open', expanded);
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') { closeMenu(); toggle.focus(); }
  });
  navigation.addEventListener('click', event => { if (event.target.closest('a')) closeMenu(); });
}
const search = document.querySelector('#research-search');
const filter = document.querySelector('#taxon-filter');
const purpose = document.querySelector('#purpose-filter');
const reset = document.querySelector('#research-reset');
if (search && filter) {
  const cards = [...document.querySelectorAll('[data-search]')];
  const count = document.querySelector('#result-count');
  const empty = document.querySelector('#no-results');
  function updateResults() {
    const query = search.value.trim().toLocaleLowerCase();
    const words = query.split(/\s+/).filter(Boolean);
    let matches = 0;
    for (const card of cards) {
      const matchesArea = filter.value === 'all' || card.dataset.taxon === filter.value;
      const matchesText = words.every(word => card.dataset.search.includes(word));
      const matchesPurpose = !purpose || purpose.value === 'all' || card.dataset.purpose === purpose.value;
      card.hidden = !(matchesArea && matchesText && matchesPurpose);
      if (!card.hidden) matches++;
    }
    count.textContent = `${matches} research ${matches === 1 ? 'note' : 'notes'}`;
    empty.hidden = matches !== 0;
    if (reset) reset.hidden = !query && filter.value === 'all' && (!purpose || purpose.value === 'all');
  }
  search.addEventListener('input', updateResults);
  filter.addEventListener('change', updateResults);
  purpose?.addEventListener('change', updateResults);
  reset?.addEventListener('click', () => { search.value = ''; filter.value = 'all'; if (purpose) purpose.value = 'all'; updateResults(); search.focus(); });
  updateResults();
}
