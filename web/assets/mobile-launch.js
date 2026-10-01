'use strict';
const projectUrl=new URL('../mobile/',document.currentScript.src).href;
const status=document.getElementById('share-status');
document.getElementById('copy-project')?.addEventListener('click',async()=>{
  try { await navigator.clipboard.writeText(projectUrl); status.textContent='Project link copied. No recordings or notes were included.'; }
  catch { status.textContent=`Copy this public project link: ${projectUrl}`; }
});
document.getElementById('share-project')?.addEventListener('click',async()=>{
  if(!navigator.share){status.textContent='Use Copy link to share the public project page.';return;}
  try {await navigator.share({title:'Talk2Nature — a field companion',text:'Explore sounds and observations with this local-first, open-source app. Try the synthetic rehearsal.',url:projectUrl});status.textContent='Share dialog completed. No recordings or notes were included.';}
  catch(error){status.textContent=error.name==='AbortError'?'Sharing cancelled.':'Sharing is unavailable here. Use Copy link.';}
});
