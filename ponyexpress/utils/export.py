"""
Export utilities for PonyXpress
CSV export functionality for delivery logs and other data.
"""

import csv
import io
from datetime import datetime, date
from flask import Response
from database.models import DeliveryLog, Package, Route, User

def export_delivery_logs_csv():
    """Export delivery logs to CSV"""
    # Create CSV data
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Date', 'Carrier', 'Packages Delivered', 'Route Distance (m)', 
        'Notes', 'Created At'
    ])
    
    # Get all delivery logs
    logs = DeliveryLog.get_all()
    
    # Write data rows
    for log in logs:
        # Get carrier username
        carrier = User.get_by_id(log.carrier_id)
        carrier_name = carrier.username if carrier else 'Unknown'
        
        writer.writerow([
            log.delivery_date,
            carrier_name,
            log.packages_delivered,
            log.route_distance or 0,
            log.notes or '',
            log.created_at
        ])
    
    # Create response
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=delivery_logs_{date.today()}.csv'}
    )

def export_packages_csv(start_date=None, end_date=None):
    """Export packages to CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Barcode', 'Package Type', 'Carrier', 'Location', 'Scanned At'
    ])
    
    # Get packages
    from database.models import Package
    packages = Package.get_all_in_date_range(start_date, end_date)
    
    # Write data rows
    for package in packages:
        carrier = User.get_by_id(package.carrier_id)
        carrier_name = carrier.username if carrier else 'Unknown'
        location = f"{package.latitude},{package.longitude}" if package.latitude and package.longitude else ''
        
        writer.writerow([
            package.barcode,
            package.package_type,
            carrier_name,
            location,
            package.scanned_at
        ])
    
    # Create response
    output.seek(0)
    filename = f"packages_{start_date or 'all'}_{end_date or 'all'}.csv"
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )

def export_routes_csv(start_date=None, end_date=None):
    """Export routes to CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Date', 'Carrier', 'Route Points', 'Created At', 'Updated At'
    ])
    
    # Get routes
    routes = Route.get_all_in_date_range(start_date, end_date)
    
    # Write data rows
    for route in routes:
        carrier = User.get_by_id(route.carrier_id)
        carrier_name = carrier.username if carrier else 'Unknown'
        route_points = len(route.route_data) if route.route_data else 0
        
        writer.writerow([
            route.route_date,
            carrier_name,
            route_points,
            route.created_at,
            route.updated_at
        ])
    
    # Create response
    output.seek(0)
    filename = f"routes_{start_date or 'all'}_{end_date or 'all'}.csv"
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )

def export_mailbox_stops_csv():
    """Export mailbox stops to CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Carrier', 'Latitude', 'Longitude', 'Photo Path', 'Created At'
    ])
    
    # Get mailbox stops
    from database.models import MailboxStop
    stops = MailboxStop.get_all()
    
    # Write data rows
    for stop in stops:
        carrier = User.get_by_id(stop.carrier_id)
        carrier_name = carrier.username if carrier else 'Unknown'
        
        writer.writerow([
            carrier_name,
            stop.latitude,
            stop.longitude,
            stop.photo_path or '',
            stop.created_at
        ])
    
    # Create response
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=mailbox_stops_{date.today()}.csv'}
    )

def generate_summary_report():
    """Generate a summary report as CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Metric', 'Value', 'Date'
    ])
    
    today = date.today()
    
    # Get statistics
    total_users = User.count_all()
    total_routes = Route.count_all()
    total_mailbox_stops = MailboxStop.count_all()
    today_deliveries = DeliveryLog.count_for_date(today)
    
    # Write data rows
    writer.writerow(['Total Users', total_users, today])
    writer.writerow(['Total Routes', total_routes, today])
    writer.writerow(['Total Mailbox Stops', total_mailbox_stops, today])
    writer.writerow(['Today\'s Deliveries', today_deliveries, today])
    
    # Create response
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=summary_report_{today}.csv'}
    )