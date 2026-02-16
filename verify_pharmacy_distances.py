"""
Verify all pharmacies are within 5km of their city centers
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from webapp.models import Pharmacy
from math import radians, sin, cos, sqrt, atan2

# City coordinates
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
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

pharmacies = Pharmacy.objects.all()
over_5km = []
max_distance = 0
max_pharmacy = None

print("\n" + "="*80)
print("VERIFICATION: Checking all pharmacy distances")
print("="*80 + "\n")

for pharmacy in pharmacies:
    city = pharmacy.city if pharmacy.city in city_coordinates else 'Bhopal'
    base_lat, base_lon = city_coordinates.get(city, (23.2599, 77.4126))
    
    distance = calculate_distance(
        pharmacy.latitude, pharmacy.longitude,
        base_lat, base_lon
    )
    
    if distance > max_distance:
        max_distance = distance
        max_pharmacy = pharmacy
    
    if distance > 5:
        over_5km.append((pharmacy.name, pharmacy.city, distance))

print(f"✓ Total pharmacies checked: {pharmacies.count()}")
print(f"✓ Pharmacies over 5km: {len(over_5km)}")
print(f"✓ Maximum distance: {max_distance:.2f} km ({max_pharmacy.name}, {max_pharmacy.city})")

if over_5km:
    print("\n⚠ Pharmacies still over 5km:")
    for name, city, dist in over_5km:
        print(f"  - {name} ({city}): {dist:.2f} km")
else:
    print("\n🎉 ALL PHARMACIES ARE NOW UNDER 5KM! ✓")

print("="*80 + "\n")
