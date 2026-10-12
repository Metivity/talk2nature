import test from 'node:test';
import assert from 'node:assert/strict';
import { CATEGORIES, SCENES, reviewClaim } from '../web/assets/practice-model.mjs';

test('practice offers three invented, species-varied scenes with explicit limits',()=>{
  assert.equal(SCENES.length,3);
  assert.deepEqual(SCENES.map(scene=>scene.id),['sound-no-video','turn-after-call','parrot-reported-name']);
  assert.ok(SCENES.every(scene=>scene.setup && scene.claims.length===3));
  assert.ok(SCENES.flatMap(scene=>scene.claims).every(claim=>claim.text && claim.explanation));
});

test('each scene exercises observation, possible explanation and not-established distinctions',()=>{
  assert.deepEqual(CATEGORIES.map(category=>category.id),['observed','possible','unknown']);
  for(const scene of SCENES) assert.deepEqual(new Set(scene.claims.map(claim=>claim.category)),new Set(CATEGORIES.map(category=>category.id)));
});

test('claim review explains evidence boundaries without scoring or inferring meaning',()=>{
  assert.deepEqual(reviewClaim(0,0,'observed'),{
    matchesThisScene:true,
    explanation:'The scene states this directly. It does not identify a caller or explain the calls.'
  });
  assert.deepEqual(reviewClaim(0,1,'observed'),{
    matchesThisScene:false,
    explanation:'One recording with three calls does not tell us how many animals called.'
  });
  assert.throws(()=>reviewClaim(9,0,'observed'),RangeError);
  assert.throws(()=>reviewClaim(0,0,'meaning'),RangeError);
});

test('parrot name practice keeps caregiver report separate from evidence of individual reference',()=>{
  const scene=SCENES.find(item=>item.id==='parrot-reported-name');
  assert.match(scene.setup,/invented note/);
  assert.match(scene.setup,/other situations/);
  assert.equal(reviewClaim(2,0,'observed').matchesThisScene,true);
  assert.equal(reviewClaim(2,1,'possible').matchesThisScene,true);
  const referential=reviewClaim(2,2,'unknown');
  assert.equal(referential.matchesThisScene,true);
  assert.match(referential.explanation,/identifies the dog or repeats a phrase/);
  assert.match(referential.explanation,/compare other dogs and situations/);
});
