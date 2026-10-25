const updateReadyMessage='A new version is ready. Save any moment you want to keep, close all Talk2Nature tabs or windows, then reopen the app.';

export function announceWaitingUpdate(notice, offline) {
  if (notice) {
    notice.hidden=false;
    notice.textContent=updateReadyMessage;
  } else if (offline) offline.textContent=updateReadyMessage;
}

export function redundantWorkerStatus(hasActiveWorker, activeShellReady) {
  if (hasActiveWorker && activeShellReady) return {
    message: 'Offline tools are ready on this browser.',
    button: 'Check for app updates'
  };
  if (hasActiveWorker) return {
    message: 'Offline files are missing. Reconnect and use Enable offline tools to repair them.',
    button: 'Enable offline tools'
  };
  return {
    message: 'Offline setup did not complete. Check your connection and storage, then try again.',
    button: 'Enable offline tools'
  };
}

export async function resolveRedundantWorker(registration, shellReady) {
  const active=registration.active;
  let ready=false;
  if (active) {
    try { ready=await shellReady(active)===true; }
    catch { ready=false; }
  }
  return redundantWorkerStatus(Boolean(active),ready);
}

export function watchWaitingWorker(registration, onReady) {
  let announced = false;
  const check = () => {
    if (announced || !registration.waiting) return;
    announced = true;
    onReady(registration.waiting);
  };
  const watch = worker => worker?.addEventListener('statechange', check);
  watch(registration.installing);
  registration.addEventListener('updatefound', () => {
    watch(registration.installing);
    check();
  });
  check();
  return check;
}
