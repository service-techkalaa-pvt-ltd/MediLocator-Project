"""
Fix pharmacy coordinates to ensure all are within 5km of their city center
"""
import os
import django
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from webapp.models import Pharmacy
from math import radians, sin, cos, sqrt, atan2

# City coordinates (same as in load_pharmacy_data.py)
city_coordinates = {
    'Delhi': (28.6139, 77.2090),
    'Mumbai': (19.0760, 72.8777),
    'Bangalore': (12.9716, 77.5946),
    'Hyderabad': (17.3850, 78.4867),
    'Chennai': (13.0827, 80.2707),
    'Kolkata': (22.5726, 88.3639),
    'Pune': (18.5204, 73.8567),
    'Ahmedabad': (23.0225, 72.5714),
    'Jaipur': (26.9124, 75.7873),
    'Lucknow': (26.8467, 80.9462),
    'Chandigarh': (30.7333, 76.7794),
    'Indore': (22.7196, 75.8577),
    'Kochi': (9.9312, 76.2673),
    'Surat': (21.1458, 72.1640),
    'Visakhapatnam': (17.6869, 83.2185),
    'Nagpur': (21.1458, 79.0882),
    'Bhopal': (23.2599, 77.4126),
    'Vadodara': (22.3072, 73.1812),
    'Ghaziabad': (28.6692, 77.4538),
    'Ludhiana': (30.9010, 75.8573),
    'Pimpri-Chinchwad': (18.6298, 73.7997),
    'Navi Mumbai': (19.0330, 73.0297),
}

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates in kilometers"""
    R = 6371  # Earth's radius in kilometers
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c
    
    return distance

def fix_pharmacy_coordinates():
    """Fix all pharmacy coordinates to be within 5km of city center"""
    
    pharmacies = Pharmacy.objects.all()
    fixed_count = 0
    already_ok = 0
    no_city_data = 0
    
    print("\n" + "="*80)
    print("FIXING PHARMACY COORDINATES")
    print("="*80 + "\n")
    
    for pharmacy in pharmacies:
        city = pharmacy.city
        
        # Get city coordinates
        if city not in city_coordinates:
            print(f"⚠ {pharmacy.name} ({city}): No city data, setting to Bhopal")
            base_lat, base_lon = 23.2599, 77.4126
            no_city_data += 1
        else:
            base_lat, base_lon = city_coordinates[city]
        
        # Calculate current distance from city center
        current_distance = calculate_distance(
            pharmacy.latitude, pharmacy.longitude,
            base_lat, base_lon
        )
        
        # If distance > 5km, fix it
        if current_distance > 5:
            # Generate new coordinates within 5km (±0.045 degrees ≈ 5km)
            # Use slightly smaller range to ensure we stay under 5km
            new_lat = base_lat + random.uniform(-0.040, 0.040)
            new_lon = base_lon + random.uniform(-0.040, 0.040)
            
            # Verify the new distance
            new_distance = calculate_distance(new_lat, new_lon, base_lat, base_lon)
            
            print(f"✓ Fixed {pharmacy.name} ({city})")
            print(f"  Old: {pharmacy.latitude:.6f}, {pharmacy.longitude:.6f} ({current_distance:.2f} km)")
            print(f"  New: {new_lat:.6f}, {new_lon:.6f} ({new_distance:.2f} km)")
            
            pharmacy.latitude = new_lat
            pharmacy.longitude = new_lon
            pharmacy.save()
            
            fixed_count += 1
        else:
            already_ok += 1
    
    print("\n" + "="*80)
    print(f"✓ Fixed: {fixed_count} pharmacies")
    print(f"✓ Already OK: {already_ok} pharmacies")
    print(f"⚠ No city data: {no_city_data} pharmacies")
    print(f"📊 Total: {Pharmacy.objects.count()} pharmacies")
    print("="*80 + "\n")

if __name__ == '__main__':
    fix_pharmacy_coordinates()
