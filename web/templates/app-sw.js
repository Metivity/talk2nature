// Public shell only. Audio, notes, credentials and runtime responses are never cached.
const REVISION = '__REVISION__';
const ASSETS = __ASSETS__;
const SCOPE_PATH = __SCOPE__;
const PREFIX = `talk2nature-shell:${SCOPE_PATH}:`;
const CACHE = PREFIX + REVISION;
const allowed = new Set(ASSETS.map(path => new URL(path, self.location.origin).href));
self.addEventListener('install', event => {
  event.waitUntil((async () => {
    try {
      const cache = await caches.open(CACHE);
      await cache.addAll([...allowed].map(url => new Request(url, {credentials:'omit', cache:'reload'})));
    } catch (error) { await caches.delete(CACHE); throw error; }
  })());
});
self.addEventListener('activate', event => {
  event.waitUntil((async () => {
    for (const key of await caches.keys()) if (key.startsWith(PREFIX) && key !== CACHE) await caches.delete(key);
    await self.clients.claim();
  })());
});
self.addEventListener('fetch', event => {
  const request = event.request, url = new URL(request.url), clean = url.origin + url.pathname;
  if (request.method !== 'GET' || request.headers.has('authorization')) return;
  // Asset queries must exactly match this release. Only the known station mode
  // query can reuse a query-free page; never normalize arbitrary URL parameters.
  const stationMode = url.pathname === SCOPE_PATH+'station/' &&
    [...url.searchParams.keys()].length === 1 &&
    ['outdoor','companion','parrot','demo'].includes(url.searchParams.get('mode'));
  const key = allowed.has(url.href) ? url.href : stationMode && allowed.has(clean) ? clean : null;
  if (!key) return;
  event.respondWith((async () => {
    const cached = await (await caches.open(CACHE)).match(key);
    return cached || fetch(request);
  })());
});
self.addEventListener('message', event => {
  if (event.data?.type !== 'SHELL_STATUS' || !event.ports[0]) return;
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE);
    const available = await Promise.all([...allowed].map(url => cache.match(url)));
    event.ports[0].postMessage({ready:available.every(Boolean), revision:REVISION});
  })());
});
// A new worker waits for existing app windows to close; never reload a recording.
