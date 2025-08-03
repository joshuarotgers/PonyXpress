/**
 * PonyXpress Main JavaScript Application
 * Handles global functionality, utilities, and app initialization
 */

// Global App Object
window.PonyXpress = {
    version: '1.0.0',
    debug: true,
    config: {
        mapDefaultZoom: 10,
        scanTimeout: 30000,
        offlineStorageKey: 'ponyxpress_offline_data',
        maxPhotoSize: 5 * 1024 * 1024, // 5MB
        notificationTimeout: 5000
    },
    user: null,
    isOnline: navigator.onLine,
    notifications: [],
    cache: new Map()
};

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    PonyXpress.init();
});

/**
 * Main App Initialization
 */
PonyXpress.init = function() {
    console.log('PonyXpress v' + this.version + ' initializing...');
    
    // Initialize core modules
    this.initNetworkMonitoring();
    this.initNotifications();
    this.initServiceWorker();
    this.initOfflineStorage();
    this.initErrorHandling();
    this.initFormValidation();
    this.initTooltips();
    this.initAnimations();
    this.initAccessibility();
    
    // Load user data if available
    this.loadUserData();
    
    console.log('PonyXpress initialization complete');
};

/**
 * Network Monitoring
 */
PonyXpress.initNetworkMonitoring = function() {
    const updateOnlineStatus = () => {
        this.isOnline = navigator.onLine;
        this.showNotification(
            this.isOnline ? 'Connection restored' : 'Working offline',
            this.isOnline ? 'success' : 'warning',
            3000
        );
        
        // Update UI elements
        const statusElements = document.querySelectorAll('[data-online-status]');
        statusElements.forEach(el => {
            el.textContent = this.isOnline ? 'Online' : 'Offline';
            el.className = this.isOnline ? 'text-success' : 'text-warning';
        });
        
        // Sync offline data when coming back online
        if (this.isOnline) {
            this.syncOfflineData();
        }
    };
    
    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);
    
    // Initial status
    updateOnlineStatus();
};

/**
 * Notification System
 */
PonyXpress.initNotifications = function() {
    // Request notification permission
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }
    
    // Create notification container if it doesn't exist
    if (!document.getElementById('notifications-container')) {
        const container = document.createElement('div');
        container.id = 'notifications-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            max-width: 350px;
        `;
        document.body.appendChild(container);
    }
};

PonyXpress.showNotification = function(message, type = 'info', duration = 5000) {
    const container = document.getElementById('notifications-container');
    if (!container) return;
    
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show notification-toast`;
    notification.style.cssText = `
        margin-bottom: 10px;
        animation: slideInRight 0.3s ease-out;
    `;
    
    notification.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="bi bi-${this.getNotificationIcon(type)} me-2"></i>
            <span>${message}</span>
            <button type="button" class="btn-close" aria-label="Close"></button>
        </div>
    `;
    
    container.appendChild(notification);
    
    // Auto dismiss
    if (duration > 0) {
        setTimeout(() => {
            this.removeNotification(notification);
        }, duration);
    }
    
    // Manual dismiss
    notification.querySelector('.btn-close').addEventListener('click', () => {
        this.removeNotification(notification);
    });
    
    // Browser notification if permitted
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification('PonyXpress', {
            body: message,
            icon: '/static/icons/icon-192x192.png',
            tag: 'ponyxpress-notification'
        });
    }
    
    this.notifications.push(notification);
};

PonyXpress.removeNotification = function(notification) {
    if (notification && notification.parentNode) {
        notification.style.animation = 'slideOutRight 0.3s ease-out';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
        
        const index = this.notifications.indexOf(notification);
        if (index > -1) {
            this.notifications.splice(index, 1);
        }
    }
};

PonyXpress.getNotificationIcon = function(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-triangle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
};

/**
 * Service Worker Registration
 */
PonyXpress.initServiceWorker = function() {
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('Service Worker registered:', registration);
                
                // Check for updates
                registration.addEventListener('updatefound', () => {
                    const newWorker = registration.installing;
                    newWorker.addEventListener('statechange', () => {
                        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                            this.showNotification(
                                'App update available. Refresh to update.',
                                'info',
                                0
                            );
                        }
                    });
                });
            })
            .catch(error => {
                console.error('Service Worker registration failed:', error);
            });
    }
};

/**
 * Offline Storage Management
 */
PonyXpress.initOfflineStorage = function() {
    // Initialize IndexedDB for offline storage
    if ('indexedDB' in window) {
        const request = indexedDB.open('PonyXpress', 1);
        
        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            
            // Create object stores
            if (!db.objectStoreNames.contains('deliveries')) {
                const deliveriesStore = db.createObjectStore('deliveries', { keyPath: 'id', autoIncrement: true });
                deliveriesStore.createIndex('timestamp', 'timestamp', { unique: false });
                deliveriesStore.createIndex('synced', 'synced', { unique: false });
            }
            
            if (!db.objectStoreNames.contains('routes')) {
                const routesStore = db.createObjectStore('routes', { keyPath: 'id', autoIncrement: true });
                routesStore.createIndex('timestamp', 'timestamp', { unique: false });
            }
        };
        
        request.onsuccess = (event) => {
            this.db = event.target.result;
            console.log('IndexedDB initialized');
        };
        
        request.onerror = (event) => {
            console.error('IndexedDB error:', event.target.error);
        };
    }
};

PonyXpress.saveOfflineData = function(store, data) {
    if (!this.db) return Promise.reject('Database not available');
    
    return new Promise((resolve, reject) => {
        const transaction = this.db.transaction([store], 'readwrite');
        const objectStore = transaction.objectStore(store);
        
        data.timestamp = Date.now();
        data.synced = false;
        
        const request = objectStore.add(data);
        
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
};

PonyXpress.syncOfflineData = function() {
    if (!this.db || !this.isOnline) return;
    
    const transaction = this.db.transaction(['deliveries'], 'readonly');
    const store = transaction.objectStore('deliveries');
    const index = store.index('synced');
    const request = index.getAll(false);
    
    request.onsuccess = () => {
        const unsyncedData = request.result;
        unsyncedData.forEach(data => {
            this.syncDataItem(data);
        });
    };
};

PonyXpress.syncDataItem = function(data) {
    fetch('/api/sync-offline-data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            this.markDataAsSynced(data.id);
        }
    })
    .catch(error => {
        console.error('Sync error:', error);
    });
};

/**
 * Error Handling
 */
PonyXpress.initErrorHandling = function() {
    window.addEventListener('error', (event) => {
        console.error('Global error:', event.error);
        this.logError(event.error);
    });
    
    window.addEventListener('unhandledrejection', (event) => {
        console.error('Unhandled promise rejection:', event.reason);
        this.logError(event.reason);
    });
};

PonyXpress.logError = function(error) {
    const errorData = {
        message: error.message || 'Unknown error',
        stack: error.stack || '',
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        url: window.location.href
    };
    
    // Store error locally
    const errors = JSON.parse(localStorage.getItem('ponyxpress_errors') || '[]');
    errors.push(errorData);
    
    // Keep only last 10 errors
    if (errors.length > 10) {
        errors.splice(0, errors.length - 10);
    }
    
    localStorage.setItem('ponyxpress_errors', JSON.stringify(errors));
    
    // Send to server if online
    if (this.isOnline) {
        fetch('/api/log-error', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(errorData)
        }).catch(() => {
            // Silently fail
        });
    }
};

/**
 * Form Validation
 */
PonyXpress.initFormValidation = function() {
    // Add real-time validation to forms
    const forms = document.querySelectorAll('form[novalidate]');
    forms.forEach(form => {
        form.addEventListener('submit', (event) => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // Focus first invalid field
                const firstInvalid = form.querySelector(':invalid');
                if (firstInvalid) {
                    firstInvalid.focus();
                }
            }
            form.classList.add('was-validated');
        });
        
        // Real-time validation on input
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', () => {
                if (input.checkValidity()) {
                    input.classList.remove('is-invalid');
                    input.classList.add('is-valid');
                } else {
                    input.classList.remove('is-valid');
                    input.classList.add('is-invalid');
                }
            });
        });
    });
};

/**
 * Tooltips Initialization
 */
PonyXpress.initTooltips = function() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Custom tooltips
    const customTooltips = document.querySelectorAll('[data-tooltip]');
    customTooltips.forEach(el => {
        el.classList.add('tooltip-custom');
    });
};

/**
 * Animations
 */
PonyXpress.initAnimations = function() {
    // Add fade-in animation to new elements
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    });
    
    // Observe elements with animation class
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    animatedElements.forEach(el => observer.observe(el));
};

/**
 * Accessibility Enhancements
 */
PonyXpress.initAccessibility = function() {
    // Skip link for keyboard navigation
    if (!document.getElementById('skip-link')) {
        const skipLink = document.createElement('a');
        skipLink.id = 'skip-link';
        skipLink.href = '#main-content';
        skipLink.textContent = 'Skip to main content';
        skipLink.className = 'sr-only sr-only-focusable';
        skipLink.style.cssText = `
            position: absolute;
            top: -40px;
            left: 6px;
            background: #007bff;
            color: white;
            padding: 8px;
            text-decoration: none;
            border-radius: 4px;
            z-index: 10000;
        `;
        
        skipLink.addEventListener('focus', () => {
            skipLink.style.top = '6px';
        });
        
        skipLink.addEventListener('blur', () => {
            skipLink.style.top = '-40px';
        });
        
        document.body.insertBefore(skipLink, document.body.firstChild);
    }
    
    // Keyboard navigation for dropdown menus
    const dropdowns = document.querySelectorAll('.dropdown-menu');
    dropdowns.forEach(dropdown => {
        dropdown.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const toggle = dropdown.previousElementSibling;
                if (toggle) {
                    toggle.click();
                    toggle.focus();
                }
            }
        });
    });
};

/**
 * User Data Management
 */
PonyXpress.loadUserData = function() {
    // Load user data from meta tags or API
    const userMeta = document.querySelector('meta[name="user-data"]');
    if (userMeta) {
        try {
            this.user = JSON.parse(userMeta.content);
        } catch (e) {
            console.error('Error parsing user data:', e);
        }
    }
};

/**
 * Utility Functions
 */
PonyXpress.utils = {
    // Format dates
    formatDate: function(date, format = 'short') {
        const d = new Date(date);
        const options = {
            short: { year: 'numeric', month: 'short', day: 'numeric' },
            long: { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' },
            time: { hour: '2-digit', minute: '2-digit' }
        };
        return d.toLocaleDateString('en-US', options[format] || options.short);
    },
    
    // Format file sizes
    formatFileSize: function(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    
    // Debounce function
    debounce: function(func, wait, immediate) {
        let timeout;
        return function executedFunction() {
            const context = this;
            const args = arguments;
            const later = function() {
                timeout = null;
                if (!immediate) func.apply(context, args);
            };
            const callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func.apply(context, args);
        };
    },
    
    // Throttle function
    throttle: function(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },
    
    // Generate unique ID
    generateId: function() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    },
    
    // Validate email
    isValidEmail: function(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },
    
    // Get current location
    getCurrentLocation: function() {
        return new Promise((resolve, reject) => {
            if (!navigator.geolocation) {
                reject(new Error('Geolocation is not supported'));
                return;
            }
            
            navigator.geolocation.getCurrentPosition(
                position => resolve({
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude,
                    accuracy: position.coords.accuracy
                }),
                error => reject(error),
                {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 300000
                }
            );
        });
    },
    
    // Compress image
    compressImage: function(file, maxWidth = 800, quality = 0.8) {
        return new Promise((resolve) => {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            const img = new Image();
            
            img.onload = function() {
                const ratio = Math.min(maxWidth / img.width, maxWidth / img.height);
                canvas.width = img.width * ratio;
                canvas.height = img.height * ratio;
                
                ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                
                canvas.toBlob(resolve, 'image/jpeg', quality);
            };
            
            img.src = URL.createObjectURL(file);
        });
    }
};

/**
 * API Helper Functions
 */
PonyXpress.api = {
    baseUrl: '',
    
    // Generic fetch wrapper
    request: function(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        };
        
        const mergedOptions = { ...defaultOptions, ...options };
        
        return fetch(this.baseUrl + url, mergedOptions)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .catch(error => {
                console.error('API request failed:', error);
                throw error;
            });
    },
    
    // GET request
    get: function(url) {
        return this.request(url, { method: 'GET' });
    },
    
    // POST request
    post: function(url, data) {
        return this.request(url, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    
    // PUT request
    put: function(url, data) {
        return this.request(url, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },
    
    // DELETE request
    delete: function(url) {
        return this.request(url, { method: 'DELETE' });
    }
};

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    .sr-only-focusable:focus {
        position: static !important;
        width: auto !important;
        height: auto !important;
        padding: inherit !important;
        margin: inherit !important;
        overflow: visible !important;
        clip: auto !important;
        white-space: normal !important;
    }
    
    .notification-toast {
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        border: none;
    }
`;
document.head.appendChild(style);

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PonyXpress;
}

// Global error handler for unhandled promises
window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
    event.preventDefault();
});

console.log('PonyXpress app.js loaded successfully');