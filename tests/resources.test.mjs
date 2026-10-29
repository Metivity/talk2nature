import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';
import vm from 'node:vm';

const script = await readFile(new URL('../web/assets/resources.js', import.meta.url), 'utf8');

function harness() {
  const elements = Object.fromEntries(['resource-search','resource-kind','resource-research-use','resource-count','resource-reset','resource-empty']
    .map(id => [id, { value: '', textContent: '', hidden: false, listeners: {}, addEventListener(name, fn) { this.listeners[name] = fn; }, focus() { this.focused = true; } }]));
  elements['resource-kind'].value = 'all';
  elements['resource-research-use'].value = 'all';
  let textReads = 0;
  const resource = (kind, researchUse, text) => ({
    dataset: { kind, researchUse },
    get textContent() { textReads += 1; return text; },
    hidden: false,
  });
  const records = [
    resource('dataset', 'conditional', 'Wild bird audio dataset and review limits. Declared license: CC BY 4.0.'),
    resource('paper', 'unresolved', 'Fungal signal measurement paper'),
    resource('code', 'not_admitted', 'Bird annotation tool source code'),
  ];
  const document = { getElementById: id => elements[id] ?? null, querySelectorAll: selector => selector === '.resource-entry' ? records : [] };
  vm.runInNewContext(script, { document });
  return { elements, records, textReads: () => textReads };
}

test('resource search, type and research-use filters are composable and reset accessibly', () => {
  const { elements, records } = harness();
  elements['resource-search'].value = 'bird';
  elements['resource-search'].listeners.input();
  assert.deepEqual(records.map(record => record.hidden), [false, true, false]);
  assert.equal(elements['resource-count'].textContent, '2 of 3 resources shown');

  elements['resource-search'].value = 'cc by 4.0';
  elements['resource-search'].listeners.input();
  assert.deepEqual(records.map(record => record.hidden), [false, true, true]);

  elements['resource-kind'].value = 'dataset';
  elements['resource-kind'].listeners.change();
  assert.deepEqual(records.map(record => record.hidden), [false, true, true]);
  assert.equal(elements['resource-empty'].hidden, true);

  elements['resource-research-use'].value = 'conditional';
  elements['resource-research-use'].listeners.change();
  assert.deepEqual(records.map(record => record.hidden), [false, true, true]);

  elements['resource-research-use'].value = 'unresolved';
  elements['resource-research-use'].listeners.change();
  assert.deepEqual(records.map(record => record.hidden), [true, true, true]);
  assert.equal(elements['resource-empty'].hidden, false);

  elements['resource-search'].value = 'mushroom';
  elements['resource-search'].listeners.input();
  assert.deepEqual(records.map(record => record.hidden), [true, true, true]);
  assert.equal(elements['resource-empty'].hidden, false);

  elements['resource-reset'].listeners.click();
  assert.deepEqual(records.map(record => record.hidden), [false, false, false]);
  assert.equal(elements['resource-search'].value, '');
  assert.equal(elements['resource-kind'].value, 'all');
  assert.equal(elements['resource-research-use'].value, 'all');
  assert.equal(elements['resource-search'].focused, true);
  assert.equal(elements['resource-reset'].hidden, true);
});

test('resource text is indexed once and reused across search and filter edits', () => {
  const { elements, textReads } = harness();
  assert.equal(textReads(), 3);

  for (const query of ['bird', 'annotation', 'no match']) {
    elements['resource-search'].value = query;
    elements['resource-search'].listeners.input();
  }
  elements['resource-kind'].value = 'dataset';
  elements['resource-kind'].listeners.change();
  elements['resource-research-use'].value = 'conditional';
  elements['resource-research-use'].listeners.change();

  assert.equal(textReads(), 3, 'filter updates should reuse the rendered-text index');
});
