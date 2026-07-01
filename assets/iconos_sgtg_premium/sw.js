const CACHE_NAME = 'sgtg-pwa-v1';
const OFFLINE_URLS = [
  '/',
  '/manifest.json',
  '/iconos_sgtg_premium/favicon.ico',
  '/iconos_sgtg_premium/icon_192x192.png',
  '/iconos_sgtg_premium/icon_512x512.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(OFFLINE_URLS)));
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => Promise.all(keys.map((key) => key !== CACHE_NAME && caches.delete(key))))
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;

  event.respondWith(
    fetch(event.request)
      .then((response) => {
        const copy = response.clone();
        if (response && response.status === 200) {
          const cache = caches.open(CACHE_NAME);
          cache.then((cache) => cache.put(event.request, copy));
        }
        return response;
      })
      .catch(() => caches.match(event.request).then((cached) => cached || caches.match('/')))
  );
});
