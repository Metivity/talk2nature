(() => {
const search = document.getElementById('graph-search');
if (search) search.addEventListener('input', () => {
  const terms = search.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
  let visible = 0;
  for (const row of document.querySelectorAll('.graph-record')) {
    row.hidden = !terms.every(term => row.dataset.search.includes(term));
    if (!row.hidden) visible++;
  }
  document.getElementById('graph-count').textContent = `${visible} evidence notes · Open a note to follow its sources.`;
  document.getElementById('graph-empty').hidden = visible !== 0;
});

})();
