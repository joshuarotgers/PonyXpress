#!/usr/bin/env python3
"""
PonyXpress - Rural Delivery Route Management System
Main Flask application with authentication, routes, and core functionality.
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
import json
from datetime import datetime, date
import uuid
from database.models import init_db, User, Route, MailboxStop, DeliveryLog, Package
from utils.helpers import allowed_file, save_photo

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'ponyxpress-secret-key-change-in-production'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    return User.get_by_id(user_id)

# Database initialization
def get_db():
    """Get database connection"""
    db = sqlite3.connect('ponyxpress.db')
    db.row_factory = sqlite3.Row
    return db

@app.before_first_request
def setup_database():
    """Initialize database on first request"""
    init_db()

# Authentication routes
@app.route('/')
def index():
    """Home page - redirect to login if not authenticated"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page with form handling"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.authenticate(username, password)
        if user:
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

# Main dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard based on user role"""
    if current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif current_user.role == 'carrier':
        return redirect(url_for('carrier_dashboard'))
    else:  # substitute
        return redirect(url_for('substitute_dashboard'))

# Carrier routes
@app.route('/carrier')
@login_required
def carrier_dashboard():
    """Carrier dashboard with route management and scanning"""
    if current_user.role != 'carrier':
        flash('Access denied. Carrier role required.', 'error')
        return redirect(url_for('dashboard'))
    
    # Get today's route
    today = date.today()
    route = Route.get_by_carrier_and_date(current_user.id, today)
    
    return render_template('carrier/dashboard.html', route=route)

@app.route('/carrier/route')
@login_required
def carrier_route():
    """Interactive route map for carriers"""
    if current_user.role != 'carrier':
        flash('Access denied. Carrier role required.', 'error')
        return redirect(url_for('dashboard'))
    
    # Get existing route and mailbox stops
    today = date.today()
    route = Route.get_by_carrier_and_date(current_user.id, today)
    mailbox_stops = MailboxStop.get_by_carrier(current_user.id)
    
    return render_template('carrier/route.html', route=route, mailbox_stops=mailbox_stops)

@app.route('/api/route/save', methods=['POST'])
@login_required
def save_route():
    """Save route trace from map"""
    if current_user.role != 'carrier':
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    route_data = data.get('route')
    today = date.today()
    
    # Save or update route
    route = Route.get_by_carrier_and_date(current_user.id, today)
    if route:
        route.update_trace(route_data)
    else:
        Route.create(current_user.id, today, route_data)
    
    return jsonify({'success': True})

@app.route('/carrier/scan')
@login_required
def carrier_scan():
    """Package scanning interface"""
    if current_user.role != 'carrier':
        flash('Access denied. Carrier role required.', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('carrier/scan.html')

@app.route('/api/package/scan', methods=['POST'])
@login_required
def scan_package():
    """Handle package scanning"""
    if current_user.role != 'carrier':
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    barcode = data.get('barcode')
    package_type = data.get('package_type')  # 'big' or 'small'
    location = data.get('location')  # GPS coordinates
    
    # Create package record
    package = Package.create(
        barcode=barcode,
        package_type=package_type,
        carrier_id=current_user.id,
        location=location,
        scanned_at=datetime.now()
    )
    
    # If small package, create mailbox stop
    if package_type == 'small' and location:
        MailboxStop.create_or_update(
            carrier_id=current_user.id,
            location=location,
            photo_path=None  # Will be added later if photo taken
        )
    
    return jsonify({
        'success': True,
        'package_id': package.id,
        'message': f'Package {barcode} scanned successfully'
    })

@app.route('/api/mailbox/photo', methods=['POST'])
@login_required
def upload_mailbox_photo():
    """Upload photo for mailbox stop"""
    if current_user.role != 'carrier':
        return jsonify({'error': 'Access denied'}), 403
    
    if 'photo' not in request.files:
        return jsonify({'error': 'No photo provided'}), 400
    
    file = request.files['photo']
    location = request.form.get('location')
    
    if file and allowed_file(file.filename):
        filename = save_photo(file)
        
        # Update mailbox stop with photo
        MailboxStop.create_or_update(
            carrier_id=current_user.id,
            location=location,
            photo_path=filename
        )
        
        return jsonify({'success': True, 'filename': filename})
    
    return jsonify({'error': 'Invalid file'}), 400

# Substitute routes
@app.route('/substitute')
@login_required
def substitute_dashboard():
    """Substitute dashboard - view only"""
    if current_user.role != 'substitute':
        flash('Access denied. Substitute role required.', 'error')
        return redirect(url_for('dashboard'))
    
    # Get today's routes and mailbox stops
    today = date.today()
    routes = Route.get_all_for_date(today)
    mailbox_stops = MailboxStop.get_all()
    
    return render_template('substitute/dashboard.html', routes=routes, mailbox_stops=mailbox_stops)

@app.route('/substitute/route')
@login_required
def substitute_route():
    """View route map (read-only)"""
    if current_user.role != 'substitute':
        flash('Access denied. Substitute role required.', 'error')
        return redirect(url_for('dashboard'))
    
    today = date.today()
    routes = Route.get_all_for_date(today)
    mailbox_stops = MailboxStop.get_all()
    
    return render_template('substitute/route.html', routes=routes, mailbox_stops=mailbox_stops)

# Admin routes
@app.route('/admin')
@login_required
def admin_dashboard():
    """Admin dashboard with management tools"""
    if current_user.role != 'admin':
        flash('Access denied. Admin role required.', 'error')
        return redirect(url_for('dashboard'))
    
    # Get statistics
    total_users = User.count_all()
    total_routes = Route.count_all()
    total_mailbox_stops = MailboxStop.count_all()
    today_deliveries = DeliveryLog.count_for_date(date.today())
    
    return render_template('admin/dashboard.html', 
                         total_users=total_users,
                         total_routes=total_routes,
                         total_mailbox_stops=total_mailbox_stops,
                         today_deliveries=today_deliveries)

@app.route('/admin/users')
@login_required
def admin_users():
    """Manage users"""
    if current_user.role != 'admin':
        flash('Access denied. Admin role required.', 'error')
        return redirect(url_for('dashboard'))
    
    users = User.get_all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/users/add', methods=['GET', 'POST'])
@login_required
def admin_add_user():
    """Add new user"""
    if current_user.role != 'admin':
        flash('Access denied. Admin role required.', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        
        if User.create(username, password, role):
            flash('User created successfully', 'success')
            return redirect(url_for('admin_users'))
        else:
            flash('Username already exists', 'error')
    
    return render_template('admin/add_user.html')

@app.route('/admin/routes')
@login_required
def admin_routes():
    """View all routes"""
    if current_user.role != 'admin':
        flash('Access denied. Admin role required.', 'error')
        return redirect(url_for('dashboard'))
    
    routes = Route.get_all()
    return render_template('admin/routes.html', routes=routes)

@app.route('/admin/mailbox-stops')
@login_required
def admin_mailbox_stops():
    """View all mailbox stops"""
    if current_user.role != 'admin':
        flash('Access denied. Admin role required.', 'error')
        return redirect(url_for('dashboard'))
    
    mailbox_stops = MailboxStop.get_all()
    return render_template('admin/mailbox_stops.html', mailbox_stops=mailbox_stops)

@app.route('/admin/delivery-logs')
@login_required
def admin_delivery_logs():
    """View delivery logs"""
    if current_user.role != 'admin':
        flash('Access denied. Admin role required.', 'error')
        return redirect(url_for('dashboard'))
    
    logs = DeliveryLog.get_all()
    return render_template('admin/delivery_logs.html', logs=logs)

@app.route('/admin/export/csv')
@login_required
def admin_export_csv():
    """Export delivery logs to CSV"""
    if current_user.role != 'admin':
        flash('Access denied. Admin role required.', 'error')
        return redirect(url_for('dashboard'))
    
    from utils.export import export_delivery_logs_csv
    return export_delivery_logs_csv()

# API routes for data
@app.route('/api/routes/<date>')
@login_required
def api_routes_by_date(date):
    """Get routes for a specific date"""
    try:
        route_date = datetime.strptime(date, '%Y-%m-%d').date()
        routes = Route.get_all_for_date(route_date)
        return jsonify([route.to_dict() for route in routes])
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400

@app.route('/api/mailbox-stops')
@login_required
def api_mailbox_stops():
    """Get all mailbox stops"""
    stops = MailboxStop.get_all()
    return jsonify([stop.to_dict() for stop in stops])

# PWA manifest and service worker
@app.route('/manifest.json')
def manifest():
    """PWA manifest file"""
    return app.send_static_file('manifest.json')

@app.route('/sw.js')
def service_worker():
    """Service worker for offline support"""
    return app.send_static_file('sw.js')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)