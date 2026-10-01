const base = new URL('../app/', import.meta.url), $ = id => document.getElementById(id);
const modes = {
  outdoor: ['OUTDOOR VOICES','A moment in the wild.','Watch from a distance. Mark naturally occurring calls, movement and changes in the setting.','outdoor-place','A bird moved to another branch. Its identity is uncertain.'],
  companion: ['SHARED MOMENTS','Get to know the everyday.','Observe a familiar animal in its ordinary routine. Mark visible behavior and naturally occurring voices; leave meaning open.','companion-place','The animal moved toward the window while I was already speaking.'],
  demo: ['SYNTHETIC REHEARSAL','Try curiosity on for size.','Use “Try synthetic station” below. Invented tones let you explore the complete workflow without a microphone.','rehearsal','A test marker, with no animal present.']
};
const mode = new URL(location.href).searchParams.get('mode');
if ($('scenario-title') && modes[mode]) {
  const [label,title,description,alias,placeholder] = modes[mode];
  $('scenario-label').textContent=label; $('scenario-title').textContent=title; $('scenario-description').textContent=description;
  $('station-alias').value=alias; $('station-note').placeholder=placeholder;
}
for (const a of document.querySelectorAll('.app-nav a')) if (new URL(a.href).pathname===location.pathname && !a.hash) a.setAttribute('aria-current','page');
let prompt;
window.addEventListener('beforeinstallprompt', event => { event.preventDefault(); prompt=event; if ($('app-install')) $('app-install').hidden=false; });
$('app-install')?.addEventListener('click', async () => {
  if (!prompt) return;
  try { await prompt.prompt(); const result=await prompt.userChoice; $('install-status').textContent=result.outcome==='accepted'?'Installation requested. Check your device’s launcher.':'Installation dismissed. You can keep using the app in your browser.'; }
  catch { $('install-status').textContent='Use your browser menu to add the app to your home screen.'; }
  finally { prompt=null; $('app-install').hidden=true; }
});
window.addEventListener('appinstalled', () => { if ($('install-status')) $('install-status').textContent='Installation reported by your browser.'; if ($('app-install')) $('app-install').hidden=true; });
if (matchMedia('(display-mode: standalone)').matches || navigator.standalone) {
  if ($('install-status')) $('install-status').textContent='You are using the standalone app window.';
}
async function offlineState() {
  if (!$('offline-status')) return;
  if (!('serviceWorker' in navigator)) { $('offline-status').textContent='Offline setup is unavailable in this browser.'; $('app-offline').disabled=true; return; }
  try {
    const registrations=await navigator.serviceWorker.getRegistrations();
    const registered=registrations.find(r=>r.scope===base.href);
    if (registered?.active) {
      const ready=await shellReady(registered.active);
      $('offline-status').textContent=ready?'Offline tools are ready on this browser.':'Offline files are missing. Reconnect and use Enable offline tools to repair them.';
      $('app-offline').textContent=ready?'Check for app updates':'Enable offline tools';
    }
    else $('offline-status').textContent='Offline tools are optional. Audio and notes stay temporary.';
    if (registered?.waiting) $('offline-status').textContent='An update is ready. Export your work, then close every Talk2Nature app window and reopen.';
    if (registered) watchWorker(registered);
  } catch { $('offline-status').textContent='Offline status is unavailable. You can use the app online.'; }
}
function shellReady(worker) {
  return new Promise(resolve=>{
    const channel=new MessageChannel(), timer=setTimeout(()=>{channel.port1.close();resolve(false);},3000);
    channel.port1.onmessage=event=>{clearTimeout(timer);channel.port1.close();resolve(event.data?.ready===true);};
    worker.postMessage({type:'SHELL_STATUS'},[channel.port2]);
  });
}
function watchWorker(registration) {
  const watch=worker=>worker?.addEventListener('statechange',()=>{
    if (worker.state==='installed') $('offline-status').textContent=registration.active?'An update is ready. Export your work, then close all app windows and reopen.':'Offline files saved. Waiting for activation…';
    if (worker.state==='activated') { $('offline-status').textContent='Offline tools are ready on this browser.'; $('app-offline').disabled=false; $('app-offline').textContent='Check for app updates'; }
    if (worker.state==='redundant') { $('offline-status').textContent='Offline setup did not complete. Check your connection and storage, then try again.'; $('app-offline').disabled=false; }
  });
  watch(registration.installing); registration.addEventListener('updatefound',()=>watch(registration.installing));
}
$('app-offline')?.addEventListener('click', async()=>{
  $('app-offline').disabled=true; $('offline-status').textContent='Saving only public app pages and code…';
  try {
    let r=(await navigator.serviceWorker.getRegistrations()).find(item=>item.scope===base.href);
    if (r?.active && !(await shellReady(r.active))) { await r.unregister(); r=null; }
    r=await navigator.serviceWorker.register(new URL('sw.js',base),{scope:base.href,updateViaCache:'none'});
    watchWorker(r); await r.update(); if(r.active) await offlineState();
  }
  catch { $('offline-status').textContent='Offline setup failed. You can keep using the app online; try again when connected.'; }
  finally { $('app-offline').disabled=false; }
});
offlineState();
