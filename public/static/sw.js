// Gramátike Service Worker - Cache Busting Strategy
// Versão incrementada a cada deploy para forçar atualização de cache
const CACHE_VERSION = 'gk-static-v4';
const OLD_CACHES = ['gk-static-v1', 'gk-static-v2', 'gk-static-v3'];

// Recursos que podem ser cacheados (apenas manifest e ícones)
const CACHEABLE_ASSETS = [
  '/static/manifest.webmanifest',
  '/static/favicon.ico',
  '/static/favicon.png',
  '/static/img/icons/icon-192.png',
  '/static/img/icons/icon-512.png',
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
  // Limpa caches antigos usando prefixo específico 'gk-static-'
  e.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name.startsWith('gk-static-') && name !== CACHE_VERSION)
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
          if (cached) return cached;
          // Retorna uma resposta mais informativa quando offline e sem cache
          return new Response(
            '<!DOCTYPE html><html><head><meta charset="utf-8"><title>Offline</title></head><body style="font-family:sans-serif;text-align:center;padding:2rem;"><h1>📶 Você está offline</h1><p>Esta página ainda não está disponível em cache. Por favor, verifique sua conexão e tente novamente.</p></body></html>',
            { status: 503, headers: { 'Content-Type': 'text/html; charset=utf-8' } }
          );
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
          // Retorna resposta vazia para recursos não críticos
          return new Response('', { status: 503 });
        }
      })
    );
  }
});
