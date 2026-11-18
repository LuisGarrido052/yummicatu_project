const CACHE_PREFIX = 'yummi-catu-public-v1';
const STATIC_CACHE = `${CACHE_PREFIX}-static`;
const PAGE_CACHE = `${CACHE_PREFIX}-pages`;
const PUBLIC_PAGES = new Set(['/', '/quienes-somos/', '/galeria/', '/formulario/']);

self.addEventListener('install', event => {
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil((async () => {
    const names = await caches.keys();
    await Promise.all(names.filter(name => name.startsWith(CACHE_PREFIX) && name !== STATIC_CACHE && name !== PAGE_CACHE).map(name => caches.delete(name)));
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', event => {
  const request = event.request;
  if (request.method !== 'GET') return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  if (request.destination === 'style' || request.destination === 'script' || request.destination === 'image') {
    event.respondWith((async () => {
      const cached = await caches.match(request);
      if (cached) return cached;
      const response = await fetch(request);
      if (response.ok) {
        const cache = await caches.open(STATIC_CACHE);
        cache.put(request, response.clone());
      }
      return response;
    })());
    return;
  }

  if (request.mode === 'navigate' && PUBLIC_PAGES.has(url.pathname)) {
    event.respondWith((async () => {
      try {
        const response = await fetch(request);
        if (response.ok) {
          const cache = await caches.open(PAGE_CACHE);
          cache.put(request, response.clone());
        }
        return response;
      } catch (error) {
        const cached = await caches.match(request);
        return cached || new Response('Yummi Catu no está disponible sin conexión hasta que la página haya sido visitada.', {
          status: 503,
          headers: {'Content-Type': 'text/plain; charset=utf-8'},
        });
      }
    })());
  }
});
