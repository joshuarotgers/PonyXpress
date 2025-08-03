/**
 * PonyXpress Main JavaScript
 * Common functionality and utilities for the application
 */

// Global variables
let currentUser = null;
let isOnline = true;

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupServiceWorker();
    setupOfflineDetection();
});

/**
 * Initialize the application
 */
function initializeApp() {
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    });
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

/**
 * Setup service worker for PWA functionality
 */
function setupServiceWorker() {
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', function() {
            navigator.serviceWorker.register('/sw.js')
                .then(function(registration) {
                    console.log('ServiceWorker registration successful with scope: ', registration.scope);
                })
                .catch(function(error) {
                    console.log('ServiceWorker registration failed: ', error);
                });
        });
    }
}

/**
 * Setup offline detection
 */
function setupOfflineDetection() {
    window.addEventListener('online', function() {
        isOnline = true;
        showOnlineStatus();
    });
    
    window.addEventListener('offline', function() {
        isOnline = false;
        showOfflineStatus();
    });
}

/**
 * Show online status notification
 */
function showOnlineStatus() {
    showNotification('success', 'Connection restored', 'You are back online');
}

/**
 * Show offline status notification
 */
function showOfflineStatus() {
    showNotification('warning', 'Connection lost', 'You are currently offline. Some features may be limited.');
}

/**
 * Show notification
 */
function showNotification(type, title, message) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        <strong>${title}</strong><br>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

/**
 * Format date for display
 */
function formatDate(date) {
    if (typeof date === 'string') {
        date = new Date(date);
    }
    return date.toLocaleDateString();
}

/**
 * Format time for display
 */
function formatTime(date) {
    if (typeof date === 'string') {
        date = new Date(date);
    }
    return date.toLocaleTimeString();
}

/**
 * Format datetime for display
 */
function formatDateTime(date) {
    if (typeof date === 'string') {
        date = new Date(date);
    }
    return date.toLocaleString();
}

/**
 * Get current GPS location
 */
function getCurrentLocation() {
    return new Promise((resolve, reject) => {
        if (!navigator.geolocation) {
            reject(new Error('Geolocation is not supported'));
            return;
        }
        
        navigator.geolocation.getCurrentPosition(
            function(position) {
                resolve({
                    lat: position.coords.latitude,
                    lng: position.coords.longitude,
                    accuracy: position.coords.accuracy
                });
            },
            function(error) {
                reject(error);
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 60000
            }
        );
    });
}

/**
 * Calculate distance between two GPS points
 */
function calculateDistance(lat1, lng1, lat2, lng2) {
    const R = 6371000; // Earth's radius in meters
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLng = (lng2 - lng1) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLng/2) * Math.sin(dLng/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
}

/**
 * Format distance for display
 */
function formatDistance(meters) {
    if (meters < 1000) {
        return `${Math.round(meters)}m`;
    } else {
        return `${(meters/1000).toFixed(1)}km`;
    }
}

/**
 * Make API request with error handling
 */
async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

/**
 * Show loading spinner
 */
function showLoading(element) {
    element.innerHTML = '<div class="loading"></div>';
    element.disabled = true;
}

/**
 * Hide loading spinner
 */
function hideLoading(element, originalText) {
    element.innerHTML = originalText;
    element.disabled = false;
}

/**
 * Validate email format
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Validate GPS coordinates
 */
function isValidGPS(lat, lng) {
    return lat >= -90 && lat <= 90 && lng >= -180 && lng <= 180;
}

/**
 * Debounce function for performance
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Throttle function for performance
 */
function throttle(func, limit) {
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
}

/**
 * Local storage utilities
 */
const Storage = {
    set: function(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (error) {
            console.error('Error saving to localStorage:', error);
        }
    },
    
    get: function(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.error('Error reading from localStorage:', error);
            return defaultValue;
        }
    },
    
    remove: function(key) {
        try {
            localStorage.removeItem(key);
        } catch (error) {
            console.error('Error removing from localStorage:', error);
        }
    },
    
    clear: function() {
        try {
            localStorage.clear();
        } catch (error) {
            console.error('Error clearing localStorage:', error);
        }
    }
};

/**
 * Export utilities
 */
const Export = {
    downloadCSV: function(data, filename) {
        const csvContent = this.convertToCSV(data);
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', filename);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    },
    
    convertToCSV: function(data) {
        if (!data || data.length === 0) return '';
        
        const headers = Object.keys(data[0]);
        const csvRows = [headers.join(',')];
        
        for (const row of data) {
            const values = headers.map(header => {
                const value = row[header];
                return typeof value === 'string' ? `"${value.replace(/"/g, '""')}"` : value;
            });
            csvRows.push(values.join(','));
        }
        
        return csvRows.join('\n');
    }
};

// Export utilities to global scope
window.PonyXpress = {
    Storage,
    Export,
    formatDate,
    formatTime,
    formatDateTime,
    getCurrentLocation,
    calculateDistance,
    formatDistance,
    apiRequest,
    showLoading,
    hideLoading,
    isValidEmail,
    isValidGPS,
    debounce,
    throttle
};