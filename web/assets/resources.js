(() => {
  const search = document.getElementById('resource-search');
  const kind = document.getElementById('resource-kind');
  const researchUse = document.getElementById('resource-research-use');
  const count = document.getElementById('resource-count');
  const reset = document.getElementById('resource-reset');
  const empty = document.getElementById('resource-empty');
  const sharing = document.getElementById('resource-sharing');
  const share = document.getElementById('resource-share');
  const shareStatus = document.getElementById('resource-share-status');
  const shareLink = document.getElementById('resource-share-link');
  const records = [...document.querySelectorAll('.resource-entry')];
  if (!search || !kind || !researchUse || !count || !reset || !empty || records.length === 0) return;
  // The record text is static; normalize it once instead of rereading every full card per keystroke.
  const searchableText = new Map(records.map(record => [record, record.textContent.toLocaleLowerCase()]));
  const kinds = new Set(['all', 'paper', 'dataset', 'code', 'model', 'standard', 'project']);
  const uses = new Set(['all', 'conditional', 'not_admitted', 'unresolved']);
  const cleanQuery = value => value.replace(/[\u0000-\u001f\u007f]/g, ' ').trim().slice(0, 160);
  // Only the three public search fields travel in a deliberately shared link.
  // Typing does not change history or write browser storage.
  const viewUrl = () => {
    const url = new URL(location.href);
    url.search = '';
    url.hash = '';
    const query = cleanQuery(search.value);
    if (query) url.searchParams.set('q', query);
    if (kinds.has(kind.value) && kind.value !== 'all') url.searchParams.set('kind', kind.value);
    if (uses.has(researchUse.value) && researchUse.value !== 'all') url.searchParams.set('use', researchUse.value);
    return url.href;
  };
  const params = new URL(location.href).searchParams;
  search.value = cleanQuery(params.get('q') || '');
  if (kinds.has(params.get('kind'))) kind.value = params.get('kind');
  if (uses.has(params.get('use'))) researchUse.value = params.get('use');

  const update = () => {
    const query = search.value.trim().toLocaleLowerCase();
    const selectedKind = kind.value;
    const selectedResearchUse = researchUse.value;
    let shown = 0;
    for (const record of records) {
      const matches = (selectedKind === 'all' || record.dataset.kind === selectedKind)
        && (selectedResearchUse === 'all' || record.dataset.researchUse === selectedResearchUse)
        && (!query || searchableText.get(record).includes(query));
      record.hidden = !matches;
      if (matches) shown += 1;
    }
    count.textContent = `${shown} of ${records.length} resources shown`;
    empty.hidden = shown !== 0;
    reset.hidden = !query && selectedKind === 'all' && selectedResearchUse === 'all';
    if (shareStatus) shareStatus.textContent = '';
    if (shareLink) { shareLink.hidden = true; shareLink.removeAttribute('href'); }
  };

  search.addEventListener('input', update);
  kind.addEventListener('change', update);
  researchUse.addEventListener('change', update);
  reset.addEventListener('click', () => {
    search.value = '';
    kind.value = 'all';
    researchUse.value = 'all';
    update();
    search.focus();
  });
  if (sharing && share && shareStatus && shareLink) {
    sharing.hidden = false;
    share.hidden = false;
    share.addEventListener('click', async () => {
      const url = viewUrl();
      try {
        await navigator.clipboard.writeText(url);
        shareStatus.textContent = url === viewUrl()
          ? 'Search link copied. Review it before sharing.'
          : 'Previous search link copied. Copy again for the current filters.';
      } catch {
        if (url !== viewUrl()) { shareStatus.textContent = 'Search changed. Copy the current search link when ready.'; return; }
        shareLink.href = url;
        shareLink.hidden = false;
        shareStatus.textContent = 'Copy was unavailable. Open the search link below, then copy its address.';
      }
    });
  }
  update();
})();
