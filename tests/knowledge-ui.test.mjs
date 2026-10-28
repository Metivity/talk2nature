import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

test('evidence map searches all record types and combines terms with type filtering', () => {
  const input = {value: '', addEventListener(event, fn) { this.oninput = fn; }};
  const type = {value: 'all', addEventListener(event, fn) { this.onchange = fn; }};
  const count = {textContent: ''}, empty = {hidden: true};
  const list = {addEventListener(event, fn) { this.onclick = fn; }};
  const rows = [
    {dataset: {search: 'fungi slow signals', kind: 'note'}, hidden: false},
    {dataset: {search: 'fungi data rights', kind: 'resource'}, hidden: false},
    {dataset: {search: 'bird calls', kind: 'source'}, hidden: false},
  ];
  let pushedHash = '', focused = false, scrolled = false;
  Object.assign(rows[2], {
    id: 'source-1', open: false,
    classList: {contains: name => name === 'graph-record'},
    scrollIntoView: () => { scrolled = true; },
    querySelector: () => ({focus: () => { focused = true; }}),
  });
  const elements = {'graph-search': input, 'graph-kind-filter': type,
    'graph-count': count, 'graph-empty': empty, 'graph-records': list, 'source-1': rows[2]};
  const context = vm.createContext({document: {
    getElementById: id => elements[id],
    querySelectorAll: () => rows,
  }, history: {pushState: (_state, _title, hash) => { pushedHash = hash; }},
  requestAnimationFrame: fn => fn()});
  // The shared classic site script already declares this binding.
  vm.runInContext('const search = null;', context);
  vm.runInContext(fs.readFileSync(new URL('../web/assets/knowledge.js', import.meta.url), 'utf8'), context);

  input.value = 'FUNGI'; input.oninput();
  assert.equal(rows[0].hidden, false);
  assert.equal(rows[1].hidden, false);
  assert.equal(rows[2].hidden, true);
  assert.match(count.textContent, /2 of 3 catalog records/);

  type.value = 'resource'; type.onchange();
  assert.equal(rows[0].hidden, true);
  assert.equal(rows[1].hidden, false);
  assert.match(count.textContent, /1 of 3 resources/);

  input.value = 'fungi missing'; input.oninput();
  assert.equal(empty.hidden, false);
  input.value = ''; input.oninput();
  assert.equal(empty.hidden, true);
  assert.equal(rows[1].hidden, false);

  let prevented = false;
  list.onclick({target: {closest: () => ({getAttribute: () => '#source-1'})},
    preventDefault: () => { prevented = true; }});
  assert.equal(prevented, true);
  assert.equal(input.value, '');
  assert.equal(type.value, 'all');
  assert.equal(rows[2].hidden, false);
  assert.equal(rows[2].open, true);
  assert.equal(pushedHash, '#source-1');
  assert.equal(scrolled, true);
  assert.equal(focused, true);
});
