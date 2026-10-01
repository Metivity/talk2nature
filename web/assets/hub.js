import {contributionDraft, youtubeEmbed} from './hub-model.mjs';
const $=id=>document.getElementById(id), playerButtons=new WeakMap();
for (const button of document.querySelectorAll('.video-load')) {
  playerButtons.set(button.closest('[data-video-id]'),button);
  button.addEventListener('click', () => {
  const box=button.closest('[data-video-id]'), frame=document.createElement('iframe');
  frame.title=box.dataset.videoTitle; frame.src=youtubeEmbed(box.dataset.videoId);
  frame.allow='encrypted-media; picture-in-picture; fullscreen'; frame.allowFullscreen=true;
  frame.referrerPolicy='strict-origin-when-cross-origin';
  box.replaceChildren(frame); frame.focus();
  });
}
if ($('video-search')) {
  const cards=[...document.querySelectorAll('[data-video-search]')];
  function filter() {
    const words=$('video-search').value.toLowerCase().trim().split(/\s+/).filter(Boolean), category=$('video-category').value;
    let count=0;
    for (const card of cards) {
      const show=words.every(w=>card.dataset.videoSearch.includes(w)) && (category==='all'||category===card.dataset.category);
      card.hidden=!show; if(show) count++;
      // A filtered-out player must not keep playing out of view.
      if (!show && card.querySelector('iframe')) {
        const box=card.querySelector('[data-video-id]'); box.replaceChildren(playerButtons.get(box));
      }
    }
    $('video-count').textContent=`${count} ${count===1?'video':'videos'}`; $('video-empty').hidden=count!==0;
    $('video-reset').hidden=!words.length&&category==='all';
  }
  $('video-search').addEventListener('input',filter); $('video-category').addEventListener('change',filter);
  $('video-reset').addEventListener('click',()=>{$('video-search').value='';$('video-category').value='all';filter();$('video-search').focus();});
}
$('source-proposal')?.addEventListener('submit', event => {
  event.preventDefault(); $('proposal-error').textContent='';
  try {
    const draft=contributionDraft(Object.fromEntries(new FormData(event.currentTarget)));
    $('proposal-body').textContent=draft.body; $('proposal-link').href=draft.url;
    $('proposal-preview').hidden=false; $('proposal-link').focus();
  } catch(error) {$('proposal-error').textContent=error.message; $('proposal-preview').hidden=true;}
});
$('source-proposal')?.addEventListener('input',()=>{$('proposal-preview').hidden=true;});
