import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import vm from 'node:vm';

const source=await readFile(new URL('../web/assets/mobile-launch.js',import.meta.url),'utf8');

function harness({clipboardWrite=async()=>{}}={}){
  const ids=['share-status','copy-project','share-project','mobile-feedback-form','feedback-workflow','feedback-outcome','feedback-device','feedback-note','feedback-preview','feedback-report','feedback-status','email-feedback','copy-feedback'];
  const elements=Object.fromEntries(ids.map(id=>[id,{id,value:'',hidden:id==='feedback-preview'||id==='email-feedback',href:'',textContent:'',listeners:{},addEventListener(name,handler){this.listeners[name]=handler},reportValidity(){this.reportedValidity=true},focus(){this.focused=true},select(){this.selected=true}}]));
  let copied='';let networkCalls=0;let storageReads=0;
  const document={currentScript:{src:'https://example.test/talk2nature/assets/mobile-launch.js?v=unit'},getElementById:id=>elements[id]};
  const navigator={clipboard:{writeText:async value=>{copied=value;await clipboardWrite(value);}}};
  const context={document,navigator,URL,encodeURIComponent,fetch:async()=>{networkCalls++;},get localStorage(){storageReads++;return {};}};
  vm.runInNewContext(source,context);
  return {elements,navigator,get copied(){return copied;},get networkCalls(){return networkCalls;},get storageReads(){return storageReads;}};
}

test('feedback report stays local and opens only a user-reviewed email draft',()=>{
  const h=harness();
  h.elements['feedback-workflow'].value='No-mic practice';
  h.elements['feedback-outcome'].value='Finished';
  h.elements['feedback-device'].value='Pixel / Chrome';
  h.elements['feedback-note'].value='The stop button & recap were clear.';
  let prevented=false;
  h.elements['mobile-feedback-form'].listeners.submit({preventDefault(){prevented=true;}});

  assert.equal(prevented,true);
  assert.equal(h.elements['feedback-preview'].hidden,false);
  assert.match(h.elements['feedback-report'].value,/Workflow: No-mic practice/);
  assert.match(h.elements['feedback-report'].value,/What was unclear or useful: The stop button & recap were clear\./);
  assert.match(h.elements['email-feedback'].href,/^mailto:raviv@metivity\.com\?/);
  assert.equal(h.elements['email-feedback'].hidden,false);
  const body=decodeURIComponent(h.elements['email-feedback'].href.split('&body=')[1]);
  assert.equal(body,h.elements['feedback-report'].value);
  assert.match(h.elements['feedback-status'].textContent,/Nothing has been saved or sent/);
  assert.equal(h.elements['feedback-status'].focused,true);
  assert.equal(h.networkCalls,0);
  assert.equal(h.storageReads,0);
});

test('email draft body safely encodes user punctuation and line breaks',()=>{
  const h=harness();
  h.elements['feedback-workflow'].value='Another workflow';
  h.elements['feedback-outcome'].value='Suggestion only';
  h.elements['feedback-note'].value='Button & label\nsecond line';
  h.elements['mobile-feedback-form'].listeners.submit({preventDefault(){}});
  const href=h.elements['email-feedback'].href;
  assert.ok(href.includes('%26'));
  assert.ok(href.includes('%0A'));
  assert.equal(decodeURIComponent(href.split('&body=')[1]),h.elements['feedback-report'].value);
});

test('copy feedback reports success without sending anything',async()=>{
  const h=harness();
  h.elements['feedback-report'].value='A short, anonymous workflow report';
  await h.elements['copy-feedback'].listeners.click();
  assert.equal(h.copied,'A short, anonymous workflow report');
  assert.match(h.elements['feedback-status'].textContent,/Nothing was sent/);
  assert.equal(h.networkCalls,0);
  assert.equal(h.storageReads,0);
});

test('clipboard failure selects the report for manual copying',async()=>{
  const h=harness({clipboardWrite:async()=>{throw new Error('permission denied');}});
  h.elements['feedback-report'].value='Fallback report';
  await h.elements['copy-feedback'].listeners.click();
  assert.equal(h.elements['feedback-report'].focused,true);
  assert.equal(h.elements['feedback-report'].selected,true);
  assert.match(h.elements['feedback-status'].textContent,/selected so you can copy it manually/);
});

test('long notes keep copy available and suppress an unreliable email URL',()=>{
  const h=harness();
  h.elements['feedback-workflow'].value='No-mic practice';
  h.elements['feedback-outcome'].value='Suggestion only';
  h.elements['feedback-note'].value='🐦'.repeat(400);
  h.elements['mobile-feedback-form'].listeners.submit({preventDefault(){}});
  assert.equal(h.elements['feedback-preview'].hidden,false);
  assert.equal(h.elements['email-feedback'].hidden,true);
  assert.match(h.elements['feedback-status'].textContent,/too long for a reliable email link; use Copy report/);
});

test('required choices are checked before a report is prepared',()=>{
  const h=harness();
  h.elements['mobile-feedback-form'].listeners.submit({preventDefault(){}});
  assert.equal(h.elements['mobile-feedback-form'].reportedValidity,true);
  assert.equal(h.elements['feedback-preview'].hidden,true);
});
