// Gramátike Service Worker - Cache Busting Strategy
// Versão incrementada a cada deploy para forçar atualização de cache
const CACHE_VERSION = 'gk-static-v3';
const OLD_CACHES = ['gk-static-v1', 'gk-static-v2'];

// Recursos que podem ser cacheados (apenas manifest e ícones)
const CACHEABLE_ASSETS = [
  '/static/manifest.webmanifest',
  '/static/favicon.ico',
  '/static/favicon.png',
];

// Padrões de URL que devem usar network-first (CSS, JS, templates)
const NETWORK_FIRST_PATTERNS = [
  /\.css(\?.*)?$/,
  /\.js(\?.*)?$/,
  /^\/$/,
  /^\/educacao/,
  /^\/perfil/,
  /^\/suporte/,
  /^\/configuracoes/,
];

self.addEventListener('install', (e) => {
  // Força o novo service worker a assumir imediatamente
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  // Limpa caches antigos
  e.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => OLD_CACHES.includes(name) || (name.startsWith('gk-') && name !== CACHE_VERSION))
          .map((name) => caches.delete(name))
      );
    }).then(() => clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;

  const url = new URL(req.url);
  
  // Verifica se deve usar estratégia network-first
  const useNetworkFirst = NETWORK_FIRST_PATTERNS.some(pattern => pattern.test(url.pathname));
  
  if (useNetworkFirst) {
    // Network-first: tenta buscar da rede, usa cache apenas se offline
    event.respondWith(
      fetch(req)
        .then((response) => {
          if (response && response.status === 200) {
            const responseClone = response.clone();
            caches.open(CACHE_VERSION).then((cache) => {
              cache.put(req, responseClone);
            });
          }
          return response;
        })
        .catch(async () => {
          const cached = await caches.match(req);
          return cached || Response.error();
        })
    );
  } else {
    // Cache-first para recursos estáticos (ícones, manifest)
    event.respondWith(
      caches.open(CACHE_VERSION).then(async (cache) => {
        const cached = await cache.match(req);
        if (cached) return cached;
        try {
          const fresh = await fetch(req);
          if (fresh && fresh.status === 200 && fresh.type === 'basic') {
            cache.put(req, fresh.clone());
          }
          return fresh;
        } catch (err) {
          return cached || Response.error();
        }
      })
    );
  }
});
