import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {test} from 'node:test';
import {compareAnnotations,parseAnnotationText} from '../web/assets/annotation-compare.mjs';

const fixture=name=>JSON.parse(readFileSync(new URL(`../examples/annotation-observer-${name}.synthetic.json`,import.meta.url),'utf8'));

test('synthetic reports retain every positive overlap and unmatched events without consensus',()=>{
  const report=compareAnnotations(fixture('a'),fixture('b'));
  assert.equal(report.report_schema,'talk2nature.annotation-comparison.v1');
  assert.equal(report.annotation_counts.a,2);
  assert.equal(report.annotation_counts.b,3);
  assert.equal(report.positive_overlap_pair_count,2);
  assert.deepEqual(report.pairwise_overlaps.map(p=>[p.event_a_id,p.event_b_id,p.temporal_iou,p.kind_a,p.kind_b,p.kind_exact_match]),[[1,10,.6,'vocalization','uncertain',false],[2,11,1,'other sound','other sound',true]]);
  assert.deepEqual(report.event_ids_without_positive_overlap,{a:[],b:[12]});
  assert.match(report.method,/no one-to-one assignment/);
  assert.equal(JSON.stringify(report).includes('annotator_id'),false);
  assert.equal(JSON.stringify(report).includes('Private note must not appear'),false);
});

test('one event can overlap multiple independent intervals and stays one-to-many',()=>{
  const a=fixture('a'),b=fixture('b');
  a.events=[{...a.events[0],start_seconds:1,end_seconds:4}];
  b.events=[{...b.events[0],start_seconds:1,end_seconds:2},{...b.events[0],id:13,start_seconds:3,end_seconds:4}];
  const report=compareAnnotations(a,b);
  assert.deepEqual(report.pairwise_overlaps.map(p=>[p.event_a_id,p.event_b_id]),[[1,10],[1,13]]);
});

test('context is compared only when both exports declare independent observations',()=>{
  const a=fixture('a'),b=fixture('b');
  a.events=[{...a.events[0],context:'feeding',context_source:'direct observation'}];
  b.events=[{...b.events[0],context:'moving',context_source:'synchronized video'}];
  let pair=compareAnnotations(a,b).pairwise_overlaps[0];
  assert.equal(pair.context_comparison,'different_declared_category');
  assert.deepEqual([pair.context_a,pair.context_b],['feeding','moving']);
  b.events[0].context='unknown';b.events[0].context_source='not observed';
  pair=compareAnnotations(a,b).pairwise_overlaps[0];
  assert.equal(pair.context_comparison,'not_comparable_from_independent_context');
  assert.deepEqual([pair.context_a,pair.context_b],[null,null]);
});

test('mismatched source declarations and repeated annotator IDs fail closed',()=>{
  const a=fixture('a'),b=fixture('b');
  b.recording.sha256='0'.repeat(64);
  assert.throws(()=>compareAnnotations(a,b),/same WAV checksum/);
  b.recording.sha256=a.recording.sha256;b.recording.annotator_id=a.recording.annotator_id;
  assert.throws(()=>compareAnnotations(a,b),/same annotator ID/);
});

test('annotation parser rejects invalid JSON, unsupported formats and oversized input',()=>{
  assert.throws(()=>parseAnnotationText('{'),/valid JSON/);
  assert.throws(()=>parseAnnotationText(JSON.stringify({...fixture('a'),schema:'other'})),/Unsupported annotation format/);
  assert.throws(()=>parseAnnotationText(' '.repeat(2*1024*1024+1)),/over the 2 MB limit/);
});
