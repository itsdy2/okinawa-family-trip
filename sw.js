const CACHE_PREFIX = 'okinawa-trip-';
const CACHE_NAME = `${CACHE_PREFIX}v4`;
const SHELL = [
  './index.html',
  './ja.html',
  './site.webmanifest',
  './assets/trip.css',
  './assets/trip.js',
  './assets/app-icon-192.png',
  './assets/app-icon-512.png',
  './assets/app-icon.svg',
  './assets/day-1.jpg',
  './assets/day-2-v2.jpg',
  './assets/day-4.jpg'
];

self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', event => {
  event.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(key => key.startsWith(CACHE_PREFIX) && key !== CACHE_NAME).map(key => caches.delete(key))))
    .then(() => self.clients.claim()));
});

self.addEventListener('fetch', event => {
  const request = event.request;
  const url = new URL(request.url);
  if (request.method !== 'GET' || url.origin !== self.location.origin) return;

  if (request.mode === 'navigate') {
    event.respondWith((async () => {
      const fallback = new URL(url.pathname.endsWith('/ja.html') ? './ja.html' : './index.html', self.registration.scope);
      try {
        const response = await fetch(request, { cache: 'no-cache' });
        if (response.status >= 500) throw new Error('Page temporarily unavailable');
        if (response.ok) await (await caches.open(CACHE_NAME)).put(fallback, response.clone());
        return response;
      } catch {
        const cache = await caches.open(CACHE_NAME);
        return await cache.match(fallback);
      }
    })());
    return;
  }

  if (url.pathname.includes('/assets/') || url.pathname.endsWith('/site.webmanifest')) {
    event.respondWith((async () => {
      const cache = await caches.open(CACHE_NAME);
      const cached = await cache.match(request);
      if (cached) return cached;
      const response = await fetch(request);
      if (response.ok) await cache.put(request, response.clone());
      return response;
    })());
  }
});
