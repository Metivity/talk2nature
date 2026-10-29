(() => {
  const search = document.getElementById('graph-search');
  const kindFilter = document.getElementById('graph-kind-filter');
  const count = document.getElementById('graph-count');
  const empty = document.getElementById('graph-empty');
  const list = document.getElementById('graph-records');
  const rows = [...document.querySelectorAll('.graph-record')];
  if (!search || !kindFilter || !count || !empty || !list || rows.length === 0) return;

  // Search the already-rendered record text and only keep supplemental terms in the
  // HTML attribute. This avoids duplicating long findings, limitations and rights text.
  const searchableText = new Map(rows.map(row => [row,
    `${row.textContent || ''} ${row.dataset.search || ''} ${row.id || ''}`.toLowerCase()]));
  const names = {note: 'research notes', resource: 'resources', source: 'source citations'};
  const update = () => {
    const terms = search.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
    const selectedKind = kindFilter.value;
    let visible = 0;
    for (const row of rows) {
      const matches = (selectedKind === 'all' || row.dataset.kind === selectedKind)
        && terms.every(term => searchableText.get(row).includes(term));
      row.hidden = !matches;
      if (matches) visible++;
    }
    const noun = selectedKind === 'all' ? 'catalog records' : names[selectedKind];
    count.textContent = `Showing ${visible} of ${rows.length} ${noun}.`;
    empty.hidden = visible !== 0;
  };

  search.addEventListener('input', update);
  kindFilter.addEventListener('change', update);
  list.addEventListener('click', event => {
    const link = event.target.closest('a[href^="#"]');
    if (!link) return;
    const target = document.getElementById(decodeURIComponent(link.getAttribute('href').slice(1)));
    if (!target?.classList.contains('graph-record')) return;
    target.open = true;
    if (!target.hidden) return;

    event.preventDefault();
    search.value = '';
    kindFilter.value = 'all';
    update();
    history.pushState(null, '', `#${target.id}`);
    requestAnimationFrame(() => {
      target.scrollIntoView({block: 'start'});
      target.querySelector('summary')?.focus({preventScroll: true});
    });
  });
})();
