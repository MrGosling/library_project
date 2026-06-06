/* eslint-env serviceworker */
/* global self, caches, fetch */

// Версия кэша. Меняйте при обновлении логики кэширования.
const CACHE_VERSION = 'v1';
const STATIC_CACHE = `library-static-${CACHE_VERSION}`;
const RUNTIME_CACHE = `library-runtime-${CACHE_VERSION}`;
const API_CACHE = `library-api-${CACHE_VERSION}`;

// Базовые ресурсы для оболочки приложения (app shell).
const PRECACHE_URLS = ['/', '/index.html', '/manifest.webmanifest', '/favicon.svg'];

// Установка: предварительное кэширование оболочки приложения.
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches
      .open(STATIC_CACHE)
      .then((cache) => cache.addAll(PRECACHE_URLS))
      .then(() => self.skipWaiting())
  );
});

// Активация: удаляем устаревшие версии кэша.
self.addEventListener('activate', (event) => {
  const allowed = [STATIC_CACHE, RUNTIME_CACHE, API_CACHE];
  event.waitUntil(
    caches
      .keys()
      .then((keys) =>
        Promise.all(
          keys.filter((key) => !allowed.includes(key)).map((key) => caches.delete(key))
        )
      )
      .then(() => self.clients.claim())
  );
});

// Стратегия "сначала сеть, потом кэш" для GET-запросов к API.
async function networkFirst(request, cacheName) {
  const cache = await caches.open(cacheName);
  try {
    const response = await fetch(request);
    if (response && response.status === 200) {
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    const cached = await cache.match(request);
    if (cached) return cached;
    throw error;
  }
}

// Стратегия "сначала кэш, потом сеть" для статики.
async function cacheFirst(request, cacheName) {
  const cache = await caches.open(cacheName);
  const cached = await cache.match(request);
  if (cached) return cached;
  const response = await fetch(request);
  if (response && response.status === 200) {
    cache.put(request, response.clone());
  }
  return response;
}

self.addEventListener('fetch', (event) => {
  const { request } = event;

  // Кэшируем только GET-запросы.
  if (request.method !== 'GET') return;

  const url = new URL(request.url);

  // Запросы к API: network-first с офлайн-фолбэком из кэша.
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirst(request, API_CACHE));
    return;
  }

  // Навигационные запросы (SPA): отдаём index.html из кэша при офлайне.
  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request).catch(() =>
        caches.match('/index.html').then((res) => res || caches.match('/'))
      )
    );
    return;
  }

  // Остальная статика: cache-first.
  if (url.origin === self.location.origin) {
    event.respondWith(cacheFirst(request, RUNTIME_CACHE));
  }
});
