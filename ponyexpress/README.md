# PonyXpress 🚚

**Rural Delivery Route Management System**

A complete web application for managing rural delivery routes and packages, built with Flask, SQLite, and modern web technologies.

## 🌟 Features

### Core Functionality
- **User Authentication** with role-based access control
- **Interactive Map** for route creation and visualization (Leaflet.js)
- **Barcode Scanning** with package size toggles
- **Offline Support** (PWA with Service Worker)
- **Photo Attachment** for mailbox stops
- **Real-time GPS** location tracking

### User Roles

#### 🚛 Carrier
- Scan packages with barcode/manual input
- Create and edit delivery routes on interactive map
- Mark packages as "Too Big" (house delivery) or "Right Size" (mailbox)
- Take photos of delivery locations
- GPS tracking for mailbox stops

#### 👤 Substitute
- View existing routes and mailbox stops (read-only)
- Access route traces and delivery information
- Cannot scan packages or create new routes

#### 🔧 Admin
- Full system access and user management
- Create, edit, and delete users
- View all routes and delivery logs
- Export delivery data to CSV
- System monitoring and maintenance

### Technical Features
- **Progressive Web App (PWA)** - installable and works offline
- **Responsive Design** - works on desktop, tablet, and mobile
- **Real-time Notifications** - both in-app and browser notifications
- **Offline Data Sync** - stores data locally when offline, syncs when online
- **Modern UI** - Bootstrap 5 with custom styling and animations
- **Security** - Password hashing, session management, CSRF protection

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite3
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **CSS Framework**: Bootstrap 5.3.2
- **Icons**: Bootstrap Icons
- **Maps**: Leaflet.js
- **Authentication**: Flask-Login
- **PWA**: Service Worker, Web App Manifest

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Modern web browser

### Setup Instructions

1. **Clone or extract the project**
   ```bash
   cd ponyexpress
   ```

2. **Create a virtual environment** (recommended)
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

4. **Initialize the database**
   ```bash
   python app.py
   ```
   The app will automatically create the SQLite database and default admin user on first run.

5. **Access the application**
   Open your browser and navigate to: `http://localhost:5000`

### Default Login Credentials
- **Username**: `admin`
- **Password**: `admin123`

⚠️ **Important**: Change the default admin password immediately after first login.

## 🚀 Usage

### Getting Started

1. **Login** with the default admin credentials
2. **Create Users** via Admin → Users → Add New User
3. **Assign Roles** (Carrier, Substitute, or Admin)
4. **Start Creating Routes** using the Map interface
5. **Begin Scanning Packages** using the Scan page

### Creating Routes

1. Navigate to **Map** page
2. Click **"Draw Route"** button
3. Click on the map to create route points
4. Click **"Save Route"** when finished
5. Enter a route name and save

### Scanning Packages

1. Go to **Scan** page
2. Enter barcode manually or use camera (simulated)
3. Select package size:
   - **Too Big** → Red pin (house delivery)
   - **Right Size** → Green pin (mailbox delivery)
4. Optionally take a photo
5. Click **"Record Delivery"**

### Managing Users (Admin Only)

1. Navigate to **Admin → Users**
2. Use **"Add New User"** to create accounts
3. Toggle user status (Active/Inactive)
4. Export user data or perform bulk actions

## 🏗️ Project Structure

```
ponyexpress/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── ponyexpress.db        # SQLite database (created on first run)
├── database/
│   └── schema.sql        # Database schema
├── templates/            # Jinja2 HTML templates
│   ├── base.html         # Base template
│   ├── login.html        # Login page
│   ├── dashboard.html    # Main dashboard
│   ├── map.html          # Interactive map
│   ├── scan.html         # Package scanning
│   ├── admin/            # Admin templates
│   │   ├── dashboard.html
│   │   ├── users.html
│   │   └── create_user.html
│   └── errors/           # Error pages
│       ├── 404.html
│       └── 500.html
└── static/               # Static assets
    ├── css/
    │   └── style.css     # Custom styles
    ├── js/
    │   └── app.js        # Main JavaScript
    ├── icons/            # PWA icons
    └── sw.js            # Service Worker
```

## 🔧 Configuration

### Environment Variables
Set these in production:

```bash
export FLASK_ENV=production
export SECRET_KEY=your-secure-secret-key
export DATABASE_URL=sqlite:///ponyexpress.db
```

### Security Settings
- Change the default `SECRET_KEY` in `app.py`
- Use HTTPS in production
- Configure proper CORS settings
- Set up database backups

### PWA Configuration
The app includes:
- **Manifest file** (`/manifest.json`)
- **Service Worker** (`/sw.js`)
- **Offline functionality**
- **Install prompts**

## 📱 Mobile Usage

PonyXpress is designed as a Progressive Web App (PWA):

1. **Install on Mobile**:
   - Open in mobile browser
   - Tap "Add to Home Screen"
   - Use like a native app

2. **Offline Capability**:
   - Works without internet connection
   - Stores data locally
   - Syncs when connection is restored

3. **GPS Features**:
   - Automatic location detection
   - Real-time position tracking
   - Location-based delivery logging

## 🗃️ Database Schema

### Key Tables
- **users** - User accounts and authentication
- **routes** - Route traces and GPS data
- **deliveries** - Package delivery records
- **mailbox_stops** - Permanent mailbox locations
- **delivery_logs** - Audit trail and tracking

### Relationships
- Users can have multiple routes
- Routes contain multiple deliveries
- Deliveries can create mailbox stops
- All actions are logged for audit purposes

## 🔍 API Endpoints

### Public Endpoints
- `POST /login` - User authentication
- `GET /logout` - User logout

### Protected Endpoints
- `GET /api/get-routes` - Fetch user routes
- `GET /api/get-mailbox-stops` - Fetch mailbox locations
- `POST /api/scan-package` - Record package scan
- `POST /api/save-route` - Save route data

### Admin Endpoints
- `GET /admin/*` - Admin dashboard pages
- `POST /admin/users/create` - Create new user
- `POST /admin/users/{id}/toggle-status` - Toggle user status
- `GET /admin/export-deliveries` - Export delivery data

## 🛡️ Security Features

- **Password Hashing** - Werkzeug security
- **Session Management** - Flask-Login
- **Role-Based Access** - Custom decorators
- **CSRF Protection** - Built-in Flask security
- **Input Validation** - Server and client-side
- **SQL Injection Prevention** - Parameterized queries

## 🧪 Testing

### Manual Testing
1. Test all user roles and permissions
2. Verify offline functionality
3. Test map creation and viewing
4. Validate package scanning workflow
5. Check admin features and exports

### Browser Compatibility
- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## 🚀 Deployment

### Development
```bash
python app.py
```

### Production (Example with Gunicorn)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

## 🔧 Maintenance

### Database Backup
```bash
# Backup database
cp ponyexpress.db ponyexpress_backup_$(date +%Y%m%d).db

# Restore database
cp ponyexpress_backup_YYYYMMDD.db ponyexpress.db
```

### Log Monitoring
- Check application logs in console output
- Monitor error rates and user activity
- Regular security updates and patches

### Performance Optimization
- Database indexing (already included)
- Static file caching
- Image compression for photos
- Service Worker caching strategy

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🆘 Support

### Common Issues

**Q: Database not found error**
A: Run `python app.py` to initialize the database automatically.

**Q: Can't login with admin credentials**
A: Ensure database is initialized and try `admin` / `admin123`.

**Q: Map not loading**
A: Check internet connection for Leaflet.js CDN resources.

**Q: Photos not uploading**
A: Ensure the `static/uploads` directory exists and has write permissions.

### Getting Help
- Check the console for error messages
- Verify all dependencies are installed
- Ensure proper file permissions
- Test in a different browser

### Contact
For technical support or feature requests, please create an issue in the project repository.

---

**PonyXpress** - Making rural delivery management simple and efficient! 🚚📦