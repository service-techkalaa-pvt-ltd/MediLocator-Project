#!/usr/bin/env python
"""Test the actual API response"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

# Import after Django setup
from django.test import Client

client = Client()

print("\n" + "="*70)
print("TESTING ACTUAL API ENDPOINTS")
print("="*70)

# Test 1: search_pharmacies (Mode 1: Both)
print("\n1. TEST: /api/search-pharmacies/ (Both location + medicine)")
print("-"*70)
response = client.get('/api/search-pharmacies/', {
    'lat': '18.5204',
    'lon': '73.8567',
    'radius': '10',
    'medicine': 'Amlong',  # Use a common medicine
    'sort': 'distance'
})
data = json.loads(response.content)
print(f"Status: {response.status_code}")
print(f"Success: {data.get('success')}")
print(f"Total: {data.get('total')} pharmacies")
if data.get('pharmacies'):
    pharmacy = data['pharmacies'][0]
    print(f"\nFirst pharmacy:")
    print(f"  Name: {pharmacy['name']}")
    print(f"  Distance: {pharmacy['distance']}km")
    print(f"  Rating: ⭐{pharmacy['rating']}")
    print(f"  Medicine available: {pharmacy['medicine_available']}")
    print(f"  Available medicines: {len(pharmacy['available_medicines'])} items")
    if pharmacy['available_medicines']:
        med = pharmacy['available_medicines'][0]
        print(f"    - {med['name']}: {med['quantity']} units @ ₹{med['price']}")

# Test 2: search_all_pharmacies (Mode 2: Location only)
print("\n\n2. TEST: /api/all-pharmacies/ (Location only)")
print("-"*70)
response = client.get('/api/all-pharmacies/', {
    'lat': '18.5204',
    'lon': '73.8567',
    'radius': '10',
    'sort': 'distance'
})
data = json.loads(response.content)
print(f"Status: {response.status_code}")
print(f"Success: {data.get('success')}")
print(f"Total: {data.get('total')} pharmacies")
if data.get('pharmacies'):
    pharmacy = data['pharmacies'][0]
    print(f"\nFirst pharmacy:")
    print(f"  Name: {pharmacy['name']}")
    print(f"  Distance: {pharmacy['distance']}km")
    print(f"  Rating: ⭐{pharmacy['rating']}")

# Test 3: search_medicines (Mode 3: Medicine only)
print("\n\n3. TEST: /api/search-medicines/ (Medicine only, nationwide)")
print("-"*70)
response = client.get('/api/search-medicines/', {
    'medicine': 'Amlong',
    'sort': 'distance'
})
data = json.loads(response.content)
print(f"Status: {response.status_code}")
print(f"Success: {data.get('success')}")
print(f"Total: {data.get('total')} pharmacies")
if data.get('pharmacies'):
    pharmacy = data['pharmacies'][0]
    print(f"\nFirst pharmacy:")
    print(f"  Name: {pharmacy['name']}")
    print(f"  City: {pharmacy['city']}")
    print(f"  Rating: ⭐{pharmacy['rating']}")

print("\n" + "="*70 + "\n")
