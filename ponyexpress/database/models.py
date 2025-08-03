"""
Database models for PonyXpress
SQLite ORM classes for all entities in the delivery management system.
"""

import sqlite3
from datetime import datetime, date
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os

def get_db():
    """Get database connection"""
    db = sqlite3.connect('ponyxpress.db')
    db.row_factory = sqlite3.Row
    return db

def init_db():
    """Initialize database with tables"""
    db = get_db()
    
    # Create tables
    db.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK (role IN ('admin', 'carrier', 'substitute')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS routes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            carrier_id INTEGER NOT NULL,
            route_date DATE NOT NULL,
            route_data TEXT,  -- JSON string of route coordinates
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (carrier_id) REFERENCES users (id),
            UNIQUE(carrier_id, route_date)
        );
        
        CREATE TABLE IF NOT EXISTS mailbox_stops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            carrier_id INTEGER NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            photo_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (carrier_id) REFERENCES users (id)
        );
        
        CREATE TABLE IF NOT EXISTS packages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode TEXT NOT NULL,
            package_type TEXT NOT NULL CHECK (package_type IN ('big', 'small')),
            carrier_id INTEGER NOT NULL,
            latitude REAL,
            longitude REAL,
            scanned_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (carrier_id) REFERENCES users (id)
        );
        
        CREATE TABLE IF NOT EXISTS delivery_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            carrier_id INTEGER NOT NULL,
            route_id INTEGER,
            packages_delivered INTEGER DEFAULT 0,
            route_distance REAL,
            delivery_date DATE NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (carrier_id) REFERENCES users (id),
            FOREIGN KEY (route_id) REFERENCES routes (id)
        );
    ''')
    
    # Create default admin user if not exists
    admin = User.get_by_username('admin')
    if not admin:
        User.create('admin', 'admin123', 'admin')
    
    db.commit()
    db.close()

class User(UserMixin):
    """User model with Flask-Login integration"""
    
    def __init__(self, id, username, password_hash, role, created_at):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.created_at = created_at
    
    @staticmethod
    def create(username, password, role):
        """Create a new user"""
        db = get_db()
        try:
            password_hash = generate_password_hash(password)
            cursor = db.execute(
                'INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
                (username, password_hash, role)
            )
            db.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
        finally:
            db.close()
    
    @staticmethod
    def get_by_id(user_id):
        """Get user by ID"""
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE id = ?', (user_id,)
        ).fetchone()
        db.close()
        
        if user:
            return User(user['id'], user['username'], user['password_hash'], 
                      user['role'], user['created_at'])
        return None
    
    @staticmethod
    def get_by_username(username):
        """Get user by username"""
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()
        db.close()
        
        if user:
            return User(user['id'], user['username'], user['password_hash'], 
                      user['role'], user['created_at'])
        return None
    
    @staticmethod
    def authenticate(username, password):
        """Authenticate user with username and password"""
        user = User.get_by_username(username)
        if user and check_password_hash(user.password_hash, password):
            return user
        return None
    
    @staticmethod
    def get_all():
        """Get all users"""
        db = get_db()
        users = db.execute('SELECT * FROM users ORDER BY created_at DESC').fetchall()
        db.close()
        
        return [User(u['id'], u['username'], u['password_hash'], 
                    u['role'], u['created_at']) for u in users]
    
    @staticmethod
    def count_all():
        """Count all users"""
        db = get_db()
        count = db.execute('SELECT COUNT(*) FROM users').fetchone()[0]
        db.close()
        return count

class Route:
    """Route model for daily delivery routes"""
    
    def __init__(self, id, carrier_id, route_date, route_data, created_at, updated_at):
        self.id = id
        self.carrier_id = carrier_id
        self.route_date = route_date
        self.route_data = route_data
        self.created_at = created_at
        self.updated_at = updated_at
    
    @staticmethod
    def create(carrier_id, route_date, route_data):
        """Create a new route"""
        db = get_db()
        route_json = json.dumps(route_data) if route_data else None
        
        cursor = db.execute(
            '''INSERT INTO routes (carrier_id, route_date, route_data) 
               VALUES (?, ?, ?)''',
            (carrier_id, route_date, route_json)
        )
        db.commit()
        db.close()
        return cursor.lastrowid
    
    def update_trace(self, route_data):
        """Update route trace data"""
        db = get_db()
        route_json = json.dumps(route_data) if route_data else None
        
        db.execute(
            '''UPDATE routes SET route_data = ?, updated_at = CURRENT_TIMESTAMP 
               WHERE id = ?''',
            (route_json, self.id)
        )
        db.commit()
        db.close()
    
    @staticmethod
    def get_by_carrier_and_date(carrier_id, route_date):
        """Get route by carrier and date"""
        db = get_db()
        route = db.execute(
            'SELECT * FROM routes WHERE carrier_id = ? AND route_date = ?',
            (carrier_id, route_date)
        ).fetchone()
        db.close()
        
        if route:
            route_data = json.loads(route['route_data']) if route['route_data'] else None
            return Route(route['id'], route['carrier_id'], route['route_date'],
                       route_data, route['created_at'], route['updated_at'])
        return None
    
    @staticmethod
    def get_all_for_date(route_date):
        """Get all routes for a specific date"""
        db = get_db()
        routes = db.execute(
            'SELECT * FROM routes WHERE route_date = ?',
            (route_date,)
        ).fetchall()
        db.close()
        
        result = []
        for route in routes:
            route_data = json.loads(route['route_data']) if route['route_data'] else None
            result.append(Route(route['id'], route['carrier_id'], route['route_date'],
                              route_data, route['created_at'], route['updated_at']))
        return result
    
    @staticmethod
    def get_all():
        """Get all routes"""
        db = get_db()
        routes = db.execute('SELECT * FROM routes ORDER BY route_date DESC').fetchall()
        db.close()
        
        result = []
        for route in routes:
            route_data = json.loads(route['route_data']) if route['route_data'] else None
            result.append(Route(route['id'], route['carrier_id'], route['route_date'],
                              route_data, route['created_at'], route['updated_at']))
        return result
    
    @staticmethod
    def count_all():
        """Count all routes"""
        db = get_db()
        count = db.execute('SELECT COUNT(*) FROM routes').fetchone()[0]
        db.close()
        return count
    
    def to_dict(self):
        """Convert route to dictionary"""
        return {
            'id': self.id,
            'carrier_id': self.carrier_id,
            'route_date': str(self.route_date),
            'route_data': self.route_data,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

class MailboxStop:
    """Mailbox stop model for GPS coordinates and photos"""
    
    def __init__(self, id, carrier_id, latitude, longitude, photo_path, created_at, updated_at):
        self.id = id
        self.carrier_id = carrier_id
        self.latitude = latitude
        self.longitude = longitude
        self.photo_path = photo_path
        self.created_at = created_at
        self.updated_at = updated_at
    
    @staticmethod
    def create_or_update(carrier_id, location, photo_path=None):
        """Create or update mailbox stop"""
        if not location:
            return None
        
        # Parse location (expecting "lat,lng" format)
        try:
            lat, lng = map(float, location.split(','))
        except (ValueError, AttributeError):
            return None
        
        db = get_db()
        
        # Check if stop exists at this location
        existing = db.execute(
            '''SELECT * FROM mailbox_stops 
               WHERE carrier_id = ? AND latitude = ? AND longitude = ?''',
            (carrier_id, lat, lng)
        ).fetchone()
        
        if existing:
            # Update existing stop
            db.execute(
                '''UPDATE mailbox_stops 
                   SET photo_path = COALESCE(?, photo_path), updated_at = CURRENT_TIMESTAMP 
                   WHERE id = ?''',
                (photo_path, existing['id'])
            )
            db.commit()
            db.close()
            return existing['id']
        else:
            # Create new stop
            cursor = db.execute(
                '''INSERT INTO mailbox_stops (carrier_id, latitude, longitude, photo_path) 
                   VALUES (?, ?, ?, ?)''',
                (carrier_id, lat, lng, photo_path)
            )
            db.commit()
            db.close()
            return cursor.lastrowid
    
    @staticmethod
    def get_by_carrier(carrier_id):
        """Get mailbox stops by carrier"""
        db = get_db()
        stops = db.execute(
            'SELECT * FROM mailbox_stops WHERE carrier_id = ? ORDER BY created_at DESC',
            (carrier_id,)
        ).fetchall()
        db.close()
        
        return [MailboxStop(s['id'], s['carrier_id'], s['latitude'], s['longitude'],
                           s['photo_path'], s['created_at'], s['updated_at']) for s in stops]
    
    @staticmethod
    def get_all():
        """Get all mailbox stops"""
        db = get_db()
        stops = db.execute('SELECT * FROM mailbox_stops ORDER BY created_at DESC').fetchall()
        db.close()
        
        return [MailboxStop(s['id'], s['carrier_id'], s['latitude'], s['longitude'],
                           s['photo_path'], s['created_at'], s['updated_at']) for s in stops]
    
    @staticmethod
    def count_all():
        """Count all mailbox stops"""
        db = get_db()
        count = db.execute('SELECT COUNT(*) FROM mailbox_stops').fetchone()[0]
        db.close()
        return count
    
    def to_dict(self):
        """Convert mailbox stop to dictionary"""
        return {
            'id': self.id,
            'carrier_id': self.carrier_id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'photo_path': self.photo_path,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

class Package:
    """Package model for scanned packages"""
    
    def __init__(self, id, barcode, package_type, carrier_id, latitude, longitude, scanned_at, created_at):
        self.id = id
        self.barcode = barcode
        self.package_type = package_type
        self.carrier_id = carrier_id
        self.latitude = latitude
        self.longitude = longitude
        self.scanned_at = scanned_at
        self.created_at = created_at
    
    @staticmethod
    def create(barcode, package_type, carrier_id, location, scanned_at):
        """Create a new package record"""
        lat = lng = None
        if location:
            try:
                lat, lng = map(float, location.split(','))
            except (ValueError, AttributeError):
                pass
        
        db = get_db()
        cursor = db.execute(
            '''INSERT INTO packages (barcode, package_type, carrier_id, latitude, longitude, scanned_at) 
               VALUES (?, ?, ?, ?, ?, ?)''',
            (barcode, package_type, carrier_id, lat, lng, scanned_at)
        )
        db.commit()
        db.close()
        return cursor.lastrowid
    
    @staticmethod
    def get_by_carrier(carrier_id, date=None):
        """Get packages by carrier and optionally by date"""
        db = get_db()
        if date:
            packages = db.execute(
                '''SELECT * FROM packages 
                   WHERE carrier_id = ? AND DATE(scanned_at) = ? 
                   ORDER BY scanned_at DESC''',
                (carrier_id, date)
            ).fetchall()
        else:
            packages = db.execute(
                'SELECT * FROM packages WHERE carrier_id = ? ORDER BY scanned_at DESC',
                (carrier_id,)
            ).fetchall()
        db.close()
        
        return [Package(p['id'], p['barcode'], p['package_type'], p['carrier_id'],
                       p['latitude'], p['longitude'], p['scanned_at'], p['created_at']) 
                for p in packages]

class DeliveryLog:
    """Delivery log model for tracking daily deliveries"""
    
    def __init__(self, id, carrier_id, route_id, packages_delivered, route_distance, 
                 delivery_date, notes, created_at):
        self.id = id
        self.carrier_id = carrier_id
        self.route_id = route_id
        self.packages_delivered = packages_delivered
        self.route_distance = route_distance
        self.delivery_date = delivery_date
        self.notes = notes
        self.created_at = created_at
    
    @staticmethod
    def create(carrier_id, route_id, packages_delivered, route_distance, delivery_date, notes=None):
        """Create a new delivery log"""
        db = get_db()
        cursor = db.execute(
            '''INSERT INTO delivery_logs 
               (carrier_id, route_id, packages_delivered, route_distance, delivery_date, notes) 
               VALUES (?, ?, ?, ?, ?, ?)''',
            (carrier_id, route_id, packages_delivered, route_distance, delivery_date, notes)
        )
        db.commit()
        db.close()
        return cursor.lastrowid
    
    @staticmethod
    def get_all():
        """Get all delivery logs"""
        db = get_db()
        logs = db.execute('SELECT * FROM delivery_logs ORDER BY delivery_date DESC').fetchall()
        db.close()
        
        return [DeliveryLog(l['id'], l['carrier_id'], l['route_id'], l['packages_delivered'],
                           l['route_distance'], l['delivery_date'], l['notes'], l['created_at']) 
                for l in logs]
    
    @staticmethod
    def count_for_date(delivery_date):
        """Count delivery logs for a specific date"""
        db = get_db()
        count = db.execute(
            'SELECT COUNT(*) FROM delivery_logs WHERE delivery_date = ?',
            (delivery_date,)
        ).fetchone()[0]
        db.close()
        return count