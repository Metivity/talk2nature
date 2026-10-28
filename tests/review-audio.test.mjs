import test from 'node:test';
import assert from 'node:assert/strict';
import {createReviewAudioControls} from '../web/assets/review-audio.mjs';

function harness({rejectPlay=false}={}) {
  const state={confirm:false,confirmations:[],plays:0,pauses:0};
  const target=()=>({listeners:{},addEventListener(name,fn){this.listeners[name]=fn;},setAttribute(name,value){this[name]=value;}});
  const audio=Object.assign(target(),{paused:true,ended:false,currentTime:0,duration:NaN,async play(){state.plays++;if(rejectPlay)throw Error('blocked');this.ended=false;this.paused=false;this.listeners.play?.();},pause(){state.pauses++;this.paused=true;this.listeners.pause?.();}});
  const button=Object.assign(target(),{textContent:'',attributes:{},setAttribute(name,value){this.attributes[name]=value;}});
  const seek=Object.assign(target(),{value:'0',max:'0'}),time={textContent:''},status={textContent:''};
  const controls=createReviewAudioControls({audio,button,seek,time,status,confirm:message=>{state.confirmations.push(message);return state.confirm;}});
  return {state,audio,button,seek,time,status,controls};
}

test('review audio stays silent until a just-in-time confirmation and supports seek and pause',async()=>{
  const h=harness();h.controls.reset(83.4);
  assert.equal(h.time.textContent,'0:00 / 1:23');
  await h.button.listeners.click();
  assert.equal(h.state.plays,0);assert.match(h.status.textContent,/not played/);
  assert.match(h.state.confirmations[0],/Right before playback/);
  assert.match(h.state.confirmations[0],/headphones or review away/);
  h.seek.value='12.5';h.seek.listeners.input();assert.equal(h.audio.currentTime,12.5);assert.equal(h.state.plays,0);
  h.state.confirm=true;await h.button.listeners.click();
  assert.equal(h.state.plays,1);assert.equal(h.button.textContent,'Pause review');
  const prompts=h.state.confirmations.length;await h.button.listeners.click();
  assert.equal(h.state.confirmations.length,prompts);assert.equal(h.audio.paused,true);assert.equal(h.button.textContent,'Play for human review');
});

test('replay after the clip ends requires a fresh confirmation and starts from zero',async()=>{
  const h=harness();h.controls.reset(4);h.state.confirm=true;await h.button.listeners.click();
  h.audio.currentTime=4;h.audio.ended=true;h.audio.paused=true;h.audio.listeners.ended();
  await h.button.listeners.click();
  assert.equal(h.state.confirmations.length,2);assert.equal(h.audio.currentTime,0);assert.equal(h.state.plays,2);
});

test('browser playback rejection is reported without losing the local file',async()=>{
  const h=harness({rejectPlay:true});h.controls.reset(2);h.state.confirm=true;await h.button.listeners.click();
  assert.match(h.status.textContent,/could not start/);assert.equal(h.state.confirmations.length,1);
});
