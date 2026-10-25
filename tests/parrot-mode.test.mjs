import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {stationPreset} from '../web/assets/station-preset.mjs';

test('parrot visit starts with a complete observer-declared moment, without identifying a species',()=>{
  const preset=stationPreset('parrot');
  assert.deepEqual(preset,{captureMode:'window',animalContext:{group:'parrot',species:'',basis:'observer-declared'}});
  preset.animalContext.species='budgerigar';
  assert.equal(stationPreset('parrot').animalContext.species,'');
  assert.deepEqual(stationPreset('companion'),{captureMode:'window'});
});

test('shared moments default to one whole 30-second observation without guessing an animal',()=>{
  const preset=stationPreset('companion');
  assert.deepEqual(preset,{captureMode:'window'});
  assert.equal(preset.animalContext,undefined);
});

test('the public first actions lead to the shared-moment and microphone-free routes',async()=>{
  const [home,app]=await Promise.all([
    readFile(new URL('../web/templates/app.html',import.meta.url),'utf8'),
    readFile(new URL('../web/assets/app.js',import.meta.url),'utf8')
  ]);
  assert.match(home,/href="\{\{base\}\}\/app\/station\/\?mode=companion#station-console">Start a 30-second moment/);
  assert.match(home,/href="\{\{base\}\}\/app\/station\/\?mode=demo#station-console"[^>]*>Try without a microphone/);
  assert.match(app,/companion: \['SHARED MOMENTS'/);
  assert.match(app,/demo: \['SYNTHETIC REHEARSAL'/);
});

test('the beginner recording view keeps elapsed time visible and folds technical readings into Advanced',async()=>{
  const station=await readFile(new URL('../web/templates/station.html',import.meta.url),'utf8');
  assert.match(station,/<div class="station-progress"><span id="station-time">00:00<\/span><small>time observed<\/small><\/div>/);
  assert.match(station,/<details id="station-advanced-instruments" class="station-settings station-advanced-instruments"><summary>Advanced · sound level and storage details<\/summary>[\s\S]*?id="station-scope"[\s\S]*?id="station-level"[\s\S]*?id="station-event-total"[\s\S]*?id="station-memory"[\s\S]*?<\/details>/);
  assert.match(station,/id="station-stop" class="station-stop"/);
});

test('the app offers a parrot visit and wires it to the editable animal picker',async()=>{
  const [home,app,station]=await Promise.all([
    readFile(new URL('../web/templates/app.html',import.meta.url),'utf8'),
    readFile(new URL('../web/assets/app.js',import.meta.url),'utf8'),
    readFile(new URL('../web/assets/station.js',import.meta.url),'utf8')
  ]);
  assert.match(home,/app\/station\/\?mode=parrot/);
  assert.match(home,/calls, mimicked words, nearby human voices and visible context separately/);
  assert.match(app,/parrot: \['PARROT FIELD VISIT'/);
  assert.match(station,/stationPreset\(new URL\(location\.href\)\.searchParams\.get\('mode'\)\)/);
  assert.match(station,/animal\.set\(preset\.animalContext\)/);
});
