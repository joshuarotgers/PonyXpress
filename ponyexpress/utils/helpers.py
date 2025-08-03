"""
Utility helper functions for PonyXpress
File handling, photo uploads, and other common operations.
"""

import os
import uuid
from werkzeug.utils import secure_filename
from datetime import datetime

# Allowed file extensions for photos
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_photo(file):
    """Save uploaded photo with unique filename"""
    if file and allowed_file(file.filename):
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        extension = file.filename.rsplit('.', 1)[1].lower()
        filename = f"mailbox_{timestamp}_{unique_id}.{extension}"
        
        # Ensure upload directory exists
        upload_folder = 'static/uploads'
        os.makedirs(upload_folder, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        return filename
    return None

def get_file_size_mb(file_path):
    """Get file size in MB"""
    if os.path.exists(file_path):
        return os.path.getsize(file_path) / (1024 * 1024)
    return 0

def cleanup_old_photos(max_age_days=30):
    """Clean up old photo files"""
    upload_folder = 'static/uploads'
    if not os.path.exists(upload_folder):
        return
    
    current_time = datetime.now()
    for filename in os.listdir(upload_folder):
        file_path = os.path.join(upload_folder, filename)
        if os.path.isfile(file_path):
            file_time = datetime.fromtimestamp(os.path.getctime(file_path))
            age_days = (current_time - file_time).days
            
            if age_days > max_age_days:
                try:
                    os.remove(file_path)
                except OSError:
                    pass  # File might be in use

def format_distance(meters):
    """Format distance in human-readable format"""
    if meters < 1000:
        return f"{meters:.0f}m"
    else:
        return f"{meters/1000:.1f}km"

def format_duration(seconds):
    """Format duration in human-readable format"""
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.0f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"

def validate_gps_coordinates(lat, lng):
    """Validate GPS coordinates"""
    try:
        lat = float(lat)
        lng = float(lng)
        return -90 <= lat <= 90 and -180 <= lng <= 180
    except (ValueError, TypeError):
        return False

def parse_location_string(location_str):
    """Parse location string in format 'lat,lng'"""
    if not location_str:
        return None, None
    
    try:
        parts = location_str.split(',')
        if len(parts) == 2:
            lat = float(parts[0].strip())
            lng = float(parts[1].strip())
            if validate_gps_coordinates(lat, lng):
                return lat, lng
    except (ValueError, IndexError):
        pass
    
    return None, None

def calculate_distance(lat1, lng1, lat2, lng2):
    """Calculate distance between two GPS points using Haversine formula"""
    import math
    
    # Convert to radians
    lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Earth's radius in meters
    r = 6371000
    
    return c * r

def sanitize_filename(filename):
    """Sanitize filename for safe storage"""
    return secure_filename(filename)

def get_file_extension(filename):
    """Get file extension from filename"""
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    return ''

def is_image_file(filename):
    """Check if file is an image based on extension"""
    return get_file_extension(filename) in ALLOWED_EXTENSIONS