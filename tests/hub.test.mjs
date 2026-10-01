import test from 'node:test';
import assert from 'node:assert/strict';
import {contributionDraft,youtubeEmbed} from '../web/assets/hub-model.mjs';
const sample={kind:'Research question',title:'How & why?',url:'https://www.nature.com/articles/srep39419',depth:'Selected methods',reason:'What about held-out bats?\nKeep unknowns explicit.'};
test('proposal preserves text and opens a draft only in the configured repository',()=>{
  const result=contributionDraft(sample), url=new URL(result.url);
  assert.equal(url.origin,'https://github.com');assert.equal(url.pathname,'/Metivity/talk2nature/issues/new');
  assert.equal(url.searchParams.get('title'),'[Research question] How & why?');
  assert.equal(url.searchParams.get('body'),result.body);assert.ok(result.body.includes(sample.reason));
});
test('unsafe or malformed source links and oversized drafts are rejected',()=>{
  for(const url of ['javascript:alert(1)','http://public.test/','https://user:secret@public.test/','not a url']) assert.throws(()=>contributionDraft({...sample,url}));
  assert.throws(()=>contributionDraft({...sample,reason:'x'.repeat(601)}));
  assert.throws(()=>contributionDraft({...sample,title:' '}));
});
test('video URL is fixed to no-cookie YouTube and cannot inject query parameters',()=>{
  assert.equal(youtubeEmbed('hOWaXi0I2YE'),'https://www.youtube-nocookie.com/embed/hOWaXi0I2YE?autoplay=0&rel=0');
  for(const id of ['https://evil.test','hOWaXi0I2YE?autoplay=1','../test']) assert.throws(()=>youtubeEmbed(id));
});
