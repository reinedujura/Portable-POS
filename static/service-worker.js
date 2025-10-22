// Service Worker for Portable POS PWA
// Provides offline capability and caching

const CACHE_NAME = 'portable-pos-v1.0.0';
const STATIC_CACHE = 'portable-pos-static-v1';
const DYNAMIC_CACHE = 'portable-pos-dynamic-v1';

// Assets to cache on install
const STATIC_ASSETS = [
  '/',
  '/static/manifest.json',
  '/static/icons/icon-192x192.png',
  '/static/icons/icon-512x512.png'
];

// Install event - cache static assets
self.addEventListener('install', event => {
  console.log('[ServiceWorker] Installing...');
  
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then(cache => {
        console.log('[ServiceWorker] Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => self.skipWaiting())
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  console.log('[ServiceWorker] Activating...');
  
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cache => {
          if (cache !== STATIC_CACHE && cache !== DYNAMIC_CACHE) {
            console.log('[ServiceWorker] Deleting old cache:', cache);
            return caches.delete(cache);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', event => {
  const { request } = event;
  
  // Skip cross-origin requests
  if (!request.url.startsWith(self.location.origin)) {
    return;
  }
  
  event.respondWith(
    caches.match(request)
      .then(cachedResponse => {
        // Return cached version if available
        if (cachedResponse) {
          console.log('[ServiceWorker] Serving from cache:', request.url);
          return cachedResponse;
        }
        
        // Otherwise fetch from network
        return fetch(request)
          .then(networkResponse => {
            // Cache dynamic content
            if (request.method === 'GET') {
              return caches.open(DYNAMIC_CACHE)
                .then(cache => {
                  cache.put(request, networkResponse.clone());
                  return networkResponse;
                });
            }
            return networkResponse;
          })
          .catch(error => {
            console.log('[ServiceWorker] Fetch failed:', error);
            
            // Return offline page for navigation requests
            if (request.mode === 'navigate') {
              return caches.match('/offline.html');
            }
          });
      })
  );
});

// Background sync for offline transactions
self.addEventListener('sync', event => {
  console.log('[ServiceWorker] Background sync triggered');
  
  if (event.tag === 'sync-transactions') {
    event.waitUntil(syncTransactions());
  }
});

async function syncTransactions() {
  // Placeholder for syncing offline transactions
  console.log('[ServiceWorker] Syncing offline transactions...');
  // Implementation would go here
}

// Push notifications (optional for future)
self.addEventListener('push', event => {
  const data = event.data ? event.data.json() : {};
  const title = data.title || 'Portable POS';
  const options = {
    body: data.body || 'You have a new notification',
    icon: '/static/icons/icon-192x192.png',
    badge: '/static/icons/badge-72x72.png',
    vibrate: [200, 100, 200],
    data: data.url || '/'
  };
  
  event.waitUntil(
    self.registration.showNotification(title, options)
  );
});

// Notification click handler
self.addEventListener('notificationclick', event => {
  event.notification.close();
  event.waitUntil(
    clients.openWindow(event.notification.data)
  );
});

console.log('[ServiceWorker] Loaded successfully');
