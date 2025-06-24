import json
import csv
import io
from datetime import datetime, timedelta
import random

# Create sample configuration and data files for PONYXPRESS

# 1. Sample configuration file
config_data = {
    "app": {
        "name": "PONYXPRESS",
        "version": "1.0.0",
        "build": "2025.06.23.001",
        "environment": "production"
    },
    "features": {
        "voice_assistant": True,
        "offline_maps": True,
        "barcode_scanning": True,
        "signature_capture": True,
        "photo_capture": True,
        "gps_tracking": True,
        "route_optimization": True,
        "cloud_sync": False,
        "ai_coaching": True,
        "dark_mode": True
    },
    "ai_assistant": {
        "model": "mistral-7b-instruct",
        "wake_word": "Hey AI",
        "language": "en-US",
        "voice_training": True,
        "offline_mode": True,
        "memory_enabled": True,
        "coaching_enabled": True
    },
    "hardware": {
        "camera_enabled": True,
        "microphone_enabled": True,
        "gps_enabled": True,
        "zebra_scanner": False,
        "bluetooth_printer": False
    },
    "sync": {
        "firebase_enabled": False,
        "sync_interval": 3600,
        "auto_backup": True,
        "data_retention_days": 90
    },
    "security": {
        "local_encryption": True,
        "biometric_auth": False,
        "session_timeout": 28800,
        "data_encryption_key": "local-device-key"
    },
    "ui": {
        "theme": "auto",
        "language": "en-US",
        "high_contrast": False,
        "large_text": False,
        "sound_effects": True
    },
    "delivery": {
        "photo_quality": "medium",
        "signature_timeout": 30,
        "auto_photo": True,
        "geo_fence_radius": 100,
        "delivery_confirmation_required": True
    }
}

# Save configuration file
with open('ponyxpress-config.json', 'w') as f:
    json.dump(config_data, f, indent=2)

print("✅ Created ponyxpress-config.json")

# 2. Sample routes data
routes_data = [
    {
        "route_id": "RT001",
        "route_name": "Downtown Commercial District",
        "carrier_name": "John Smith",
        "estimated_time": "6.5 hours",
        "total_stops": 45,
        "route_type": "business",
        "start_time": "08:00:00",
        "end_time": "16:30:00",
        "stops": [
            {
                "stop_id": 1,
                "address": "123 Main St, Suite 100, Downtown, NY 10001",
                "customer_name": "Acme Corporation",
                "packages": ["9405511206213100012345", "9405511206213100012346"],
                "delivery_type": "business",
                "time_window": "09:00-17:00",
                "estimated_duration": 5,
                "special_instructions": "Front desk delivery, signature required",
                "coordinates": {"lat": 40.7128, "lng": -74.0060}
            },
            {
                "stop_id": 2,
                "address": "456 Broadway Ave, Floor 3, Downtown, NY 10001",
                "customer_name": "Tech Solutions LLC",
                "packages": ["9405511206213100012347"],
                "delivery_type": "business",
                "time_window": "08:00-18:00",
                "estimated_duration": 3,
                "special_instructions": "Ring buzzer for suite 301",
                "coordinates": {"lat": 40.7589, "lng": -73.9851}
            }
        ]
    },
    {
        "route_id": "RT002", 
        "route_name": "Residential Suburbs East",
        "carrier_name": "Sarah Johnson",
        "estimated_time": "7.2 hours",
        "total_stops": 62,
        "route_type": "residential",
        "start_time": "08:30:00",
        "end_time": "17:00:00",
        "stops": [
            {
                "stop_id": 1,
                "address": "789 Oak Street, Suburb, NY 10002",
                "customer_name": "Miller Family",
                "packages": ["9405511206213100012348", "9405511206213100012349"],
                "delivery_type": "residential",
                "time_window": "09:00-19:00",
                "estimated_duration": 2,
                "special_instructions": "Leave at front door if no answer",
                "coordinates": {"lat": 40.6892, "lng": -74.0445}
            }
        ]
    }
]

# Save routes data
with open('sample-routes.json', 'w') as f:
    json.dump(routes_data, f, indent=2)

print("✅ Created sample-routes.json")

# 3. Sample packages data with tracking information
packages_data = []
tracking_prefixes = ["9405", "9205", "9305", "9505"]
package_types = ["Priority Mail", "First Class", "Priority Express", "Ground Advantage", "Media Mail"]
statuses = ["Pending", "Out for Delivery", "Delivered", "Attempted", "Hold for Pickup"]

for i in range(50):
    package = {
        "tracking_number": f"{random.choice(tracking_prefixes)}511206213100{str(i+12345).zfill(6)}",
        "package_type": random.choice(package_types),
        "weight": round(random.uniform(0.5, 25.0), 2),
        "dimensions": {
            "length": random.randint(6, 24),
            "width": random.randint(4, 18), 
            "height": random.randint(2, 12)
        },
        "status": random.choice(statuses),
        "destination": {
            "name": f"Customer {i+1}",
            "address": f"{random.randint(100, 9999)} {random.choice(['Main', 'Oak', 'Pine', 'Elm', 'Broadway'])} {random.choice(['St', 'Ave', 'Blvd', 'Dr', 'Ln'])}",
            "city": random.choice(["New York", "Brooklyn", "Queens", "Bronx", "Staten Island"]),
            "state": "NY",
            "zip": f"100{random.randint(10, 99)}"
        },
        "special_handling": random.choice([None, "Signature Required", "Adult Signature", "Hold for Pickup", "No Safe Drop"]),
        "created_date": (datetime.now() - timedelta(days=random.randint(0, 7))).isoformat(),
        "estimated_delivery": (datetime.now() + timedelta(days=random.randint(0, 3))).isoformat()
    }
    packages_data.append(package)

# Save packages data
with open('sample-packages.json', 'w') as f:
    json.dump(packages_data, f, indent=2)

print("✅ Created sample-packages.json")

# 4. Create sample delivery log CSV
delivery_log_data = []
for i in range(100):
    delivery = {
        "delivery_id": f"DEL{str(i+1000).zfill(6)}",
        "tracking_number": f"{random.choice(tracking_prefixes)}511206213100{str(i+12345).zfill(6)}",
        "carrier_name": random.choice(["John Smith", "Sarah Johnson", "Mike Williams", "Lisa Brown"]),
        "delivery_date": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d"),
        "delivery_time": f"{random.randint(8, 17):02d}:{random.randint(0, 59):02d}:00",
        "address": f"{random.randint(100, 9999)} {random.choice(['Main', 'Oak', 'Pine', 'Elm', 'Broadway'])} {random.choice(['St', 'Ave', 'Blvd', 'Dr', 'Ln'])}",
        "status": random.choice(["Delivered", "Attempted - No Answer", "Delivered to Neighbor", "Hold for Pickup"]),
        "signature": random.choice(["Electronic", "None", "Neighbor - J. Doe"]),
        "photo_taken": random.choice(["Yes", "No"]),
        "delivery_duration_minutes": random.randint(1, 8),
        "gps_lat": round(40.7128 + random.uniform(-0.1, 0.1), 6),
        "gps_lng": round(-74.0060 + random.uniform(-0.1, 0.1), 6),
        "weather": random.choice(["Clear", "Rain", "Snow", "Cloudy", "Overcast"]),
        "notes": random.choice(["", "Customer not home", "Left with doorman", "Safe location", "Business closed"])
    }
    delivery_log_data.append(delivery)

# Save delivery log as CSV
csv_buffer = io.StringIO()
if delivery_log_data:
    writer = csv.DictWriter(csv_buffer, fieldnames=delivery_log_data[0].keys())
    writer.writeheader()
    writer.writerows(delivery_log_data)

with open('delivery-log-sample.csv', 'w', newline='') as f:
    f.write(csv_buffer.getvalue())

print("✅ Created delivery-log-sample.csv")

# 5. Create roles and permissions configuration
roles_config = {
    "roles": {
        "carrier": {
            "name": "Mail Carrier",
            "description": "Regular postal carrier with delivery responsibilities",
            "permissions": [
                "scan_packages",
                "deliver_packages", 
                "navigate_routes",
                "view_assigned_routes",
                "capture_signatures",
                "take_photos",
                "use_voice_assistant",
                "access_offline_maps",
                "export_personal_data"
            ],
            "restrictions": [
                "cannot_edit_routes",
                "cannot_assign_routes",
                "cannot_view_other_carriers",
                "cannot_access_admin_dashboard"
            ]
        },
        "substitute": {
            "name": "Substitute Carrier", 
            "description": "Temporary carrier covering routes",
            "permissions": [
                "scan_packages",
                "deliver_packages",
                "navigate_routes", 
                "view_assigned_routes",
                "capture_signatures",
                "take_photos",
                "use_voice_assistant",
                "access_offline_maps",
                "clone_routes"
            ],
            "restrictions": [
                "cannot_edit_routes",
                "cannot_assign_routes", 
                "limited_historical_data",
                "cannot_access_admin_dashboard"
            ]
        },
        "supervisor": {
            "name": "Route Supervisor",
            "description": "Supervisor managing multiple carriers and routes",
            "permissions": [
                "scan_packages",
                "deliver_packages",
                "navigate_routes",
                "view_all_routes",
                "edit_routes",
                "assign_routes",
                "view_carrier_performance",
                "access_live_tracking",
                "export_team_data",
                "manage_substitutes"
            ],
            "restrictions": [
                "cannot_manage_system_settings",
                "cannot_add_new_carriers"
            ]
        },
        "admin": {
            "name": "System Administrator", 
            "description": "Full system access and management",
            "permissions": [
                "all_carrier_permissions",
                "all_supervisor_permissions",
                "manage_users",
                "system_configuration",
                "data_management",
                "security_settings",
                "integration_management",
                "audit_logs",
                "backup_restore"
            ],
            "restrictions": []
        }
    },
    "permission_groups": {
        "delivery": ["scan_packages", "deliver_packages", "capture_signatures", "take_photos"],
        "navigation": ["navigate_routes", "access_offline_maps", "gps_tracking"],
        "route_management": ["view_routes", "edit_routes", "assign_routes", "clone_routes"],
        "team_management": ["view_carriers", "manage_substitutes", "view_performance"],
        "data_access": ["export_data", "view_reports", "audit_logs"],
        "system": ["system_configuration", "user_management", "security_settings"]
    }
}

# Save roles configuration
with open('roles-permissions.json', 'w') as f:
    json.dump(roles_config, f, indent=2)

print("✅ Created roles-permissions.json")

# 6. Create voice commands configuration
voice_commands = {
    "wake_words": ["Hey AI", "Hey Pony", "Assistant"],
    "commands": {
        "navigation": {
            "start_route": ["start route", "begin delivery", "start my route"],
            "next_stop": ["next stop", "continue route", "next delivery"],
            "skip_stop": ["skip this stop", "skip delivery", "come back later"],
            "get_directions": ["get directions", "navigate to", "how do I get to"],
            "current_location": ["where am I", "current location", "my location"],
            "route_status": ["route status", "how much left", "time remaining"]
        },
        "delivery": {
            "scan_package": ["scan package", "scan barcode", "read code"],
            "delivered": ["delivered", "package delivered", "delivery complete"],
            "attempted": ["attempted delivery", "no answer", "customer not home"],
            "take_photo": ["take photo", "capture image", "photo proof"],
            "get_signature": ["get signature", "signature required", "sign here"]
        },
        "information": {
            "package_info": ["package info", "what's this package", "package details"],
            "customer_info": ["customer info", "who lives here", "customer details"],
            "address_lookup": ["find address", "where is", "lookup address"],
            "case_memory": ["case memory", "remember this", "save address"]
        },
        "system": {
            "help": ["help", "what can you do", "commands"],
            "settings": ["settings", "preferences", "options"],
            "logout": ["logout", "sign out", "end session"],
            "sync_data": ["sync data", "upload data", "backup now"]
        }
    },
    "responses": {
        "acknowledgment": ["Got it", "Understood", "On it", "Will do"],
        "completion": ["Done", "Complete", "Finished", "All set"],
        "error": ["Sorry, I didn't understand", "Please try again", "Could you repeat that?"],
        "help": ["I can help with navigation, deliveries, and information. What do you need?"]
    },
    "training_phrases": [
        "Hey AI, start my route",
        "Hey AI, next stop please", 
        "Hey AI, package delivered at front door",
        "Hey AI, where am I",
        "Hey AI, take a photo",
        "Hey AI, help me"
    ]
}

# Save voice commands configuration
with open('voice-commands.json', 'w') as f:
    json.dump(voice_commands, f, indent=2)

print("✅ Created voice-commands.json")

print("\n📁 Generated PONYXPRESS Configuration Files:")
print("   • ponyxpress-config.json - Main app configuration")
print("   • sample-routes.json - Sample delivery routes")
print("   • sample-packages.json - Sample package data")
print("   • delivery-log-sample.csv - Sample delivery history")
print("   • roles-permissions.json - Role-based access control")
print("   • voice-commands.json - Voice assistant configuration")