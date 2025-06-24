# PONYXPRESS Installation Guide

## Platform-Specific Installation Instructions

### 🌐 Web/Progressive Web App (PWA)

#### Chrome, Edge, Firefox, Safari
1. Navigate to the PONYXPRESS web URL
2. Click the "Install" button in the address bar (Chrome/Edge)
3. Or access "Add to Home Screen" from browser menu
4. Launch from desktop or app drawer

#### Mobile Installation
- **Android**: Chrome will prompt for installation, appears in app drawer
- **iOS**: Safari → Share → Add to Home Screen → Opens as native-like app

---

### 🤖 Android Installation

#### Method 1: APK Sideloading
```bash
# Enable "Unknown Sources" in Android settings
# Download ponyxpress-android.apk
adb install ponyxpress-android.apk

# Or manually:
# 1. Download APK to device
# 2. Open file manager, locate APK
# 3. Tap to install, grant permissions
```

#### Method 2: Launcher Replacement
```bash
# For full OS replacement mode
# 1. Install PONYXPRESS APK
# 2. Go to Settings → Apps → Default Apps → Home App
# 3. Select PONYXPRESS as default launcher
```

#### Required Permissions
- Camera (package scanning)
- Location (GPS navigation)
- Microphone (voice commands)
- Storage (offline data)
- Phone (emergency contact)

---

### 🍎 iOS Installation

#### TestFlight Installation
1. Receive TestFlight invitation email/link
2. Install TestFlight app from App Store
3. Open invitation link on iOS device
4. Tap "Install" in TestFlight
5. App appears on home screen

#### PWA Installation (Alternative)
1. Open Safari, navigate to PONYXPRESS URL
2. Tap Share button (square with arrow)
3. Select "Add to Home Screen"
4. Customize name and tap "Add"
5. Launch from home screen (full-screen mode)

---

### 🖥️ Windows Installation

#### Method 1: Installer Package
```batch
# Download ponyxpress-windows-setup.exe
# Double-click to run installer
# Follow setup wizard
# Choose installation directory
# Select additional components:
#   - Mistral 7B AI Assistant
#   - Offline Map Data
#   - Zebra Scanner Drivers
```

#### Method 2: Portable Version
```batch
# Download ponyxpress-windows-portable.zip
# Extract to desired folder
# Run ponyxpress.exe
# No installation required
```

#### Method 3: Microsoft Store (Future)
```batch
# Search "PONYXPRESS" in Microsoft Store
# Click "Get" or "Install"
# Launch from Start Menu
```

#### System Requirements
- Windows 10 version 1903 or later
- 4GB RAM minimum (8GB recommended with AI)
- 2GB available storage
- DirectX 11 compatible graphics

---

### 🖥️ macOS Installation

#### Method 1: DMG Installer
```bash
# Download ponyxpress-macos.dmg
# Double-click to mount
# Drag PONYXPRESS.app to Applications folder
# Launch from Applications or Spotlight
# Grant permissions when prompted
```

#### Method 2: Homebrew (Advanced)
```bash
# Install via Homebrew Cask
brew install --cask ponyxpress

# Or from source
brew tap ponyxpress/tap
brew install ponyxpress
```

#### Required Permissions
- Camera Access (System Preferences → Security & Privacy)
- Microphone Access (for voice commands)
- Location Services (for GPS navigation)
- Full Disk Access (for local encryption)

#### Apple Silicon (M1/M2) Notes
- Native ARM64 support included
- Enhanced performance with AI assistant
- Battery optimization for mobile use

---

### 🐧 Linux Installation

#### Ubuntu/Debian (DEB Package)
```bash
# Download .deb package
wget https://releases.ponyxpress.com/ponyxpress_1.0.0_amd64.deb

# Install with dependencies
sudo dpkg -i ponyxpress_1.0.0_amd64.deb
sudo apt-get install -f

# Launch
ponyxpress
# Or from applications menu
```

#### Red Hat/CentOS/Fedora (RPM Package)
```bash
# Download RPM package
wget https://releases.ponyxpress.com/ponyxpress-1.0.0-1.x86_64.rpm

# Install
sudo rpm -ivh ponyxpress-1.0.0-1.x86_64.rpm
# Or with yum/dnf
sudo yum install ponyxpress-1.0.0-1.x86_64.rpm
```

#### Universal Installation Script
```bash
# One-line installer for all distributions
curl -sSL https://install.ponyxpress.com | bash

# Or download and inspect first
curl -sSL https://install.ponyxpress.com -o install.sh
chmod +x install.sh
./install.sh
```

#### AppImage (Portable)
```bash
# Download AppImage
wget https://releases.ponyxpress.com/PONYXPRESS-1.0.0-x86_64.AppImage
chmod +x PONYXPRESS-1.0.0-x86_64.AppImage

# Run directly
./PONYXPRESS-1.0.0-x86_64.AppImage

# Integrate with desktop
./PONYXPRESS-1.0.0-x86_64.AppImage --appimage-integrate
```

#### Dependencies
```bash
# Required packages (auto-installed with package managers)
sudo apt-get install \
    libgtk-3-0 \
    libnotify4 \
    libnss3 \
    libatspi2.0-0 \
    libdrm2 \
    libgtk-3-0 \
    libgtk-3-common
```

---

## 🤖 AI Assistant Setup (Mistral 7B)

### Automatic Installation (Recommended)
- AI assistant downloads automatically on first launch
- Approximately 4GB download for full Mistral 7B model
- Cached locally for offline use

### Manual Installation
```bash
# Windows
cd "C:\Program Files\PONYXPRESS\ai_assistant"
download-mistral.bat

# macOS
cd "/Applications/PONYXPRESS.app/Contents/Resources/ai"
./download-mistral.sh

# Linux
cd "/opt/ponyxpress/ai_assistant"
sudo ./download-mistral.sh
```

### System Requirements for AI
- **Minimum**: 8GB RAM, 4GB available storage
- **Recommended**: 16GB RAM, 8GB available storage
- **GPU Acceleration**: Optional NVIDIA CUDA or AMD ROCm support

---

## 🗺️ Offline Maps Setup

### Automatic Download
- Maps download automatically for detected location
- Covers 50-mile radius around initial GPS position
- Updates available monthly

### Manual Map Selection
```bash
# Access via Settings → Maps → Download Regions
# Available regions:
# - United States (Complete): 12GB
# - State-by-state: 200MB - 2GB each
# - Metropolitan areas: 50MB - 500MB each
# - Custom bounding box: Variable size
```

### Map Storage Locations
- **Windows**: `%APPDATA%\PONYXPRESS\maps\`
- **macOS**: `~/Library/Application Support/PONYXPRESS/maps/`
- **Linux**: `~/.config/ponyxpress/maps/`
- **Android**: `/sdcard/Android/data/com.ponyxpress/files/maps/`
- **iOS**: App sandbox container

---

## 🔐 Initial Configuration

### First Launch Setup
1. **Select Role**: Carrier, Substitute, Supervisor, Admin
2. **Location Permission**: Allow for GPS functionality
3. **Camera Permission**: Required for package scanning
4. **Microphone Permission**: Needed for "Hey AI" commands
5. **Storage Permission**: For offline data and photos

### Account Setup
```bash
# Create local profile (offline mode)
# Or connect to organization server
# Import existing route data
# Configure backup preferences
```

### Voice Training
1. Complete voice calibration: "Hey AI, train my voice"
2. Record 5-10 sample phrases
3. Test activation: "Hey AI, hello"
4. Configure case memory addresses

---

## 🛠️ Troubleshooting Common Issues

### Installation Problems

#### "Unknown Publisher" Warning (Windows)
```batch
# Right-click installer → Properties → Unblock
# Or temporarily disable SmartScreen
# Or add certificate to trusted publishers
```

#### Permission Denied (Linux)
```bash
# Ensure execute permissions
chmod +x ponyxpress-installer.sh

# Install with sudo if needed
sudo ./ponyxpress-installer.sh
```

#### App Store Rejection (iOS)
```bash
# Use TestFlight for pre-release distribution
# Or install as PWA via Safari
# Enterprise distribution requires MDM
```

### Runtime Issues

#### Voice Commands Not Working
1. Check microphone permissions
2. Test with "Hey AI, test microphone"
3. Retrain voice model if needed
4. Verify audio input device

#### GPS Accuracy Problems
1. Enable high-accuracy GPS mode
2. Ensure location permissions granted
3. Download offline maps for area
4. Clear GPS cache and restart

#### Scanner Not Detecting Codes
1. Check camera permissions
2. Ensure adequate lighting
3. Clean camera lens
4. Test with sample barcodes

### Performance Optimization

#### Reduce Memory Usage
```bash
# Disable AI assistant if not needed
# Lower map cache size
# Reduce photo resolution
# Clear old delivery data
```

#### Improve Battery Life
```bash
# Enable battery saver mode
# Reduce GPS accuracy
# Disable unnecessary features
# Use dark theme
```

---

## 📁 File Structure After Installation

```
PONYXPRESS/
├── 📁 app/                 # Main application files
│   ├── index.html          # Web app entry point
│   ├── app.js              # Core application logic
│   ├── style.css           # UI styling
│   └── manifest.json       # PWA configuration
├── 📁 ai_assistant/        # Mistral 7B integration
│   ├── models/             # AI model files
│   ├── voice/              # Voice processing
│   └── training/           # Custom voice data
├── 📁 maps/                # Offline map data
│   ├── tiles/              # Map tile cache
│   └── routing/            # Route calculation data
├── 📁 data/                # Local storage
│   ├── routes/             # Route definitions
│   ├── deliveries/         # Delivery history
│   ├── photos/             # Delivery photos
│   └── signatures/         # Digital signatures
├── 📁 config/              # Configuration files
│   ├── settings.json       # User preferences
│   ├── roles.json          # Role definitions
│   └── encryption.key      # Local encryption key
└── 📁 docs/                # Documentation
    ├── user-guide.pdf      # Complete user manual
    ├── api-docs.html       # Developer documentation
    └── troubleshooting.md  # Support information
```

---

## 🔄 Updates and Maintenance

### Automatic Updates
- App checks for updates daily when online
- Critical security updates install automatically
- Feature updates require user approval

### Manual Update Process
```bash
# Web/PWA: Refresh browser or reinstall
# Windows: Download new installer or use built-in updater
# macOS: Download new DMG or use app updater
# Linux: Update via package manager or download new package
# Mobile: Update via app store or TestFlight
```

### Backup and Migration
```bash
# Export settings and data
ponyxpress --export-data backup.json

# Import on new installation
ponyxpress --import-data backup.json

# Cloud sync automatically handles migration
```

---

## 📞 Support and Resources

### Getting Help
- **In-app support**: Settings → Help & Support
- **Voice command**: "Hey AI, I need help"
- **Documentation**: Access offline user guide
- **Community forum**: https://community.ponyxpress.com
- **Technical support**: support@ponyxpress.com

### Additional Resources
- Video tutorials: https://learn.ponyxpress.com
- API documentation: https://docs.ponyxpress.com
- Source code: https://github.com/ponyxpress (coming soon)
- Training materials: https://training.ponyxpress.com