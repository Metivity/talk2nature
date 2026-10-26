import {announceWaitingUpdate,resolveRedundantWorker,watchWaitingWorker} from './app-update.mjs';
import {appNavOverlapsControls} from './app-nav-visibility.mjs';
const base = new URL('../app/', import.meta.url), $ = id => document.getElementById(id);
const modes = {
  outdoor: ['OUTDOOR VOICES','A moment in the wild.','Watch from a distance. Mark naturally occurring calls, movement and changes in the setting.','Outdoor moment','A bird moved to another branch. Its identity is uncertain.'],
  companion: ['SHARED MOMENTS','Get to know the everyday.','Observe any animal naturally. Choose a group if you know it, or leave the identity unsure. Mark visible behavior and naturally occurring voices; leave meaning open.','Shared moment','The animal moved toward the window while I was already speaking.'],
  parrot: ['PARROT FIELD VISIT','A little time together.','Observe a parrot in its ordinary routine. Keep calls, mimicked speech, nearby human voices and visible context distinct. No sound is translated or answered. You can change the animal group below.','Parrot visit','Mimicked phrase heard; nearby human speech was present too.'],
  demo: ['SYNTHETIC REHEARSAL','Try curiosity on for size.','Use “Try without a microphone” below. Invented tones let you explore the complete workflow without a microphone.','Practice session','A test marker, with no animal present.']
};
const mode = new URL(location.href).searchParams.get('mode');
if ($('scenario-title') && modes[mode]) {
  const [label,title,description,alias,placeholder] = modes[mode];
  $('scenario-label').textContent=label; $('scenario-title').textContent=title; $('scenario-description').textContent=description;
  $('station-alias').value=alias; $('station-note').placeholder=placeholder;
  if (mode === 'demo') { $('station-start').hidden=true; $('station-permission').closest('.station-setup').hidden=true; }
}
for (const a of document.querySelectorAll('.app-nav a')) if (new URL(a.href).pathname===location.pathname && !a.hash) a.setAttribute('aria-current','page');
const appNav = document.querySelector('.app-nav');
if (appNav) {
  const compactViewport = window.matchMedia('(max-width: 800px)');
  const isFixedNav = () => window.getComputedStyle(appNav).position === 'fixed';
  const focusableControls = 'a[href],button:not(:disabled),input:not(:disabled),select:not(:disabled),textarea:not(:disabled),summary,[tabindex]:not([tabindex="-1"])';
  let previousY = Math.max(0, window.scrollY || 0);
  let direction = 0;
  let distance = 0;
  const revealNav = () => {
    document.body.classList.remove('app-nav-away');
    if (!compactViewport.matches || !isFixedNav()) return;
    const style = appNav.style;
    const originalTransform = [style.getPropertyValue('transform'), style.getPropertyPriority('transform')];
    const originalTransition = [style.getPropertyValue('transition'), style.getPropertyPriority('transition')];
    style.setProperty('transition', 'none');
    style.setProperty('transform', 'none');
    const overlaps = appNavOverlapsControls(appNav, document.querySelectorAll(focusableControls), document.activeElement);
    if (overlaps) document.body.classList.add('app-nav-away');
    if (originalTransform[0]) style.setProperty('transform', ...originalTransform);
    else style.removeProperty('transform');
    if (originalTransition[0]) style.setProperty('transition', ...originalTransition);
    else style.removeProperty('transition');
  };
  const hideNav = (instant = false) => {
    if (appNav.contains(document.activeElement)) return;
    if (!instant) {
      document.body.classList.add('app-nav-away');
      return;
    }
    const style = appNav.style;
    const transition = [style.getPropertyValue('transition'), style.getPropertyPriority('transition')];
    style.setProperty('transition', 'none');
    document.body.classList.add('app-nav-away');
    appNav.getBoundingClientRect();
    if (transition[0]) style.setProperty('transition', ...transition);
    else style.removeProperty('transition');
  };
  const syncViewport = () => {
    previousY = Math.max(0, window.scrollY || 0);
    direction = 0;
    distance = 0;
    if (!compactViewport.matches || !isFixedNav() || previousY <= 80) revealNav();
    else hideNav();
  };
  const updateNavOnScroll = () => {
    const y = Math.max(0, window.scrollY || 0);
    const delta = y - previousY;
    previousY = y;
    if (!compactViewport.matches || !isFixedNav()) {
      revealNav();
      direction = 0;
      distance = 0;
      return;
    }
    if (!document.body.classList.contains('app-nav-away') && appNavOverlapsControls(appNav, document.querySelectorAll(focusableControls), document.activeElement)) {
      hideNav(true);
      direction = 0;
      distance = 0;
      return;
    }
    if (!delta) return;
    const nextDirection = Math.sign(delta);
    if (nextDirection !== direction) distance = 0;
    direction = nextDirection;
    distance += Math.abs(delta);
    if (y <= 48) {
      revealNav();
      distance = 0;
    } else if (distance >= 8) {
      if (direction > 0 && y > 80) hideNav();
      else if (direction < 0) revealNav();
      distance = 0;
    }
  };
  window.addEventListener('scroll', updateNavOnScroll, {passive: true});
  window.addEventListener('resize', syncViewport, {passive: true});
  syncViewport();
  if (previousY > 80 && compactViewport.matches && isFixedNav()) hideNav();
  appNav.addEventListener('focusin', revealNav);
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible' && window.scrollY <= 48) revealNav();
  });
}
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
const watchedRegistrations = new WeakSet(), checkedRegistrations = new WeakSet();
function updateReady() {
  announceWaitingUpdate($('app-update-status'),$('offline-status'));
}
async function offlineState() {
  const offline=$('offline-status');
  if (!offline && !$('app-update-status')) return;
  if (!('serviceWorker' in navigator)) { if(offline) offline.textContent='Offline setup is unavailable in this browser.'; const button=$('app-offline'); if(button) button.disabled=true; return; }
  try {
    const registrations=await navigator.serviceWorker.getRegistrations();
    const registered=registrations.find(r=>r.scope===base.href);
    if (offline && registered?.active) {
      const ready=await shellReady(registered.active);
      offline.textContent=ready?'Offline tools are ready on this browser.':'Offline files are missing. Reconnect and use Enable offline tools to repair them.';
      const button=$('app-offline'); if(button) button.textContent=ready?'Check for app updates':'Enable offline tools';
    }
    else if (offline) offline.textContent='Offline tools are optional. Audio and notes stay temporary.';
    if (registered) observeRegistration(registered);
  } catch { if(offline) offline.textContent='Offline status is unavailable. You can use the app online.'; }
}
function shellReady(worker) {
  return new Promise(resolve=>{
    const channel=new MessageChannel(), timer=setTimeout(()=>{channel.port1.close();resolve(false);},3000);
    channel.port1.onmessage=event=>{clearTimeout(timer);channel.port1.close();resolve(event.data?.ready===true);};
    worker.postMessage({type:'SHELL_STATUS'},[channel.port2]);
  });
}
function watchWorker(registration) {
  const watch=worker=>worker?.addEventListener('statechange',async()=>{
    const offline=$('offline-status'), button=$('app-offline');
    if (worker.state==='installed') { if(registration.active) updateReady(); else if(offline) offline.textContent='Offline files saved. Waiting for activation…'; }
    if (worker.state==='activated') { if(offline) offline.textContent='Offline tools are ready on this browser.'; if(button) {button.disabled=false; button.textContent='Check for app updates';} }
    if (worker.state==='redundant') {
      const result=await resolveRedundantWorker(registration,shellReady);
      if(offline) offline.textContent=result.message;
      if(button) {button.disabled=false;button.textContent=result.button;}
    }
  });
  watch(registration.installing); registration.addEventListener('updatefound',()=>watch(registration.installing));
}
function observeRegistration(registration, checkForUpdates=true) {
  if (!watchedRegistrations.has(registration)) {
    watchedRegistrations.add(registration);
    watchWaitingWorker(registration,updateReady);
    watchWorker(registration);
  }
  if (checkForUpdates && !checkedRegistrations.has(registration) && typeof registration.update==='function') {
    checkedRegistrations.add(registration);
    registration.update().catch(()=>{});
  }
}
$('app-offline')?.addEventListener('click', async()=>{
  $('app-offline').disabled=true; $('offline-status').textContent='Saving only public app pages and code…';
  try {
    let r=(await navigator.serviceWorker.getRegistrations()).find(item=>item.scope===base.href);
    if (r?.active && !(await shellReady(r.active))) { await r.unregister(); r=null; }
    r=await navigator.serviceWorker.register(new URL('sw.js',base),{scope:base.href,updateViaCache:'none'});
    observeRegistration(r,false); await r.update(); checkedRegistrations.add(r); if(r.active) await offlineState();
  }
  catch { $('offline-status').textContent='Offline setup failed. You can keep using the app online; try again when connected.'; }
  finally { $('app-offline').disabled=false; }
});
offlineState();
