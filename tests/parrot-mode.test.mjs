import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {stationPreset} from '../web/assets/station-preset.mjs';

test('parrot visit starts with a complete observer-declared moment, without identifying a species',()=>{
  const preset=stationPreset('parrot');
  assert.deepEqual(preset,{captureMode:'window',animalContext:{group:'parrot',species:'',basis:'observer-declared'}});
  preset.animalContext.species='budgerigar';
  assert.equal(stationPreset('parrot').animalContext.species,'');
  assert.equal(stationPreset('companion'),null);
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
