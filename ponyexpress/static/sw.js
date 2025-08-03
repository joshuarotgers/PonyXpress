/**
 * PonyXpress Service Worker
 * Provides offline support and caching for the application
 */

const CACHE_NAME = 'ponyxpress-v1.0.0';
const STATIC_CACHE = 'ponyxpress-static-v1.0.0';
const DYNAMIC_CACHE = 'ponyxpress-dynamic-v1.0.0';

// Files to cache for offline functionality
const STATIC_FILES = [
    '/',
    '/static/css/style.css',
    '/static/js/app.js',
    '/static/manifest.json',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
    'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',
    'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'
];

// Install event - cache static files
self.addEventListener('install', event => {
    console.log('Service Worker installing...');
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then(cache => {
                console.log('Caching static files');
                return cache.addAll(STATIC_FILES);
            })
            .then(() => {
                console.log('Static files cached successfully');
                return self.skipWaiting();
            })
            .catch(error => {
                console.error('Error caching static files:', error);
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
    console.log('Service Worker activating...');
    event.waitUntil(
        caches.keys()
            .then(cacheNames => {
                return Promise.all(
                    cacheNames.map(cacheName => {
                        if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
                            console.log('Deleting old cache:', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            })
            .then(() => {
                console.log('Service Worker activated');
                return self.clients.claim();
            })
    );
});

// Fetch event - serve from cache when offline
self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);

    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }

    // Handle API requests
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(handleApiRequest(request));
        return;
    }

    // Handle static files
    if (url.pathname.startsWith('/static/') || 
        url.pathname.startsWith('/manifest.json') ||
        url.pathname.startsWith('/sw.js')) {
        event.respondWith(handleStaticRequest(request));
        return;
    }

    // Handle HTML pages
    if (request.headers.get('accept').includes('text/html')) {
        event.respondWith(handlePageRequest(request));
        return;
    }

    // Handle other requests
    event.respondWith(handleOtherRequest(request));
});

/**
 * Handle API requests with offline fallback
 */
async function handleApiRequest(request) {
    try {
        // Try network first
        const response = await fetch(request);
        
        // Cache successful responses
        if (response.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, response.clone());
        }
        
        return response;
    } catch (error) {
        console.log('API request failed, trying cache:', request.url);
        
        // Try cache as fallback
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Return offline response for specific endpoints
        if (request.url.includes('/api/packages/today')) {
            return new Response(JSON.stringify({ count: 0 }), {
                headers: { 'Content-Type': 'application/json' }
            });
        }
        
        if (request.url.includes('/api/mailbox-stops/count')) {
            return new Response(JSON.stringify({ count: 0 }), {
                headers: { 'Content-Type': 'application/json' }
            });
        }
        
        // Return error response
        return new Response(JSON.stringify({ error: 'Offline - No cached data available' }), {
            status: 503,
            headers: { 'Content-Type': 'application/json' }
        });
    }
}

/**
 * Handle static file requests
 */
async function handleStaticRequest(request) {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
        return cachedResponse;
    }
    
    try {
        const response = await fetch(request);
        if (response.ok) {
            const cache = await caches.open(STATIC_CACHE);
            cache.put(request, response.clone());
        }
        return response;
    } catch (error) {
        // Return offline page for missing static files
        return new Response('Offline - Static file not available', {
            status: 503,
            headers: { 'Content-Type': 'text/plain' }
        });
    }
}

/**
 * Handle page requests
 */
async function handlePageRequest(request) {
    try {
        // Try network first
        const response = await fetch(request);
        
        // Cache successful responses
        if (response.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, response.clone());
        }
        
        return response;
    } catch (error) {
        console.log('Page request failed, trying cache:', request.url);
        
        // Try cache as fallback
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Return offline page
        return caches.match('/offline.html');
    }
}

/**
 * Handle other requests
 */
async function handleOtherRequest(request) {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
        return cachedResponse;
    }
    
    try {
        const response = await fetch(request);
        if (response.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, response.clone());
        }
        return response;
    } catch (error) {
        return new Response('Offline - Resource not available', {
            status: 503,
            headers: { 'Content-Type': 'text/plain' }
        });
    }
}

/**
 * Background sync for offline actions
 */
self.addEventListener('sync', event => {
    console.log('Background sync triggered:', event.tag);
    
    if (event.tag === 'background-sync') {
        event.waitUntil(doBackgroundSync());
    }
});

/**
 * Perform background sync
 */
async function doBackgroundSync() {
    try {
        // Get pending actions from IndexedDB
        const pendingActions = await getPendingActions();
        
        for (const action of pendingActions) {
            try {
                await performAction(action);
                await removePendingAction(action.id);
            } catch (error) {
                console.error('Failed to sync action:', action, error);
            }
        }
    } catch (error) {
        console.error('Background sync failed:', error);
    }
}

/**
 * Get pending actions from IndexedDB
 */
async function getPendingActions() {
    // This would typically use IndexedDB
    // For now, return empty array
    return [];
}

/**
 * Perform a pending action
 */
async function performAction(action) {
    const response = await fetch(action.url, {
        method: action.method,
        headers: action.headers,
        body: action.body
    });
    
    if (!response.ok) {
        throw new Error(`Action failed: ${response.status}`);
    }
    
    return response;
}

/**
 * Remove pending action from IndexedDB
 */
async function removePendingAction(id) {
    // This would typically use IndexedDB
    console.log('Removing pending action:', id);
}

/**
 * Push notification handling
 */
self.addEventListener('push', event => {
    console.log('Push notification received:', event);
    
    const options = {
        body: event.data ? event.data.text() : 'New notification from PonyXpress',
        icon: '/static/images/icon-192x192.png',
        badge: '/static/images/badge-72x72.png',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        },
        actions: [
            {
                action: 'explore',
                title: 'View Details',
                icon: '/static/images/checkmark.png'
            },
            {
                action: 'close',
                title: 'Close',
                icon: '/static/images/xmark.png'
            }
        ]
    };
    
    event.waitUntil(
        self.registration.showNotification('PonyXpress', options)
    );
});

/**
 * Notification click handling
 */
self.addEventListener('notificationclick', event => {
    console.log('Notification clicked:', event);
    
    event.notification.close();
    
    if (event.action === 'explore') {
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});

/**
 * Message handling from main thread
 */
self.addEventListener('message', event => {
    console.log('Service Worker received message:', event.data);
    
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    
    if (event.data && event.data.type === 'CACHE_URLS') {
        event.waitUntil(
            caches.open(DYNAMIC_CACHE)
                .then(cache => {
                    return cache.addAll(event.data.urls);
                })
        );
    }
});