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
  const records = [
    { dataset: { kind: 'dataset', researchUse: 'conditional' }, textContent: 'Wild bird audio dataset and review limits', hidden: false },
    { dataset: { kind: 'paper', researchUse: 'unresolved' }, textContent: 'Fungal signal measurement paper', hidden: false },
    { dataset: { kind: 'code', researchUse: 'not_admitted' }, textContent: 'Bird annotation tool source code', hidden: false },
  ];
  const document = { getElementById: id => elements[id] ?? null, querySelectorAll: selector => selector === '.resource-entry' ? records : [] };
  vm.runInNewContext(script, { document });
  return { elements, records };
}

test('resource search, type and research-use filters are composable and reset accessibly', () => {
  const { elements, records } = harness();
  elements['resource-search'].value = 'bird';
  elements['resource-search'].listeners.input();
  assert.deepEqual(records.map(record => record.hidden), [false, true, false]);
  assert.equal(elements['resource-count'].textContent, '2 of 3 resources shown');

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
