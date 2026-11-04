import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';

const read = path => readFile(new URL(path, import.meta.url), 'utf8');

test('saved-moment actions appear before the research explainer and accept only session ZIPs', async () => {
  const html = await read('../web/templates/compare.html');
  assert.ok(html.indexOf('compare-workbench') < html.indexOf('compare-evidence'));
  assert.match(html, /class="file-picker compare-file-picker"[^>]*for="file-a"/);
  assert.match(html, /Session ZIP · up to 27 MB · no unzipping/);
  assert.match(html, /id="file-a" accept="\.zip,application\/zip" aria-label="Choose the first saved Talk2Nature session ZIP"/);
  assert.match(html, /id="file-b" accept="\.zip,application\/zip" aria-label="Choose a second saved Talk2Nature session ZIP"/);
});

test('every public file import uses the shared touch-sized, labelled picker', async () => {
  const [listen, annotations, compare, design] = await Promise.all([
    read('../web/templates/listen.html'), read('../web/templates/annotation-compare.html'),
    read('../web/templates/compare.html'), read('../web/assets/design.css'),
  ]);
  const inputs = [listen, annotations, compare].join('\n').match(/<input[^>]+type="file"[^>]*>/g) ?? [];
  assert.equal(inputs.length, 7);
  for (const input of inputs) assert.match(input, /aria-label="Choose/);
  for (const id of ['wav-file', 'session-zip-file', 'labels-file', 'annotation-file-a', 'annotation-file-b']) {
    assert.match(`${listen}\n${annotations}`, new RegExp(`class="file-picker[^\"]*"[^>]*for="${id}"`));
  }
  assert.match(design, /\.file-picker input\[type=file\]\{position:absolute;inset:0;width:100%;height:100%;margin:0;opacity:0/);
  assert.match(design, /\.file-picker:focus-within\{outline:/);
});
