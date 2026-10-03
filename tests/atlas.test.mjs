import test from 'node:test';
import assert from 'node:assert/strict';
import {filterAtlas,mapClusters} from '../web/assets/atlas-model.mjs';
const records=[
 {id:'bee',title:'Honeybee history',taxon:'Insects',kind:'Lecture',finding:'Dance directions',group:'other_animals',source_year:1973,observation_period:{label:'1949 trial'},location_note:'Austria',place_labels:['Wolfgangsee, Austria'],locations:[{place_id:'a',basis:'A cited site'}]},
 {id:'bat',title:'Bat context',taxon:'Bats',kind:'Study',finding:'Context',group:'mammals',source_year:2016,location_note:'Capture origin',place_labels:['Herzliya, Israel'],locations:[{place_id:'b',basis:'Animal origin'}]},
 {id:'whale',title:'Whale birth',taxon:'Marine mammals',kind:'Observation',finding:'Birth observed in 2023',group:'mammals',source_year:2026,location_note:'Offshore',place_labels:['Dominica'],locations:[{place_id:'c',basis:'Study region'}]},
 {id:'plant',title:'Plant sounds',taxon:'Plants & fungi',kind:'Study',finding:'Sound',group:'plants_fungi',source_year:2023,location_note:'Not checked',locations:[]}
];
const places=[{id:'a',latitude:47.8,longitude:13.4},{id:'b',latitude:32.2,longitude:34.8},{id:'c',latitude:15.4,longitude:-61.5}];
test('all records include unlocated studies; combined filters and reset preserve the source-year distinction',()=>{
 assert.equal(filterAtlas(records).length,4);
 assert.deepEqual(filterAtlas(records,{place:'unmapped'}).map(r=>r.id),['plant']);
 assert.deepEqual(filterAtlas(records,{period:'early'}).map(r=>r.id),['bee']);
 assert.deepEqual(filterAtlas(records,{period:'middle',group:'mammals'}).map(r=>r.id),['bat']);
 assert.deepEqual(filterAtlas(records,{query:'AUSTRIA dance'}).map(r=>r.id),['bee']);
 assert.equal(filterAtlas(records,{query:'nothing'}).length,0);
 assert.equal(filterAtlas(records,{period:'middle',query:'birth'}).length,0);
 assert.equal(filterAtlas(records,{place:'mapped'}).length,3);
 assert.deepEqual(filterAtlas(records,{place:'selection',selected:['a','b']}).map(r=>r.id),['bee','bat']);
 assert.deepEqual(filterAtlas(records,{place:'c'}).map(r=>r.id),['whale']);
});
test('narrow-screen clustering preserves every mapped note without inventing an unknown-location pin',()=>{
 const desktop=mapClusters(records,places,1200),mobile=mapClusters(records,places,320);
 assert.equal(desktop.length,3);assert.ok(mobile.length<desktop.length);
 assert.deepEqual(mobile.flatMap(c=>c.records).sort(),['bat','bee','whale']);
 assert.equal(mobile.some(c=>c.records.includes('plant')),false);
 for(let i=0;i<mobile.length;i++)for(let j=i+1;j<mobile.length;j++)assert.ok(Math.hypot(mobile[i].x-mobile[j].x,mobile[i].y-mobile[j].y)*.32>=52);
 assert.deepEqual(mapClusters(filterAtlas(records,{place:'unmapped'}),places,390),[]);
 assert.throws(()=>mapClusters(records,places,0));
});
test('a study with two places is counted once when their mobile pins merge',()=>{
 const record={...records[0],locations:[{place_id:'a'},{place_id:'b'}]};
 const clusters=mapClusters([record],places,320);assert.equal(clusters.length,1);assert.deepEqual(clusters[0].records,['bee']);assert.equal(clusters[0].places.length,2);
});
