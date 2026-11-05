import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {bindFilePicker, showFileSelection} from '../web/assets/file-picker.mjs';

const read = path => readFile(new URL(path, import.meta.url), 'utf8');

test('saved-moment actions appear before the research explainer and accept only session ZIPs', async () => {
  const html = await read('../web/templates/compare.html');
  assert.ok(html.indexOf('compare-workbench') < html.indexOf('compare-evidence'));
  assert.match(html, /class="file-picker compare-file-picker"[^>]*for="file-a"/);
  assert.match(html, /ZIP up to 27 MB/);
  assert.match(html, /id="file-a" accept="\.zip,application\/zip" aria-label="Choose the first saved Talk2Nature session ZIP from this device"/);
  assert.match(html, /id="file-b" accept="\.zip,application\/zip" aria-label="Choose a second saved Talk2Nature session ZIP from this device"/);
});

test('every public file import uses the shared touch-sized, labelled picker', async () => {
  const [listen, annotations, compare, design] = await Promise.all([
    read('../web/templates/listen.html'), read('../web/templates/annotation-compare.html'),
    read('../web/templates/compare.html'), read('../web/assets/design.css'),
  ]);
  const inputs = [listen, annotations, compare].join('\n').match(/<input[^>]+type="file"[^>]*>/g) ?? [];
  assert.equal(inputs.length, 7);
  assert.match(listen, /id="wav-file" type="file" accept="\.wav,\.t2n,audio\/wav,audio\/x-wav"/);
  assert.doesNotMatch(listen, /id="wav-file"[^>]*application\/octet-stream/);
  const selectedNames = [listen, annotations, compare].join('\n').match(/data-selected-file aria-live="polite" hidden/g) ?? [];
  assert.equal(selectedNames.length, inputs.length);
  for (const input of inputs) assert.match(input, /aria-label="(?:Open|Choose)/);
  for (const id of ['wav-file', 'session-zip-file', 'labels-file', 'annotation-file-a', 'annotation-file-b']) {
    assert.match(`${listen}\n${annotations}`, new RegExp(`class="file-picker[^\"]*"[^>]*for="${id}"`));
  }
  assert.match(design, /\.file-picker input\[type=file\]\{position:absolute;inset:0;width:100%;height:100%;margin:0;opacity:0/);
  assert.match(design, /\.file-picker:focus-within\{outline:/);
});

test('selected filename is shown in the local file picker and can be cleared', () => {
  const output = {textContent: '', title: '', hidden: true};
  const label = {querySelector: selector => selector === '[data-selected-file]' ? output : null};
  const input = {closest: selector => selector === '.file-picker' ? label : null};
  assert.equal(showFileSelection(input, {name: 'evening-song.t2n'}), true);
  assert.equal(output.textContent, 'Selected on this device: evening-song.t2n · Tap to choose another');
  assert.equal(output.title, 'evening-song.t2n');
  assert.equal(output.hidden, false);
  assert.equal(showFileSelection(input, null), false);
  assert.equal(output.textContent, '');
  assert.equal(output.hidden, true);
});

test('file picker names phone file locations and avoids relying on desktop-only drop instructions', async () => {
  const [listen, annotations, compare] = await Promise.all([
    read('../web/templates/listen.html'), read('../web/templates/annotation-compare.html'), read('../web/templates/compare.html'),
  ]);
  for (const page of [listen, annotations, compare]) {
    assert.match(page, /Files or Downloads/);
    assert.doesNotMatch(page, /computer: drop here/);
  }
});

test('file actions say what opens and do not use an external-link arrow', async () => {
  const [listen, compare] = await Promise.all([read('../web/templates/listen.html'), read('../web/templates/compare.html')]);
  const actions = `${listen}\n${compare}`.match(/<span class="file-picker-action">[^<]*(?:<span[^>]*>[^<]*<\/span>)?<\/span>/g) ?? [];
  assert.ok(actions.length >= 5);
  assert.match(listen, /Choose a sound or notebook/);
  assert.match(listen, /Choose a Station session ZIP/);
  assert.match(listen, /Choose saved labels for this sound/);
  assert.match(compare, /Choose a session ZIP/);
  assert.match(compare, /Choose a second session ZIP/);
  assert.doesNotMatch(actions.join(' '), /↗/);
});

test('file picker opens one accepted dropped file through the normal change path', () => {
  const listeners = {}, output = {textContent: '', hidden: true};
  const classes = new Set();
  const picker = {
    dataset: {}, querySelector: selector => selector === '[data-selected-file]' ? output : null,
    addEventListener: (name, fn) => { listeners[name] = fn; },
    classList: {toggle: (name, enabled) => enabled ? classes.add(name) : classes.delete(name)},
    contains: () => false,
  };
  const input = {
    accept: '.zip,application/zip',
    closest: selector => selector === '.file-picker' ? picker : null,
    dispatchEvent: event => { input.changed = event.type === 'change' && event.bubbles; },
  };
  class Transfer { constructor() { this.items = {add: file => { this.files = [file]; }}; } }
  assert.equal(bindFilePicker(input, {DataTransferClass: Transfer, EventClass: Event}), true);
  const prevented = {value: false};
  listeners.dragover({preventDefault: () => { prevented.value = true; }});
  assert.equal(prevented.value, true);
  assert.ok(classes.has('file-picker-over'));
  listeners.drop({preventDefault() {}, dataTransfer: {files: [{name: 'station-session.zip', type: 'application/zip'}]}});
  assert.equal(input.files[0].name, 'station-session.zip');
  assert.equal(input.changed, true);
  assert.equal(classes.has('file-picker-over'), false);
});

test('file picker announces unsupported drops and never opens more than one file', () => {
  const listeners = {}, output = {textContent: '', hidden: true};
  const picker = {dataset: {}, querySelector: () => output, addEventListener: (name, fn) => { listeners[name] = fn; }, classList: {toggle() {}}, contains: () => false};
  const input = {accept: '.json,application/json', closest: () => picker};
  class Transfer { constructor() { this.items = {add: () => {}}; } }
  bindFilePicker(input, {DataTransferClass: Transfer, EventClass: Event});
  listeners.drop({preventDefault() {}, dataTransfer: {files: [{name: 'notes.txt', type: 'text/plain'}]}});
  assert.match(output.textContent, /does not match/);
  listeners.drop({preventDefault() {}, dataTransfer: {files: [{name: 'a.json', type: 'application/json'}, {name: 'b.json', type: 'application/json'}]}});
  assert.match(output.textContent, /one file at a time/);
});

test('homepage title and description name the project focus in searchable language', async () => {
  const build = await read('../web/build.py');
  assert.match(build, /Open-source animal communication research and bioacoustic tools/);
  assert.match(build, /Open-source animal communication research, bioacoustics and local tools for documenting animal sounds/);
  assert.match(build, /\{url\('contribute\/'\)\}\">Join the project/);
});

test('the app home makes saved-file import obvious without opening More tools', async () => {
  const html = await read('../web/templates/app.html');
  const link = html.indexOf('Already have a recording? Choose a sound or saved notebook');
  const moreTools = html.indexOf('app-more-tools-panel');
  assert.ok(link >= 0 && (moreTools < 0 || link < moreTools));
  assert.match(html, /href="\{\{base\}\}\/app\/review\/"/);
});
