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
  assert.match(home,/href="\{\{base\}\}\/app\/station\/\?mode=companion#station-console">Set up a 30-second moment/);
  assert.match(home,/href="\{\{base\}\}\/app\/station\/\?mode=demo#station-console"[^>]*>Try without a microphone/);
  assert.match(app,/companion: \['SHARED MOMENTS'/);
  assert.match(app,/demo: \['SYNTHETIC REHEARSAL'/);
  for(const label of ['Outdoor moment','Shared moment','Parrot visit','Practice session']) assert.ok(app.includes(`'${label}'`),label);
  assert.doesNotMatch(app,/'outdoor-place'|'companion-place'|'parrot-visit'|'rehearsal'/);
});

test('the beginner recording view keeps elapsed time visible and folds technical readings into Advanced',async()=>{
  const station=await readFile(new URL('../web/templates/station.html',import.meta.url),'utf8');
  assert.match(station,/<div class="station-progress"><span id="station-time">00:00<\/span><small>time observed<\/small><\/div>/);
  assert.match(station,/<label>A short name for this moment<input id="station-alias" value="Listening session"/);
  assert.doesNotMatch(station,/Station alias/);
  assert.match(station,/<details id="station-advanced-instruments" class="station-settings station-advanced-instruments"><summary>Advanced · sound level and storage details<\/summary>[\s\S]*?id="station-scope"[\s\S]*?id="station-level"[\s\S]*?id="station-event-total"[\s\S]*?id="station-memory"[\s\S]*?<\/details>/);
  assert.match(station,/id="station-stop" class="station-stop"/);
});

test('optional setting notes start collapsed so the primary save action is closer after Stop',async()=>{
  const station=await readFile(new URL('../web/templates/station.html',import.meta.url),'utf8');
  const start=station.indexOf('<details id="station-soundscape-details" class="station-soundscape-disclosure">');
  const end=station.indexOf('</details>',start);
  assert.ok(start>=0&&end>start,'soundscape notes use a native disclosure');
  const disclosure=station.slice(start,end+'</details>'.length);
  assert.match(disclosure,/<summary>Optional · sounds around you<\/summary>/);
  assert.doesNotMatch(disclosure.slice(0,disclosure.indexOf('>')+1),/\sopen(?:\s|>)/);
  assert.match(disclosure,/id="station-soundscape-context"/);
  for(const category of ['people_or_machines','other_animals','weather_or_water','another_surrounding_sound','mixed_or_uncertain']) assert.ok(disclosure.includes(`value="${category}"`),category);
  assert.ok(end<station.indexOf('id="station-bundle"'),'the primary save action follows optional setting notes');
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
