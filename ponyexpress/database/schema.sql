-- PonyXpress Database Schema
-- SQLite database structure for rural delivery route management

-- Users table for authentication and role management
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('carrier', 'substitute', 'admin')),
    active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Routes table for storing daily route traces
CREATE TABLE IF NOT EXISTS routes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name VARCHAR(200) NOT NULL,
    route_data TEXT, -- JSON data containing GeoJSON route information
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'completed')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Deliveries table for package delivery records
CREATE TABLE IF NOT EXISTS deliveries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    barcode VARCHAR(255) NOT NULL,
    delivery_type VARCHAR(20) NOT NULL CHECK (delivery_type IN ('house', 'mailbox')),
    latitude REAL,
    longitude REAL,
    photo VARCHAR(255), -- Filename of attached photo
    notes TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'delivered' CHECK (status IN ('delivered', 'attempted', 'returned')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Mailbox stops table for semi-permanent mailbox locations
CREATE TABLE IF NOT EXISTS mailbox_stops (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    delivery_id INTEGER, -- Reference to the delivery that created this stop
    address TEXT,
    notes TEXT,
    photo VARCHAR(255), -- Filename of mailbox photo
    is_permanent BOOLEAN NOT NULL DEFAULT 0, -- Whether this is a permanent mailbox location
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (delivery_id) REFERENCES deliveries (id) ON DELETE SET NULL
);

-- Route assignments table for substitute access
CREATE TABLE IF NOT EXISTS route_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    route_id INTEGER NOT NULL,
    substitute_user_id INTEGER NOT NULL,
    assigned_by INTEGER NOT NULL, -- Admin user who made the assignment
    assigned_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    FOREIGN KEY (route_id) REFERENCES routes (id) ON DELETE CASCADE,
    FOREIGN KEY (substitute_user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_by) REFERENCES users (id) ON DELETE CASCADE
);

-- Delivery logs table for detailed tracking and audit trail
CREATE TABLE IF NOT EXISTS delivery_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    delivery_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    action VARCHAR(50) NOT NULL, -- 'scanned', 'delivered', 'attempted', 'photo_added', etc.
    details TEXT, -- JSON data with additional information
    latitude REAL,
    longitude REAL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (delivery_id) REFERENCES deliveries (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- User sessions table for tracking active sessions
CREATE TABLE IF NOT EXISTS user_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_routes_user_id ON routes(user_id);
CREATE INDEX IF NOT EXISTS idx_routes_status ON routes(status);
CREATE INDEX IF NOT EXISTS idx_routes_created_at ON routes(created_at);
CREATE INDEX IF NOT EXISTS idx_deliveries_user_id ON deliveries(user_id);
CREATE INDEX IF NOT EXISTS idx_deliveries_barcode ON deliveries(barcode);
CREATE INDEX IF NOT EXISTS idx_deliveries_created_at ON deliveries(created_at);
CREATE INDEX IF NOT EXISTS idx_mailbox_stops_user_id ON mailbox_stops(user_id);
CREATE INDEX IF NOT EXISTS idx_mailbox_stops_location ON mailbox_stops(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_delivery_logs_delivery_id ON delivery_logs(delivery_id);
CREATE INDEX IF NOT EXISTS idx_delivery_logs_user_id ON delivery_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(session_token);

-- Triggers for automatic timestamp updates
CREATE TRIGGER IF NOT EXISTS update_users_timestamp 
    AFTER UPDATE ON users 
    BEGIN 
        UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; 
    END;

CREATE TRIGGER IF NOT EXISTS update_routes_timestamp 
    AFTER UPDATE ON routes 
    BEGIN 
        UPDATE routes SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; 
    END;

CREATE TRIGGER IF NOT EXISTS update_mailbox_stops_timestamp 
    AFTER UPDATE ON mailbox_stops 
    BEGIN 
        UPDATE mailbox_stops SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; 
    END;

-- Create delivery log entry when a delivery is created
CREATE TRIGGER IF NOT EXISTS log_delivery_creation
    AFTER INSERT ON deliveries
    BEGIN
        INSERT INTO delivery_logs (delivery_id, user_id, action, details, latitude, longitude)
        VALUES (NEW.id, NEW.user_id, 'created', 
                json_object('barcode', NEW.barcode, 'delivery_type', NEW.delivery_type),
                NEW.latitude, NEW.longitude);
    END;

-- Create delivery log entry when a delivery is updated
CREATE TRIGGER IF NOT EXISTS log_delivery_update
    AFTER UPDATE ON deliveries
    BEGIN
        INSERT INTO delivery_logs (delivery_id, user_id, action, details)
        VALUES (NEW.id, NEW.user_id, 'updated',
                json_object('old_status', OLD.status, 'new_status', NEW.status));
    END;