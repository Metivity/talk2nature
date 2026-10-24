const updateReadyMessage='Update ready. Nothing will reload now. Export work you want to keep, then close all Talk2Nature windows and reopen.';

export function announceWaitingUpdate(notice, offline) {
  if (notice) {
    notice.hidden=false;
    notice.textContent=updateReadyMessage;
  } else if (offline) offline.textContent=updateReadyMessage;
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
