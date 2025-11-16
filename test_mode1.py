#!/usr/bin/env python
"""Test Mode 1: Both location + medicine search"""
import os
import django
import json
import math

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from webapp.models import Pharmacy, Inventory, Medicine

print("\n" + "="*70)
print("TEST MODE 1: BOTH SEARCH (Location + Medicine)")
print("="*70)

# Simulate: Search for Paracetamol near Pune (18.5204, 73.8567) within 10km
lat, lon, radius = 18.5204, 73.8567, 10
medicine_name = "paracetamol"

print(f"\nSearching for '{medicine_name}' near Pune ({lat}°, {lon}°) within {radius}km")
print("-"*70)

# Find pharmacies in radius
nearby = []
for p in Pharmacy.objects.all():
    dlat = math.radians(p.latitude - lat)
    dlon = math.radians(p.longitude - lon)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat)) * math.cos(math.radians(p.latitude)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = 6371 * c
    if distance <= radius:
        nearby.append((p, distance))

nearby.sort(key=lambda x: x[1])
print(f"✓ Found {len(nearby)} pharmacies in {radius}km radius")

# Check which have the medicine
results = []
for pharm, dist in nearby:
    inventory = Inventory.objects.filter(
        pharmacy=pharm,
        medicine__name__icontains=medicine_name,
        quantity__gt=0
    ).select_related('medicine')
    
    medicines = []
    for inv in inventory:
        medicines.append({
            'name': inv.medicine.name,
            'quantity': inv.quantity,
            'price': float(inv.price)
        })
    
    result = {
        'id': pharm.id,
        'name': pharm.name,
        'address': pharm.address,
        'city': pharm.city,
        'phone': pharm.phone,
        'latitude': pharm.latitude,
        'longitude': pharm.longitude,
        'rating': pharm.rating,
        'distance': round(dist, 2),
        'medicine_available': len(medicines) > 0,
        'available_medicines': medicines,
    }
    results.append(result)

print(f"\n✓ Results: {len(results)} pharmacies have '{medicine_name}'")
print("-"*70)

for i, pharm in enumerate(results[:10], 1):
    med_str = "✓ HAS" if pharm['medicine_available'] else "✗ NONE"
    print(f"\n{i}. {pharm['name']}")
    print(f"   📍 {pharm['address']}, {pharm['city']}")
    print(f"   📞 {pharm['phone']}")
    print(f"   ⭐ {pharm['rating']} | 📏 {pharm['distance']}km | {med_str}")
    if pharm['available_medicines']:
        for med in pharm['available_medicines'][:3]:
            print(f"      💊 {med['name']} - ₹{med['price']} ({med['quantity']} units)")

print("\n" + "="*70)
print(f"RESULT: Mode 1 returns {len(results)} pharmacies with {medicine_name}")
print("="*70 + "\n")
