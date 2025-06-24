// PONYXPRESS Application JavaScript

class PonyXpressApp {
    constructor() {
        this.currentUser = null;
        this.currentMode = 'role-select';
        this.isVoiceActive = false;
        this.isOfflineMode = true;
        this.routes = [];
        this.packages = [];
        this.deliveries = [];
        this.settings = {
            theme: 'auto',
            voiceEnabled: true,
            offlineMode: true,
            cloudSync: false,
            soundEffects: true
        };

        this.init();
    }

    async init() {
        console.log('Initializing PONYXPRESS app...');
        this.loadSettings();
        this.setupEventListeners();
        this.loadSampleData();
        this.startApp();
        this.registerServiceWorker();
    }

    loadSettings() {
        const savedSettings = localStorage.getItem('ponyxpress-settings');
        if (savedSettings) {
            this.settings = { ...this.settings, ...JSON.parse(savedSettings) };
        }
        this.applyTheme();
    }

    setupEventListeners() {
        // Wait for DOM to be ready
        document.addEventListener('DOMContentLoaded', () => {
            this.bindEvents();
        });
        
        // If DOM is already ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.bindEvents();
            });
        } else {
            this.bindEvents();
        }
    }

    bindEvents() {
        // Menu toggle
        const menuToggle = document.getElementById('menuToggle');
        const menuClose = document.getElementById('menuClose');
        const sideMenu = document.getElementById('sideMenu');

        if (menuToggle) {
            menuToggle.addEventListener('click', () => {
                sideMenu.classList.add('open');
            });
        }

        if (menuClose) {
            menuClose.addEventListener('click', () => {
                sideMenu.classList.remove('open');
            });
        }

        // Mode switching
        document.querySelectorAll('.mode-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const mode = e.target.dataset.mode;
                this.switchMode(mode);
                sideMenu.classList.remove('open');
            });
        });

        // Role selection
        document.querySelectorAll('.role-card').forEach(card => {
            card.addEventListener('click', (e) => {
                const role = e.currentTarget.dataset.role;
                this.selectRole(role);
            });
        });

        // Theme toggle
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                this.toggleTheme();
            });
        }

        // Voice toggle
        const voiceToggle = document.getElementById('voiceToggle');
        if (voiceToggle) {
            voiceToggle.addEventListener('click', () => {
                this.toggleVoiceAssistant();
            });
        }

        // Modal controls
        this.setupModalControls();

        // Functional buttons
        this.setupFunctionalButtons();

        // Voice commands
        this.setupVoiceCommands();

        // Settings
        this.setupSettings();

        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            const menu = document.getElementById('sideMenu');
            const menuToggle = document.getElementById('menuToggle');
            if (menu && menuToggle && !menu.contains(e.target) && !menuToggle.contains(e.target)) {
                menu.classList.remove('open');
            }
        });
    }

    setupModalControls() {
        // Scanner modal
        const scannerBtn = document.getElementById('scannerBtn');
        const closeScannerBtn = document.getElementById('closeScannerBtn');
        const scannerModal = document.getElementById('scannerModal');

        if (scannerBtn && scannerModal) {
            scannerBtn.addEventListener('click', () => {
                scannerModal.classList.remove('hidden');
            });
        }

        if (closeScannerBtn && scannerModal) {
            closeScannerBtn.addEventListener('click', () => {
                scannerModal.classList.add('hidden');
            });
        }

        // Settings modal
        const settingsBtn = document.getElementById('settingsBtn');
        const closeSettingsBtn = document.getElementById('closeSettingsBtn');
        const settingsModal = document.getElementById('settingsModal');

        if (settingsBtn && settingsModal) {
            settingsBtn.addEventListener('click', () => {
                settingsModal.classList.remove('hidden');
            });
        }

        if (closeSettingsBtn && settingsModal) {
            closeSettingsBtn.addEventListener('click', () => {
                settingsModal.classList.add('hidden');
            });
        }

        // Package lookup
        const lookupPackageBtn = document.getElementById('lookupPackageBtn');
        if (lookupPackageBtn) {
            lookupPackageBtn.addEventListener('click', () => {
                this.lookupPackage();
            });
        }
    }

    setupFunctionalButtons() {
        // USPS Carrier Mode buttons
        const startRouteBtn = document.getElementById('startRouteBtn');
        if (startRouteBtn) {
            startRouteBtn.addEventListener('click', () => {
                this.startRoute();
            });
        }

        const scanPackageBtn = document.getElementById('scanPackageBtn');
        if (scanPackageBtn) {
            scanPackageBtn.addEventListener('click', () => {
                const scannerModal = document.getElementById('scannerModal');
                if (scannerModal) {
                    scannerModal.classList.remove('hidden');
                }
            });
        }

        // Delivery Driver Mode buttons
        const buildRouteBtn = document.getElementById('buildRouteBtn');
        if (buildRouteBtn) {
            buildRouteBtn.addEventListener('click', () => {
                this.buildRoute();
            });
        }

        const addStopBtn = document.getElementById('addStopBtn');
        if (addStopBtn) {
            addStopBtn.addEventListener('click', () => {
                this.addRouteStop();
            });
        }

        const capturePhotoBtn = document.getElementById('capturePhotoBtn');
        if (capturePhotoBtn) {
            capturePhotoBtn.addEventListener('click', () => {
                this.capturePhoto();
            });
        }

        const captureSignatureBtn = document.getElementById('captureSignatureBtn');
        if (captureSignatureBtn) {
            captureSignatureBtn.addEventListener('click', () => {
                this.captureSignature();
            });
        }

        const confirmDeliveryBtn = document.getElementById('confirmDeliveryBtn');
        if (confirmDeliveryBtn) {
            confirmDeliveryBtn.addEventListener('click', () => {
                this.confirmDelivery();
            });
        }

        // Navigation buttons
        const startNavBtn = document.getElementById('startNavBtn');
        if (startNavBtn) {
            startNavBtn.addEventListener('click', () => {
                this.startNavigation();
            });
        }

        // Admin buttons
        const assignRouteBtn = document.getElementById('assignRouteBtn');
        if (assignRouteBtn) {
            assignRouteBtn.addEventListener('click', () => {
                this.assignRoute();
            });
        }

        const liveTrackingBtn = document.getElementById('liveTrackingBtn');
        if (liveTrackingBtn) {
            liveTrackingBtn.addEventListener('click', () => {
                this.toggleLiveTracking();
            });
        }

        // Export data
        const exportBtn = document.getElementById('exportBtn');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => {
                this.exportData();
            });
        }
    }

    setupVoiceCommands() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            this.recognition.continuous = true;
            this.recognition.interimResults = true;

            this.recognition.onresult = (event) => {
                const transcript = event.results[event.results.length - 1][0].transcript.toLowerCase();
                if (transcript.includes('hey ai')) {
                    this.activateVoiceAssistant(transcript);
                }
            };

            if (this.settings.voiceEnabled) {
                try {
                    this.recognition.start();
                } catch (error) {
                    console.log('Voice recognition not available');
                }
            }
        }
    }

    setupSettings() {
        // Theme setting
        const themeSelect = document.getElementById('themeSelect');
        if (themeSelect) {
            themeSelect.value = this.settings.theme;
            themeSelect.addEventListener('change', (e) => {
                this.settings.theme = e.target.value;
                this.applyTheme();
                this.saveSettings();
            });
        }

        // Voice setting
        const voiceEnabled = document.getElementById('voiceEnabled');
        if (voiceEnabled) {
            voiceEnabled.checked = this.settings.voiceEnabled;
            voiceEnabled.addEventListener('change', (e) => {
                this.settings.voiceEnabled = e.target.checked;
                this.saveSettings();
                if (this.recognition) {
                    if (e.target.checked) {
                        try {
                            this.recognition.start();
                        } catch (error) {
                            console.log('Voice recognition start failed');
                        }
                    } else {
                        this.recognition.stop();
                    }
                }
            });
        }

        // Offline mode
        const offlineMode = document.getElementById('offlineMode');
        if (offlineMode) {
            offlineMode.checked = this.settings.offlineMode;
            offlineMode.addEventListener('change', (e) => {
                this.settings.offlineMode = e.target.checked;
                this.updateConnectionStatus();
                this.saveSettings();
            });
        }

        // Cloud sync
        const cloudSync = document.getElementById('cloudSync');
        if (cloudSync) {
            cloudSync.checked = this.settings.cloudSync;
            cloudSync.addEventListener('change', (e) => {
                this.settings.cloudSync = e.target.checked;
                this.saveSettings();
            });
        }

        // Sound effects
        const soundEffects = document.getElementById('soundEffects');
        if (soundEffects) {
            soundEffects.checked = this.settings.soundEffects;
            soundEffects.addEventListener('change', (e) => {
                this.settings.soundEffects = e.target.checked;
                this.saveSettings();
            });
        }

        // Test sound button
        const testSoundBtn = document.getElementById('testSoundBtn');
        if (testSoundBtn) {
            testSoundBtn.addEventListener('click', () => {
                this.playStartupSound();
            });
        }
    }

    loadSampleData() {
        // Load sample routes
        this.routes = [
            { id: 1, name: "Downtown Route A", stops: 45, estimatedTime: "6.5 hours", status: "active" },
            { id: 2, name: "Residential Route B", stops: 62, estimatedTime: "7.2 hours", status: "pending" },
            { id: 3, name: "Business District C", stops: 28, estimatedTime: "4.8 hours", status: "completed" }
        ];

        // Load sample packages
        this.packages = [
            { tracking: "9405511206213100012345", type: "Priority Mail", status: "Out for Delivery", recipient: "John Smith" },
            { tracking: "9205511206213100012346", type: "First Class", status: "Delivered", recipient: "Jane Doe" },
            { tracking: "9305511206213100012347", type: "Express", status: "Pending", recipient: "Bob Johnson" }
        ];

        // Update package list after DOM is ready
        setTimeout(() => {
            this.updatePackageList();
        }, 100);
    }

    startApp() {
        console.log('Starting app...');
        
        // Play startup sound after a delay
        setTimeout(() => {
            if (this.settings.soundEffects) {
                this.playStartupSound();
            }
        }, 1000);

        // Hide startup screen and show main app
        setTimeout(() => {
            console.log('Transitioning to main app...');
            const startupScreen = document.getElementById('startupScreen');
            const mainApp = document.getElementById('mainApp');
            
            if (startupScreen) {
                startupScreen.style.display = 'none';
            }
            if (mainApp) {
                mainApp.classList.remove('hidden');
            }
            
            this.updateConnectionStatus();
            this.updateGPSStatus();
            
            console.log('App started successfully');
        }, 2500); // Reduced from 3000 to 2500ms for faster loading
    }

    async registerServiceWorker() {
        if ('serviceWorker' in navigator) {
            try {
                // Create inline service worker
                const swCode = `
                    const CACHE_NAME = 'ponyxpress-v1';
                    self.addEventListener('install', event => {
                        console.log('Service Worker installed');
                    });
                    self.addEventListener('fetch', event => {
                        // Handle fetch events
                    });
                `;
                
                const blob = new Blob([swCode], { type: 'application/javascript' });
                const swUrl = URL.createObjectURL(blob);
                
                const registration = await navigator.serviceWorker.register(swUrl);
                console.log('Service Worker registered:', registration);
            } catch (error) {
                console.log('Service Worker registration failed:', error);
            }
        }
    }

    switchMode(mode) {
        console.log('Switching to mode:', mode);
        this.currentMode = mode;
        
        // Hide all screens
        document.querySelectorAll('.screen').forEach(screen => {
            screen.classList.remove('active');
        });

        // Show selected screen
        const screenMap = {
            'role-select': 'roleSelectScreen',
            'usps-carrier': 'uspsCarrierScreen',
            'delivery-driver': 'deliveryDriverScreen',
            'navigation': 'navigationScreen',
            'admin': 'adminScreen'
        };

        const screenId = screenMap[mode];
        if (screenId) {
            const screen = document.getElementById(screenId);
            if (screen) {
                screen.classList.add('active');
            }
        }

        // Update mode indicator
        const modeNames = {
            'role-select': 'Select Mode',
            'usps-carrier': '📮 USPS Carrier',
            'delivery-driver': '🚚 Delivery Driver',
            'navigation': '🗺️ Navigation',
            'admin': '👑 Admin Dashboard'
        };

        const currentModeElement = document.getElementById('currentMode');
        if (currentModeElement) {
            currentModeElement.textContent = modeNames[mode] || 'Select Mode';
        }

        // Update menu items
        document.querySelectorAll('.mode-btn').forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.mode === mode) {
                btn.classList.add('active');
            }
        });
    }

    selectRole(role) {
        this.currentUser = { role };
        
        // Visual feedback
        document.querySelectorAll('.role-card').forEach(card => {
            card.classList.remove('selected');
        });
        const selectedCard = document.querySelector(`[data-role="${role}"]`);
        if (selectedCard) {
            selectedCard.classList.add('selected');
        }

        // Auto-switch to appropriate mode after selection
        setTimeout(() => {
            const modeMap = {
                'carrier': 'usps-carrier',
                'substitute': 'usps-carrier',
                'supervisor': 'admin',
                'admin': 'admin'
            };
            this.switchMode(modeMap[role] || 'usps-carrier');
        }, 1000);

        this.showNotification(`Welcome, ${role.charAt(0).toUpperCase() + role.slice(1)}!`, 'success');
    }

    toggleTheme() {
        const themes = ['light', 'dark', 'auto'];
        const currentIndex = themes.indexOf(this.settings.theme);
        this.settings.theme = themes[(currentIndex + 1) % themes.length];
        this.applyTheme();
        this.saveSettings();
    }

    applyTheme() {
        const html = document.documentElement;
        const themeToggle = document.getElementById('themeToggle');
        
        if (this.settings.theme === 'auto') {
            html.removeAttribute('data-color-scheme');
            if (themeToggle) themeToggle.textContent = '🌙';
        } else {
            html.setAttribute('data-color-scheme', this.settings.theme);
            if (themeToggle) {
                themeToggle.textContent = this.settings.theme === 'dark' ? '☀️' : '🌙';
            }
        }
    }

    toggleVoiceAssistant() {
        const assistant = document.getElementById('voiceAssistant');
        if (assistant) {
            if (assistant.classList.contains('hidden')) {
                assistant.classList.remove('hidden');
                const voiceStatus = document.getElementById('voiceStatus');
                if (voiceStatus) {
                    voiceStatus.textContent = 'Voice assistant activated. Say "Hey AI" followed by your command.';
                }
            } else {
                assistant.classList.add('hidden');
            }
        }
    }

    activateVoiceAssistant(transcript) {
        const assistant = document.getElementById('voiceAssistant');
        const responseDiv = document.getElementById('voiceResponse');
        
        if (assistant) {
            assistant.classList.remove('hidden');
            assistant.classList.add('active');
        }
        
        // Simulate AI response based on command
        let response = "I'm processing your request...";
        
        if (transcript.includes('scan') || transcript.includes('package')) {
            response = "Opening package scanner. Please position the barcode in view.";
            setTimeout(() => {
                const scannerModal = document.getElementById('scannerModal');
                if (scannerModal) {
                    scannerModal.classList.remove('hidden');
                }
            }, 1000);
        } else if (transcript.includes('route') || transcript.includes('navigation')) {
            response = "Calculating optimal route. GPS is active and ready for navigation.";
        } else if (transcript.includes('delivery') || transcript.includes('delivered')) {
            response = "Marking current stop as delivered. Would you like to capture a photo or signature?";
        } else if (transcript.includes('help')) {
            response = "Available commands: 'scan package', 'start route', 'mark delivered', 'show navigation'. How can I assist you?";
        } else {
            response = "I understand you said: '" + transcript + "'. How can I help with your delivery tasks?";
        }
        
        if (responseDiv) {
            responseDiv.textContent = response;
        }
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            if (assistant) {
                assistant.classList.remove('active');
                setTimeout(() => {
                    assistant.classList.add('hidden');
                }, 500);
            }
        }, 5000);
    }

    lookupPackage() {
        const trackingInput = document.getElementById('manualTrackingInput');
        if (!trackingInput) return;
        
        const trackingNumber = trackingInput.value.trim();
        
        if (!trackingNumber) {
            this.showNotification('Please enter a tracking number', 'error');
            return;
        }

        // Simulate package lookup
        const foundPackage = this.packages.find(pkg => 
            pkg.tracking.includes(trackingNumber) || trackingNumber === pkg.tracking
        );

        if (foundPackage) {
            this.showNotification(`Package found: ${foundPackage.type} for ${foundPackage.recipient}`, 'success');
            // Close scanner modal
            const scannerModal = document.getElementById('scannerModal');
            if (scannerModal) {
                scannerModal.classList.add('hidden');
            }
            // Add to current delivery list
            this.addToDeliveryList(foundPackage);
        } else {
            this.showNotification('Package not found. Please check the tracking number.', 'warning');
        }

        trackingInput.value = '';
    }

    addToDeliveryList(package) {
        // Add package to delivery list with current timestamp
        const delivery = {
            ...package,
            timestamp: new Date().toISOString(),
            location: this.getCurrentLocation()
        };
        this.deliveries.push(delivery);
        this.updatePackageList();
    }

    updatePackageList() {
        const packageList = document.getElementById('packageList');
        if (!packageList) return;

        packageList.innerHTML = '';
        
        this.packages.forEach(pkg => {
            const item = document.createElement('div');
            item.className = 'package-item';
            item.innerHTML = `
                <div class="package-info">
                    <div class="package-type">${pkg.type}</div>
                    <div class="package-tracking">${pkg.tracking}</div>
                    <div class="package-recipient">${pkg.recipient}</div>
                </div>
                <div class="status status--${this.getStatusClass(pkg.status)}">${pkg.status}</div>
            `;
            packageList.appendChild(item);
        });
    }

    getStatusClass(status) {
        const statusMap = {
            'Delivered': 'success',
            'Out for Delivery': 'warning',
            'Pending': 'info',
            'Failed': 'error'
        };
        return statusMap[status] || 'info';
    }

    startRoute() {
        this.showNotification('Route started! GPS tracking is now active.', 'success');
        this.updateGPSStatus('active');
        
        // Simulate route progress
        let completed = 12;
        const total = 45;
        const progressBar = document.querySelector('.progress-fill');
        
        const updateProgress = () => {
            const percentage = (completed / total) * 100;
            if (progressBar) {
                progressBar.style.width = percentage + '%';
            }
            
            // Update stats
            const statValue = document.querySelector('.stat-value');
            if (statValue) {
                statValue.textContent = completed;
            }
            
            if (completed < total) {
                completed++;
                setTimeout(updateProgress, 10000); // Update every 10 seconds for demo
            }
        };
        
        setTimeout(updateProgress, 5000);
    }

    buildRoute() {
        this.showNotification('Route builder activated. Add stops to create your delivery route.', 'info');
    }

    addRouteStop() {
        const addressInput = document.getElementById('stopAddress');
        if (!addressInput) return;
        
        const address = addressInput.value.trim();
        
        if (!address) {
            this.showNotification('Please enter an address', 'error');
            return;
        }

        const routeStops = document.getElementById('routeStops');
        if (!routeStops) return;
        
        const stopNumber = routeStops.children.length + 1;
        
        const stopElement = document.createElement('div');
        stopElement.className = 'route-stop';
        stopElement.innerHTML = `
            <div class="stop-number">${stopNumber}</div>
            <div class="stop-address">${address}</div>
            <button class="btn btn--outline btn--sm" onclick="this.parentElement.remove()">Remove</button>
        `;
        
        routeStops.appendChild(stopElement);
        addressInput.value = '';
        this.showNotification(`Stop ${stopNumber} added: ${address}`, 'success');
    }

    capturePhoto() {
        // Simulate photo capture
        const preview = document.getElementById('capturePreview');
        if (preview) {
            preview.classList.remove('hidden');
            preview.classList.add('has-content');
            preview.innerHTML = `
                <div style="text-align: center; color: var(--color-success);">
                    📷 Photo captured successfully
                    <br><small>Delivery confirmation photo saved</small>
                </div>
            `;
        }
        this.showNotification('Photo captured for delivery confirmation', 'success');
    }

    captureSignature() {
        // Simulate signature capture
        const preview = document.getElementById('capturePreview');
        if (preview) {
            preview.classList.remove('hidden');
            preview.classList.add('has-content');
            preview.innerHTML = `
                <div style="text-align: center; color: var(--color-success);">
                    ✍️ Signature captured successfully
                    <br><small>Customer signature recorded</small>
                </div>
            `;
        }
        this.showNotification('Signature captured for delivery confirmation', 'success');
    }

    confirmDelivery() {
        this.showNotification('Delivery confirmed! Package marked as delivered.', 'success');
        
        // Update package status
        if (this.packages.length > 0) {
            this.packages[0].status = 'Delivered';
            this.updatePackageList();
        }
        
        // Clear capture preview
        const preview = document.getElementById('capturePreview');
        if (preview) {
            preview.classList.add('hidden');
            preview.classList.remove('has-content');
            preview.innerHTML = '';
        }
    }

    startNavigation() {
        this.showNotification('Navigation started! Turn-by-turn directions are now active.', 'success');
        this.simulateNavigation();
    }

    simulateNavigation() {
        const instructions = [
            "Head northeast on Oak Street toward Main Street",
            "Turn right onto Main Street",
            "Continue for 0.8 miles",
            "Turn left onto Elm Avenue",
            "Destination will be on your right"
        ];
        
        let currentInstruction = 0;
        const turnText = document.querySelector('.turn-text');
        
        const updateInstruction = () => {
            if (currentInstruction < instructions.length) {
                if (turnText) {
                    turnText.textContent = instructions[currentInstruction];
                }
                currentInstruction++;
                setTimeout(updateInstruction, 15000); // Change every 15 seconds for demo
            } else {
                if (turnText) {
                    turnText.textContent = "You have arrived at your destination";
                }
                this.showNotification('Navigation complete! You have arrived.', 'success');
            }
        };
        
        setTimeout(updateInstruction, 3000);
    }

    assignRoute() {
        const routeSelect = document.getElementById('routeSelect');
        const carrierSelect = document.getElementById('carrierSelect');
        
        if (!routeSelect || !carrierSelect) return;
        
        if (!routeSelect.value || !carrierSelect.value) {
            this.showNotification('Please select both a route and a carrier', 'error');
            return;
        }
        
        this.showNotification(`Route ${routeSelect.options[routeSelect.selectedIndex].text} assigned to ${carrierSelect.options[carrierSelect.selectedIndex].text}`, 'success');
    }

    toggleLiveTracking() {
        this.showNotification('Live tracking view activated. Real-time GPS positions are now visible.', 'info');
        this.simulateLiveTracking();
    }

    simulateLiveTracking() {
        const trackerItems = document.querySelectorAll('.tracker-item');
        
        setInterval(() => {
            trackerItems.forEach(item => {
                const timeSpan = item.querySelector('.tracker-time');
                if (timeSpan) {
                    const randomMinutes = Math.floor(Math.random() * 5) + 1;
                    timeSpan.textContent = `Last update: ${randomMinutes} min ago`;
                }
            });
        }, 30000); // Update every 30 seconds
    }

    exportData() {
        // Simulate data export
        const data = {
            routes: this.routes,
            packages: this.packages,
            deliveries: this.deliveries,
            exportDate: new Date().toISOString()
        };
        
        const csvContent = this.convertToCSV(data.deliveries);
        this.downloadFile('ponyxpress-deliveries.csv', csvContent, 'text/csv');
        
        this.showNotification('Delivery data exported successfully!', 'success');
    }

    convertToCSV(data) {
        if (!data.length) return 'tracking,type,status,recipient,timestamp,location\n';
        
        const headers = Object.keys(data[0]).join(',');
        const rows = data.map(item => Object.values(item).join(','));
        return headers + '\n' + rows.join('\n');
    }

    downloadFile(filename, content, contentType) {
        const blob = new Blob([content], { type: contentType });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }

    getCurrentLocation() {
        // Simulate GPS location
        const locations = [
            '123 Oak Street, Downtown',
            '456 Main Avenue, Residential',
            '789 Elm Drive, Business District',
            '321 Pine Road, Suburbs'
        ];
        return locations[Math.floor(Math.random() * locations.length)];
    }

    updateConnectionStatus() {
        const status = document.getElementById('connectionStatus');
        if (status) {
            if (this.settings.offlineMode) {
                status.textContent = '🔄 Offline Mode';
                status.style.color = 'var(--color-info)';
            } else {
                status.textContent = '📡 Online';
                status.style.color = 'var(--color-success)';
            }
        }
    }

    updateGPSStatus(state = 'ready') {
        const status = document.getElementById('gpsStatus');
        if (status) {
            const statusMap = {
                'ready': { text: '📡 GPS Ready', color: 'var(--color-success)' },
                'active': { text: '📍 GPS Active', color: 'var(--color-warning)' },
                'searching': { text: '🔍 GPS Searching', color: 'var(--color-info)' }
            };
            
            const statusInfo = statusMap[state] || statusMap['ready'];
            status.textContent = statusInfo.text;
            status.style.color = statusInfo.color;
        }
    }

    playStartupSound() {
        if (!this.settings.soundEffects) return;
        
        // Create a simple audio context for the pony neigh sound
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            // Simulate a horse neigh with frequency modulation
            oscillator.frequency.setValueAtTime(300, audioContext.currentTime);
            oscillator.frequency.exponentialRampToValueAtTime(600, audioContext.currentTime + 0.1);
            oscillator.frequency.exponentialRampToValueAtTime(200, audioContext.currentTime + 0.3);
            
            gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.5);
        } catch (error) {
            console.log('Audio not supported');
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification status--${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 80px;
            right: 16px;
            max-width: 300px;
            padding: 12px 16px;
            border-radius: 8px;
            font-weight: 500;
            z-index: 1000;
            animation: slideIn 0.3s ease-out;
        `;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    saveSettings() {
        localStorage.setItem('ponyxpress-settings', JSON.stringify(this.settings));
    }

    // Easter egg - random Seth Rogen laugh
    playRandomLaugh() {
        if (Math.random() < 0.01 && this.settings.soundEffects) { // 1% chance
            console.log('🎭 Seth Rogen laugh triggered!');
            this.showNotification('🎭 Heh heh heh... (Easter egg activated!)', 'info');
        }
    }
}

// Add CSS animations for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing PONYXPRESS...');
    window.ponyXpress = new PonyXpressApp();
    
    // Easter egg trigger on random clicks
    document.addEventListener('click', () => {
        if (window.ponyXpress) {
            window.ponyXpress.playRandomLaugh();
        }
    });
});

// Also initialize if DOM is already loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        if (!window.ponyXpress) {
            console.log('DOM ready, initializing PONYXPRESS...');
            window.ponyXpress = new PonyXpressApp();
        }
    });
} else {
    console.log('DOM already ready, initializing PONYXPRESS...');
    window.ponyXpress = new PonyXpressApp();
}

// PWA Install prompt
let deferredPrompt;
window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    
    // Show install button or notification
    const installBtn = document.createElement('button');
    installBtn.textContent = '📱 Install PONYXPRESS';
    installBtn.className = 'btn btn--primary';
    installBtn.style.cssText = `
        position: fixed;
        bottom: 60px;
        left: 16px;
        z-index: 100;
    `;
    
    installBtn.onclick = async () => {
        if (deferredPrompt) {
            deferredPrompt.prompt();
            const { outcome } = await deferredPrompt.userChoice;
            console.log(`Install prompt result: ${outcome}`);
            deferredPrompt = null;
            installBtn.remove();
        }
    };
    
    document.body.appendChild(installBtn);
    
    // Auto-remove install button after 10 seconds
    setTimeout(() => {
        if (installBtn.parentNode) {
            installBtn.remove();
        }
    }, 10000);
});

// Handle app installation
window.addEventListener('appinstalled', () => {
    console.log('PONYXPRESS installed successfully!');
    if (window.ponyXpress) {
        window.ponyXpress.showNotification('PONYXPRESS installed as an app!', 'success');
    }
});

// Offline/Online detection
window.addEventListener('online', () => {
    if (window.ponyXpress) {
        window.ponyXpress.showNotification('Connection restored!', 'success');
        window.ponyXpress.updateConnectionStatus();
    }
});

window.addEventListener('offline', () => {
    if (window.ponyXpress) {
        window.ponyXpress.showNotification('Working offline', 'info');
        window.ponyXpress.updateConnectionStatus();
    }
});