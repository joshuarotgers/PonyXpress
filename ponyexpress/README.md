# PonyXpress - Rural Delivery Management System

A comprehensive web application for managing rural delivery routes and packages. Built with Flask, SQLite, and modern web technologies.

## 🚀 Features

### Core Functionality
- **Role-based Authentication**: Admin, Carrier, and Substitute roles with different permissions
- **Interactive Route Mapping**: Draw and edit delivery routes using Leaflet maps
- **Package Scanning**: Barcode scanning with package type classification
- **GPS Integration**: Automatic location tracking and mailbox stop creation
- **Photo Management**: Upload and manage photos for mailbox stops
- **Offline Support**: PWA with service worker for offline functionality

### User Roles

#### Carrier
- Draw and edit daily delivery routes
- Scan packages and categorize by size
- Create mailbox stops with GPS coordinates
- Upload photos for mailbox identification
- View route history and statistics

#### Substitute
- View all carrier routes (read-only)
- Access mailbox stop information
- View delivery logs and statistics

#### Admin
- Manage all users and roles
- View and export delivery logs
- Monitor system statistics
- Manage routes and mailbox stops
- Export data to CSV format

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone or download the project**
   ```bash
   cd ponyexpress
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   Open your web browser and navigate to `http://localhost:5000`

## 🔐 Default Login Credentials

The application creates default users on first run:

- **Admin**: `admin` / `admin123`
- **Carrier**: `carrier` / `carrier123` (create via admin panel)
- **Substitute**: `substitute` / `sub123` (create via admin panel)

## 📱 PWA Features

PonyXpress is a Progressive Web App (PWA) with the following features:

- **Offline Support**: Works without internet connection
- **App-like Experience**: Can be installed on mobile devices
- **Background Sync**: Syncs data when connection is restored
- **Push Notifications**: Real-time updates (if configured)

## 🗺️ Route Management

### Drawing Routes
1. Navigate to "Route Map" as a Carrier
2. Click "Draw Route" button
3. Click on the map to add route points
4. Click "Save Route" when finished

### Mailbox Stops
- Small packages automatically create mailbox stops
- Add photos to mailbox stops for identification
- GPS coordinates are automatically captured

## 📦 Package Scanning

### Package Types
- **Big Package**: Delivered to house (red pin on map)
- **Small Package**: Delivered to mailbox (green pin + GPS stop)

### Scanning Process
1. Select package type (Big/Small)
2. Enter or scan barcode
3. GPS location is automatically captured
4. Package is logged and route updated

## 📊 Admin Features

### User Management
- Create new users with different roles
- Modify existing user permissions
- View user activity and statistics

### Data Export
- Export delivery logs to CSV
- Export package data with date ranges
- Export route information
- Export mailbox stop data

### System Monitoring
- Real-time statistics dashboard
- Route performance metrics
- Package delivery tracking
- System health monitoring

## 🗄️ Database Schema

The application uses SQLite with the following tables:

- **users**: User accounts and roles
- **routes**: Daily delivery routes with GPS coordinates
- **mailbox_stops**: GPS coordinates and photos for mailbox locations
- **packages**: Scanned package information
- **delivery_logs**: Daily delivery summaries

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
FLASK_SECRET_KEY=your-secret-key-here
FLASK_ENV=development
UPLOAD_FOLDER=static/uploads
MAX_CONTENT_LENGTH=16777216
```

### Database
The SQLite database (`ponyxpress.db`) is automatically created on first run.

## 📁 Project Structure

```
ponyexpress/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── database/
│   └── models.py         # Database models and ORM
├── utils/
│   ├── helpers.py        # Utility functions
│   └── export.py         # CSV export functionality
├── templates/
│   ├── base.html         # Base template
│   ├── login.html        # Login page
│   ├── carrier/          # Carrier-specific templates
│   ├── substitute/       # Substitute-specific templates
│   └── admin/           # Admin-specific templates
└── static/
    ├── css/
    │   └── style.css     # Custom styles
    ├── js/
    │   └── app.js        # Main JavaScript
    ├── manifest.json     # PWA manifest
    ├── sw.js            # Service worker
    └── uploads/         # Photo uploads directory
```

## 🚀 Deployment

### Development
```bash
python app.py
```

### Production
For production deployment, consider:

1. **WSGI Server**: Use Gunicorn or uWSGI
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

2. **Reverse Proxy**: Use Nginx or Apache

3. **Environment**: Set `FLASK_ENV=production`

4. **Security**: Change default secret key and passwords

## 🔒 Security Considerations

- Change default admin password immediately
- Use HTTPS in production
- Regularly backup the SQLite database
- Implement rate limiting for API endpoints
- Validate all user inputs
- Use environment variables for sensitive data

## 🐛 Troubleshooting

### Common Issues

1. **Database not created**
   - Ensure write permissions in project directory
   - Check Python path and virtual environment

2. **Photos not uploading**
   - Create `static/uploads` directory
   - Check file permissions

3. **GPS not working**
   - Ensure HTTPS in production (required for GPS)
   - Check browser permissions

4. **Offline functionality not working**
   - Clear browser cache
   - Check service worker registration
   - Verify manifest.json is accessible

### Logs
Check console output for error messages and debugging information.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the troubleshooting section above
- Review the code comments for implementation details
- Create an issue for bugs or feature requests

## 🔄 Updates

To update the application:

1. Backup your database
2. Pull latest changes
3. Update dependencies: `pip install -r requirements.txt`
4. Restart the application

---

**PonyXpress** - Making rural delivery management simple and efficient! 🐎📦