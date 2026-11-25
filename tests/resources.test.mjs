import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';
import vm from 'node:vm';

const script = await readFile(new URL('../web/assets/resources.js', import.meta.url), 'utf8');

function harness({href = 'https://example.test/talk2nature/research/resources/', clipboard} = {}) {
  const elements = Object.fromEntries(['resource-search','resource-kind','resource-research-use','resource-count','resource-reset','resource-empty','resource-sharing','resource-share','resource-share-status','resource-share-link']
    .map(id => [id, { value: '', textContent: '', hidden: false, listeners: {}, addEventListener(name, fn) { this.listeners[name] = fn; }, focus() { this.focused = true; }, removeAttribute(name) { delete this[name]; } }]));
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
  let copied;
  const location = {href};
  const context = {document, URL, location, navigator: {clipboard: {writeText: clipboard || (async value => { copied = value; })}}, fetch() { throw new Error('No network request allowed'); }, localStorage: {setItem() {throw new Error('No persistence allowed');}}, history: {replaceState() {throw new Error('No automatic URL change allowed');}}};
  vm.runInNewContext(script, context);
  return { elements, records, textReads: () => textReads, location, copied: () => copied };
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

test('a shared search restores intersecting filters without a network request or history edit', () => {
  const h = harness({href:'https://example.test/talk2nature/research/resources/?q=bird&kind=dataset&use=conditional'});
  assert.deepEqual(h.records.map(record => record.hidden), [false, true, true]);
  assert.equal(h.elements['resource-count'].textContent, '1 of 3 resources shown');
  assert.equal(h.location.href, 'https://example.test/talk2nature/research/resources/?q=bird&kind=dataset&use=conditional');
});

test('copy uses current controls and drops unrelated URL fields and record fragments', async () => {
  const h = harness({href:'https://example.test/talk2nature/research/resources/?ignored=private-text#resource-old'});
  h.elements['resource-search'].value = 'bird & field';
  h.elements['resource-kind'].value = 'dataset';
  h.elements['resource-research-use'].value = 'conditional';
  await h.elements['resource-share'].listeners.click();
  const url = new URL(h.copied());
  assert.equal(url.searchParams.get('q'), 'bird & field');
  assert.equal(url.searchParams.get('kind'), 'dataset');
  assert.equal(url.searchParams.get('use'), 'conditional');
  assert.equal(url.searchParams.get('ignored'), null);
  assert.equal(url.hash, '');
  const reopened = harness({href:url.href});
  assert.equal(reopened.elements['resource-search'].value, 'bird & field');
  assert.equal(reopened.elements['resource-kind'].value, 'dataset');
  assert.match(h.elements['resource-share-status'].textContent, /copied/);
});

test('malformed filters fall back and long query text is bounded', () => {
  const h = harness({href:`https://example.test/talk2nature/research/resources/?kind=not-a-kind&use=cleared&q=${'x'.repeat(400)}%0A`});
  assert.equal(h.elements['resource-kind'].value, 'all');
  assert.equal(h.elements['resource-research-use'].value, 'all');
  assert.equal(h.elements['resource-search'].value.length, 160);
});

test('clipboard denial exposes a usable same-page link and edits clear it', async () => {
  const h = harness({clipboard:async () => {throw new Error('denied');}});
  h.elements['resource-search'].value = 'fungal';
  await h.elements['resource-share'].listeners.click();
  assert.equal(h.elements['resource-share-link'].hidden, false);
  assert.equal(new URL(h.elements['resource-share-link'].href).searchParams.get('q'), 'fungal');
  h.elements['resource-search'].value = 'bird';
  h.elements['resource-search'].listeners.input();
  assert.equal(h.elements['resource-share-link'].hidden, true);
  assert.equal(h.elements['resource-share-link'].href, undefined);
});

test('a pending copy is labeled as the previous search if filters change', async () => {
  let finish;
  const h = harness({clipboard:() => new Promise(resolve => {finish = resolve;})});
  const copying = h.elements['resource-share'].listeners.click();
  h.elements['resource-search'].value = 'new search';
  h.elements['resource-search'].listeners.input();
  finish();
  await copying;
  assert.match(h.elements['resource-share-status'].textContent, /Previous search link/);
});
