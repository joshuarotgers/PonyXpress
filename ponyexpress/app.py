"""
PonyXpress - Rural Delivery Route Management System
Main Flask application with authentication and route management
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_file
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
import json
import csv
from datetime import datetime
from functools import wraps
import base64

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Database configuration
DATABASE = 'ponyexpress.db'

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with schema"""
    with app.app_context():
        conn = get_db()
        with open('database/schema.sql', 'r') as f:
            conn.executescript(f.read())
        conn.close()

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username, email, role, active=True):
        self.id = id
        self.username = username
        self.email = email
        self.role = role
        self.active = active

@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    conn = get_db()
    user = conn.execute(
        'SELECT * FROM users WHERE id = ?', (user_id,)
    ).fetchone()
    conn.close()
    
    if user:
        return User(user['id'], user['username'], user['email'], user['role'], user['active'])
    return None

# Role-based access decorator
def role_required(*roles):
    """Decorator to require specific roles"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            if current_user.role not in roles:
                flash('You do not have permission to access this page.', 'error')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Routes

@app.route('/')
def index():
    """Home page - redirect to dashboard if logged in"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ? AND active = 1', (username,)
        ).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            user_obj = User(user['id'], user['username'], user['email'], user['role'])
            login_user(user_obj)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard - role-specific content"""
    conn = get_db()
    
    # Get user's active route if any
    active_route = conn.execute(
        'SELECT * FROM routes WHERE user_id = ? AND status = "active" ORDER BY created_at DESC LIMIT 1',
        (current_user.id,)
    ).fetchone()
    
    # Get recent deliveries
    recent_deliveries = conn.execute(
        'SELECT * FROM deliveries WHERE user_id = ? ORDER BY created_at DESC LIMIT 10',
        (current_user.id,)
    ).fetchall()
    
    conn.close()
    
    return render_template('dashboard.html', 
                         active_route=active_route, 
                         recent_deliveries=recent_deliveries)

@app.route('/map')
@login_required
def map_view():
    """Interactive map for route creation and viewing"""
    conn = get_db()
    
    # Get user's routes
    routes = conn.execute(
        'SELECT * FROM routes WHERE user_id = ? ORDER BY created_at DESC',
        (current_user.id,)
    ).fetchall()
    
    # Get mailbox stops
    mailbox_stops = conn.execute(
        'SELECT * FROM mailbox_stops WHERE user_id = ? ORDER BY created_at DESC',
        (current_user.id,)
    ).fetchall()
    
    conn.close()
    
    return render_template('map.html', routes=routes, mailbox_stops=mailbox_stops)

@app.route('/scan')
@login_required
@role_required('carrier', 'admin')
def scan_packages():
    """Barcode scanning page for carriers"""
    return render_template('scan.html')

@app.route('/api/scan-package', methods=['POST'])
@login_required
@role_required('carrier', 'admin')
def api_scan_package():
    """API endpoint for package scanning"""
    data = request.get_json()
    barcode = data.get('barcode')
    too_big = data.get('too_big', False)
    too_small = data.get('too_small', False)
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    photo = data.get('photo')  # Base64 encoded photo
    
    if not barcode:
        return jsonify({'error': 'Barcode is required'}), 400
    
    # Determine delivery type and location
    delivery_type = 'house' if too_big else 'mailbox'
    
    conn = get_db()
    
    # Save delivery record
    delivery_id = conn.execute(
        '''INSERT INTO deliveries (user_id, barcode, delivery_type, latitude, longitude, created_at)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (current_user.id, barcode, delivery_type, latitude, longitude, datetime.now())
    ).lastrowid
    
    # If too_small (deliver to mailbox), save as mailbox stop
    if too_small and latitude and longitude:
        conn.execute(
            '''INSERT INTO mailbox_stops (user_id, latitude, longitude, delivery_id, created_at)
               VALUES (?, ?, ?, ?, ?)''',
            (current_user.id, latitude, longitude, delivery_id, datetime.now())
        )
    
    # Save photo if provided
    if photo:
        try:
            # Decode base64 photo
            photo_data = base64.b64decode(photo.split(',')[1])
            filename = f"delivery_{delivery_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            with open(filepath, 'wb') as f:
                f.write(photo_data)
            
            # Update delivery record with photo filename
            conn.execute(
                'UPDATE deliveries SET photo = ? WHERE id = ?',
                (filename, delivery_id)
            )
        except Exception as e:
            print(f"Error saving photo: {e}")
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'delivery_id': delivery_id,
        'delivery_type': delivery_type
    })

@app.route('/api/save-route', methods=['POST'])
@login_required
@role_required('carrier', 'admin')
def api_save_route():
    """API endpoint for saving route traces"""
    data = request.get_json()
    route_data = data.get('route_data')  # GeoJSON format
    route_name = data.get('name', f"Route {datetime.now().strftime('%Y-%m-%d')}")
    
    if not route_data:
        return jsonify({'error': 'Route data is required'}), 400
    
    conn = get_db()
    
    # Deactivate any existing active routes for this user
    conn.execute(
        'UPDATE routes SET status = "inactive" WHERE user_id = ? AND status = "active"',
        (current_user.id,)
    )
    
    # Save new route
    route_id = conn.execute(
        '''INSERT INTO routes (user_id, name, route_data, status, created_at)
           VALUES (?, ?, ?, "active", ?)''',
        (current_user.id, route_name, json.dumps(route_data), datetime.now())
    ).lastrowid
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'route_id': route_id})

@app.route('/api/get-routes')
@login_required
def api_get_routes():
    """API endpoint to get user's routes"""
    conn = get_db()
    
    if current_user.role == 'substitute':
        # Substitutes can only view, not their own routes but assigned routes
        routes = conn.execute(
            'SELECT * FROM routes WHERE status = "active" ORDER BY created_at DESC'
        ).fetchall()
    else:
        routes = conn.execute(
            'SELECT * FROM routes WHERE user_id = ? ORDER BY created_at DESC',
            (current_user.id,)
        ).fetchall()
    
    conn.close()
    
    routes_list = []
    for route in routes:
        routes_list.append({
            'id': route['id'],
            'name': route['name'],
            'route_data': json.loads(route['route_data']) if route['route_data'] else None,
            'status': route['status'],
            'created_at': route['created_at']
        })
    
    return jsonify(routes_list)

@app.route('/api/get-mailbox-stops')
@login_required
def api_get_mailbox_stops():
    """API endpoint to get mailbox stops"""
    conn = get_db()
    
    if current_user.role == 'substitute':
        # Substitutes can view all mailbox stops
        stops = conn.execute(
            'SELECT * FROM mailbox_stops ORDER BY created_at DESC'
        ).fetchall()
    else:
        stops = conn.execute(
            'SELECT * FROM mailbox_stops WHERE user_id = ? ORDER BY created_at DESC',
            (current_user.id,)
        ).fetchall()
    
    conn.close()
    
    stops_list = []
    for stop in stops:
        stops_list.append({
            'id': stop['id'],
            'latitude': stop['latitude'],
            'longitude': stop['longitude'],
            'delivery_id': stop['delivery_id'],
            'created_at': stop['created_at']
        })
    
    return jsonify(stops_list)

# Admin routes

@app.route('/admin')
@login_required
@role_required('admin')
def admin_dashboard():
    """Admin dashboard"""
    conn = get_db()
    
    # Get statistics
    total_users = conn.execute('SELECT COUNT(*) as count FROM users').fetchone()['count']
    total_routes = conn.execute('SELECT COUNT(*) as count FROM routes').fetchone()['count']
    total_deliveries = conn.execute('SELECT COUNT(*) as count FROM deliveries').fetchone()['count']
    total_mailboxes = conn.execute('SELECT COUNT(*) as count FROM mailbox_stops').fetchone()['count']
    
    # Get recent activity
    recent_users = conn.execute(
        'SELECT * FROM users ORDER BY created_at DESC LIMIT 10'
    ).fetchall()
    
    recent_routes = conn.execute(
        'SELECT r.*, u.username FROM routes r JOIN users u ON r.user_id = u.id ORDER BY r.created_at DESC LIMIT 10'
    ).fetchall()
    
    conn.close()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_routes=total_routes,
                         total_deliveries=total_deliveries,
                         total_mailboxes=total_mailboxes,
                         recent_users=recent_users,
                         recent_routes=recent_routes)

@app.route('/admin/users')
@login_required
@role_required('admin')
def admin_users():
    """Admin user management"""
    conn = get_db()
    users = conn.execute('SELECT * FROM users ORDER BY created_at DESC').fetchall()
    conn.close()
    
    return render_template('admin/users.html', users=users)

@app.route('/admin/users/create', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def admin_create_user():
    """Create new user"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        
        # Validate input
        if not all([username, email, password, role]):
            flash('All fields are required.', 'error')
            return render_template('admin/create_user.html')
        
        if role not in ['carrier', 'substitute', 'admin']:
            flash('Invalid role selected.', 'error')
            return render_template('admin/create_user.html')
        
        conn = get_db()
        
        # Check if username exists
        existing_user = conn.execute(
            'SELECT id FROM users WHERE username = ?', (username,)
        ).fetchone()
        
        if existing_user:
            flash('Username already exists.', 'error')
            conn.close()
            return render_template('admin/create_user.html')
        
        # Create user
        password_hash = generate_password_hash(password)
        conn.execute(
            '''INSERT INTO users (username, email, password, role, active, created_at)
               VALUES (?, ?, ?, ?, 1, ?)''',
            (username, email, password_hash, role, datetime.now())
        )
        conn.commit()
        conn.close()
        
        flash('User created successfully!', 'success')
        return redirect(url_for('admin_users'))
    
    return render_template('admin/create_user.html')

@app.route('/admin/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@role_required('admin')
def admin_toggle_user_status(user_id):
    """Toggle user active status"""
    conn = get_db()
    
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    if not user:
        flash('User not found.', 'error')
        conn.close()
        return redirect(url_for('admin_users'))
    
    new_status = 0 if user['active'] else 1
    conn.execute('UPDATE users SET active = ? WHERE id = ?', (new_status, user_id))
    conn.commit()
    conn.close()
    
    status_text = 'activated' if new_status else 'deactivated'
    flash(f'User {user["username"]} has been {status_text}.', 'success')
    
    return redirect(url_for('admin_users'))

@app.route('/admin/export-deliveries')
@login_required
@role_required('admin')
def admin_export_deliveries():
    """Export delivery logs to CSV"""
    conn = get_db()
    deliveries = conn.execute(
        '''SELECT d.*, u.username 
           FROM deliveries d 
           JOIN users u ON d.user_id = u.id 
           ORDER BY d.created_at DESC'''
    ).fetchall()
    conn.close()
    
    # Create CSV file
    filename = f"deliveries_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    with open(filepath, 'w', newline='') as csvfile:
        fieldnames = ['id', 'username', 'barcode', 'delivery_type', 'latitude', 'longitude', 'photo', 'created_at']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for delivery in deliveries:
            writer.writerow({
                'id': delivery['id'],
                'username': delivery['username'],
                'barcode': delivery['barcode'],
                'delivery_type': delivery['delivery_type'],
                'latitude': delivery['latitude'],
                'longitude': delivery['longitude'],
                'photo': delivery['photo'],
                'created_at': delivery['created_at']
            })
    
    return send_file(filepath, as_attachment=True, download_name=filename)

# PWA routes

@app.route('/manifest.json')
def manifest():
    """PWA manifest file"""
    return jsonify({
        "name": "PonyXpress",
        "short_name": "PonyXpress",
        "description": "Rural Delivery Route Management System",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#007bff",
        "icons": [
            {
                "src": "/static/icons/icon-192x192.png",
                "sizes": "192x192",
                "type": "image/png"
            },
            {
                "src": "/static/icons/icon-512x512.png",
                "sizes": "512x512",
                "type": "image/png"
            }
        ]
    })

@app.route('/sw.js')
def service_worker():
    """Service worker for offline support"""
    return app.send_static_file('sw.js')

# Error handlers

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    # Initialize database if it doesn't exist
    if not os.path.exists(DATABASE):
        init_db()
        
        # Create default admin user
        conn = get_db()
        admin_password = generate_password_hash('admin123')
        conn.execute(
            '''INSERT INTO users (username, email, password, role, active, created_at)
               VALUES (?, ?, ?, ?, 1, ?)''',
            ('admin', 'admin@ponyxpress.com', admin_password, 'admin', datetime.now())
        )
        conn.commit()
        conn.close()
        print("Database initialized with default admin user (admin/admin123)")
    
    app.run(debug=True, host='0.0.0.0', port=5000)