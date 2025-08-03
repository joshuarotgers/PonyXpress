/**
 * PonyXpress Service Worker
 * Provides offline functionality and caching for the PWA
 */

const CACHE_NAME = 'ponyxpress-v1.0.0';
const OFFLINE_URL = '/offline';

// Files to cache for offline functionality
const CACHE_URLS = [
    '/',
    '/login',
    '/dashboard',
    '/map',
    '/scan',
    '/manifest.json',
    '/static/css/style.css',
    '/static/js/app.js',
    '/static/icons/icon-192x192.png',
    '/static/icons/icon-512x512.png',
    // Bootstrap CSS
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css',
    // Bootstrap Icons
    'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css',
    // Bootstrap JS
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js',
    // Leaflet CSS & JS
    'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',
    'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'
];

// API endpoints that should be cached
const API_CACHE_URLS = [
    '/api/get-routes',
    '/api/get-mailbox-stops'
];

// Install event - cache resources
self.addEventListener('install', event => {
    console.log('Service Worker: Installing...');
    
    event.waitUntil(
        Promise.all([
            // Cache static resources
            caches.open(CACHE_NAME).then(cache => {
                console.log('Service Worker: Caching static files');
                return cache.addAll(CACHE_URLS);
            }),
            // Skip waiting to activate immediately
            self.skipWaiting()
        ])
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
    console.log('Service Worker: Activating...');
    
    event.waitUntil(
        Promise.all([
            // Clean up old caches
            caches.keys().then(cacheNames => {
                return Promise.all(
                    cacheNames.map(cacheName => {
                        if (cacheName !== CACHE_NAME) {
                            console.log('Service Worker: Deleting old cache:', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            }),
            // Take control of all clients
            self.clients.claim()
        ])
    );
});

// Fetch event - serve cached content when offline
self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);
    
    // Handle different types of requests
    if (request.method === 'GET') {
        if (isNavigationRequest(request)) {
            // Handle page navigation
            event.respondWith(handleNavigationRequest(request));
        } else if (isAPIRequest(url)) {
            // Handle API requests
            event.respondWith(handleAPIRequest(request));
        } else if (isStaticAsset(url)) {
            // Handle static assets
            event.respondWith(handleStaticAsset(request));
        }
    } else if (request.method === 'POST' && isAPIRequest(url)) {
        // Handle POST requests for offline storage
        event.respondWith(handleOfflinePost(request));
    }
});

// Background sync for offline data
self.addEventListener('sync', event => {
    console.log('Service Worker: Background sync triggered');
    
    if (event.tag === 'background-sync') {
        event.waitUntil(syncOfflineData());
    }
});

// Push notification handling
self.addEventListener('push', event => {
    console.log('Service Worker: Push notification received');
    
    if (event.data) {
        const data = event.data.json();
        const options = {
            body: data.body || 'New notification from PonyXpress',
            icon: '/static/icons/icon-192x192.png',
            badge: '/static/icons/icon-192x192.png',
            tag: data.tag || 'ponyxpress-notification',
            requireInteraction: true,
            actions: [
                {
                    action: 'view',
                    title: 'View',
                    icon: '/static/icons/icon-192x192.png'
                },
                {
                    action: 'dismiss',
                    title: 'Dismiss'
                }
            ]
        };
        
        event.waitUntil(
            self.registration.showNotification(data.title || 'PonyXpress', options)
        );
    }
});

// Notification click handling
self.addEventListener('notificationclick', event => {
    console.log('Service Worker: Notification clicked');
    
    event.notification.close();
    
    if (event.action === 'view') {
        event.waitUntil(
            clients.openWindow('/dashboard')
        );
    }
});

/**
 * Helper Functions
 */

function isNavigationRequest(request) {
    return request.mode === 'navigate';
}

function isAPIRequest(url) {
    return url.pathname.startsWith('/api/');
}

function isStaticAsset(url) {
    return url.pathname.startsWith('/static/') || 
           CACHE_URLS.includes(url.pathname);
}

async function handleNavigationRequest(request) {
    try {
        // Try network first
        const networkResponse = await fetch(request);
        
        // Cache successful responses
        if (networkResponse.ok) {
            const cache = await caches.open(CACHE_NAME);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
    } catch (error) {
        console.log('Service Worker: Network failed, serving cached page');
        
        // Try to serve from cache
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Fallback to offline page
        const cache = await caches.open(CACHE_NAME);
        return cache.match('/') || new Response('Offline', { status: 503 });
    }
}

async function handleAPIRequest(request) {
    const url = new URL(request.url);
    
    try {
        // Try network first
        const networkResponse = await fetch(request);
        
        // Cache GET requests that are in our cache list
        if (request.method === 'GET' && API_CACHE_URLS.includes(url.pathname)) {
            const cache = await caches.open(CACHE_NAME);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
    } catch (error) {
        console.log('Service Worker: API request failed, checking cache');
        
        // For GET requests, try to serve from cache
        if (request.method === 'GET') {
            const cachedResponse = await caches.match(request);
            if (cachedResponse) {
                return cachedResponse;
            }
        }
        
        // Return offline response
        return new Response(
            JSON.stringify({ 
                error: 'Offline', 
                offline: true,
                message: 'This request failed because you are offline'
            }), 
            { 
                status: 503,
                headers: { 'Content-Type': 'application/json' }
            }
        );
    }
}

async function handleStaticAsset(request) {
    // Cache first strategy for static assets
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
        return cachedResponse;
    }
    
    try {
        const networkResponse = await fetch(request);
        
        // Cache the response
        if (networkResponse.ok) {
            const cache = await caches.open(CACHE_NAME);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
    } catch (error) {
        console.log('Service Worker: Failed to load static asset:', request.url);
        
        // Return a placeholder or error response
        return new Response('Asset not available offline', { status: 503 });
    }
}

async function handleOfflinePost(request) {
    try {
        // Try network first
        return await fetch(request);
    } catch (error) {
        console.log('Service Worker: POST request failed, storing for background sync');
        
        // Store the request for background sync
        const requestData = {
            url: request.url,
            method: request.method,
            headers: Object.fromEntries(request.headers.entries()),
            body: await request.text(),
            timestamp: Date.now()
        };
        
        // Store in IndexedDB for later sync
        await storeOfflineRequest(requestData);
        
        // Register for background sync
        if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
            try {
                await self.registration.sync.register('background-sync');
            } catch (syncError) {
                console.log('Background sync registration failed:', syncError);
            }
        }
        
        return new Response(
            JSON.stringify({ 
                success: true, 
                offline: true,
                message: 'Request stored for sync when online'
            }), 
            { 
                status: 202,
                headers: { 'Content-Type': 'application/json' }
            }
        );
    }
}

async function storeOfflineRequest(requestData) {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('PonyXpress', 1);
        
        request.onerror = () => reject(request.error);
        
        request.onsuccess = () => {
            const db = request.result;
            const transaction = db.transaction(['offline_requests'], 'readwrite');
            const store = transaction.objectStore('offline_requests');
            
            const addRequest = store.add(requestData);
            addRequest.onsuccess = () => resolve();
            addRequest.onerror = () => reject(addRequest.error);
        };
        
        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            if (!db.objectStoreNames.contains('offline_requests')) {
                const store = db.createObjectStore('offline_requests', { keyPath: 'id', autoIncrement: true });
                store.createIndex('timestamp', 'timestamp', { unique: false });
            }
        };
    });
}

async function syncOfflineData() {
    console.log('Service Worker: Syncing offline data...');
    
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('PonyXpress', 1);
        
        request.onsuccess = () => {
            const db = request.result;
            const transaction = db.transaction(['offline_requests'], 'readwrite');
            const store = transaction.objectStore('offline_requests');
            
            store.getAll().onsuccess = async (event) => {
                const requests = event.target.result;
                
                for (const requestData of requests) {
                    try {
                        const response = await fetch(requestData.url, {
                            method: requestData.method,
                            headers: requestData.headers,
                            body: requestData.body
                        });
                        
                        if (response.ok) {
                            // Remove successfully synced request
                            store.delete(requestData.id);
                            console.log('Service Worker: Synced offline request:', requestData.url);
                        }
                    } catch (error) {
                        console.log('Service Worker: Failed to sync request:', error);
                    }
                }
                
                resolve();
            };
        };
        
        request.onerror = () => reject(request.error);
    });
}

// Periodic background sync (if supported)
self.addEventListener('periodicsync', event => {
    if (event.tag === 'periodic-background-sync') {
        event.waitUntil(syncOfflineData());
    }
});

// Message handling from main thread
self.addEventListener('message', event => {
    console.log('Service Worker: Message received:', event.data);
    
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    
    if (event.data && event.data.type === 'CACHE_URLS') {
        event.waitUntil(
            caches.open(CACHE_NAME).then(cache => {
                return cache.addAll(event.data.urls);
            })
        );
    }
});

console.log('Service Worker: Loaded successfully');