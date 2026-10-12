(() => {
  const search = document.getElementById('resource-search');
  const kind = document.getElementById('resource-kind');
  const count = document.getElementById('resource-count');
  const reset = document.getElementById('resource-reset');
  const empty = document.getElementById('resource-empty');
  const records = [...document.querySelectorAll('.resource-entry')];
  if (!search || !kind || !count || !reset || !empty || records.length === 0) return;

  const update = () => {
    const query = search.value.trim().toLocaleLowerCase();
    const selectedKind = kind.value;
    let shown = 0;
    for (const record of records) {
      const matches = (selectedKind === 'all' || record.dataset.kind === selectedKind)
        && (!query || record.textContent.toLocaleLowerCase().includes(query));
      record.hidden = !matches;
      if (matches) shown += 1;
    }
    count.textContent = `${shown} of ${records.length} resources shown`;
    empty.hidden = shown !== 0;
    reset.hidden = !query && selectedKind === 'all';
  };

  search.addEventListener('input', update);
  kind.addEventListener('change', update);
  reset.addEventListener('click', () => {
    search.value = '';
    kind.value = 'all';
    update();
    search.focus();
  });
})();
