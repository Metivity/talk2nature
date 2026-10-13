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
